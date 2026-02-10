from datetime import date, timedelta
from pathlib import Path
import shutil
import time
from typing import Callable

from core.pipeline import Pipeline
from core.context import ExecutionContext
from config.settings import TEMP_DIR, SHAREPOINT
from config.mappings import FILE_CLASSIFICATION_RULES

from steps.comprovei import solicitar_exportacao
from steps.downloader import baixar_arquivo
from steps.extractor import extrair_zip
from steps.classifier import classificar_arquivos
from steps.sharepoint import upload_sharepoint, _get_access_token
from steps.sharepoint_reader import get_last_processed_date
from utils.logger import logger
from notifications.email import enviar_email
from steps.powerbi import atualizar_todos_datasets

TIPOS = ["paradas", "documentos", "rotas"]
CHUNK_SIZE = 5 * 1024 * 1024  # 5MB
MAX_RETRIES = 3
RETRY_DELAY = 10  # segundos


def gerar_datas_faltantes(ultima_data: date) -> list[date]:
    hoje = date.today()
    datas = []
    atual = ultima_data + timedelta(days=1)
    while atual < hoje:
        datas.append(atual)
        atual += timedelta(days=1)
    return datas


def get_rule_by_tipo(tipo: str) -> dict:
    for rule in FILE_CLASSIFICATION_RULES:
        if rule["tipo"] == tipo:
            return rule
    raise ValueError(f"Regra não encontrada para tipo '{tipo}'")


def limpar_temp_dir():
    """Remove todos os arquivos e pastas do TEMP_DIR."""
    if TEMP_DIR.exists():
        for item in TEMP_DIR.iterdir():
            try:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            except Exception as e:
                logger.warning(f"Não foi possível remover {item}: {e}")


def run_with_retry(func: Callable, *args, max_retries: int = MAX_RETRIES, delay: int = RETRY_DELAY, **kwargs):
    """
    Tenta executar uma função até max_retries vezes.
    Retorna o resultado se sucesso, ou None se falhar todas as tentativas.
    """
    for attempt in range(1, max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt < max_retries:
                logger.warning(f"Tentativa {attempt} de {func.__name__} falhou: {e}. Retentando em {delay}s...")
                time.sleep(delay)
            else:
                logger.error(f"{func.__name__} falhou após {max_retries} tentativas: {e}")
                return None


def main():
    logger.info("Iniciando pipeline Comprovei → múltiplos tipos")
    errors = []

    access_token = _get_access_token()
    site_id = SHAREPOINT["site_id"]

    for tipo in TIPOS:
        logger.info(f"\n=== Pipeline para tipo: {tipo} ===")
        rule = get_rule_by_tipo(tipo)

        ultima_data = get_last_processed_date(sharepoint_path=rule["sharepoint_path"])
        if ultima_data is None:
            logger.warning("Nenhum arquivo encontrado. Iniciando do começo do mês.")
            ultima_data = date.today().replace(day=1) - timedelta(days=1)

        datas_faltantes = gerar_datas_faltantes(ultima_data)
        logger.info(f"Datas a processar para {tipo}: {datas_faltantes}")

        for data_exportacao in datas_faltantes:
            logger.info(f"--- Processando {tipo} {data_exportacao} ---")
            pipeline = Pipeline()
            ctx = ExecutionContext()
            ctx["data_exportacao"] = data_exportacao

            zip_path = None
            csv_path = None

            try:
                # Solicitar exportação
                r1 = run_with_retry(pipeline.run_step, solicitar_exportacao, rule["comprovei_tipo"], data_exportacao)
                if r1 is None:
                    raise RuntimeError("Falha na solicitação de exportação após retries")
                ctx.update(r1.data)

                # Download
                r2 = run_with_retry(pipeline.run_step, baixar_arquivo, ctx["download_url"], TEMP_DIR)
                if r2 is None:
                    raise RuntimeError("Falha no download após retries")
                zip_path = Path(r2.data["file_path"])

                # Extração + renomeação
                r3 = run_with_retry(pipeline.run_step, extrair_zip, zip_path, tipo, data_exportacao)
                if r3 is None:
                    raise RuntimeError("Falha na extração após retries")
                csv_path = Path(r3.data["csv_files"][0])

                # Limpar ZIP após extrair
                if zip_path.exists():
                    zip_path.unlink()
                    logger.debug(f"Arquivo ZIP removido: {zip_path.name}")

                # Classificação
                r4 = run_with_retry(pipeline.run_step, classificar_arquivos, csv_path)
                if r4 is None:
                    raise RuntimeError("Falha na classificação após retries")
                ctx.update(r4.data)

                #  Upload SharePoint
                r5 = run_with_retry(pipeline.run_step, upload_sharepoint, str(csv_path), rule["sharepoint_path"], access_token, site_id)
                if r5 is None:
                    raise RuntimeError("Falha no upload após retries")

                success, _ = pipeline.summary()
                logger.info(f"Finalizado {tipo} {data_exportacao} — sucesso={success}")

            except Exception as e:
                logger.error(f"Erro no processamento de {tipo} {data_exportacao}: {e}")
                errors.append({
                    "tipo": tipo,
                    "data": data_exportacao,
                    "error": str(e)
                })

            finally:
                # Limpar CSV mesmo se der erro
                try:
                    if zip_path:
                        zip_path.unlink()
                        logger.debug(f"Arquivo ZIP removido no finally: {zip_path.name}")
                except FileNotFoundError:
                    pass

                try:
                    if csv_path:
                        csv_path.unlink()
                        logger.debug(f"Arquivo CSV removido no finally: {csv_path.name}")
                except FileNotFoundError:
                    pass

        # Limpeza do TEMP_DIR ao final de cada tipo
        limpar_temp_dir()
        logger.debug(f"TEMP_DIR limpo após processar {tipo}")

    # --- Atualização dos datasets Power BI ---
    try:
        results = atualizar_todos_datasets()
        for r in results:
            if r.success:
                logger.debug(f"[OK] {r.data['dataset_id']} refresh iniciado")
            else:
                logger.error(f"[ERRO POWER BI] {r.message}")
                errors.append({
                    "tipo": "power_bi",
                    "data": None,
                    "error": r.message
                })
    except Exception as e:
        logger.exception("Erro inesperado ao atualizar datasets do Power BI")
        errors.append({
            "tipo": "power_bi",
            "data": None,
            "error": str(e)
        })


    # --- Resumo final + e-mail ---
    if errors:
        corpo = (
            "Erros detectados na pipeline Comprovei\n\n" +
            "\n".join(
                f"- Tipo: {e['tipo']}"
                + (f" | Data: {e['data']}" if e["data"] else "")
                + f"\n  Erro: {e['error']}"
                for e in errors
            )
        )

        enviar_email(
            access_token=access_token,
            assunto="Falha na pipeline Comprovei",
            corpo=corpo,
            destinatario="josiel.maicon@translogtransportes.com.br"
        )
    else:
        enviar_email(
            access_token=access_token,
            assunto="Atualização Monitorada - Indicadores Operacionais",
            corpo="Todos os tipos foram processados e os datasets do Power BI foram atualizados com sucesso.",
            destinatario="josiel.maicon@translogtransportes.com.br"
        )

    logger.info("Pipeline encerrado para todos os tipos.")



if __name__ == "__main__":
    main()
