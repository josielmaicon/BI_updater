import zipfile
import gzip
import shutil
import os
from pathlib import Path
from core.step_result import StepResult
from utils.logger import logger

def extrair_zip(
    zip_path: str | Path,
    tipo_exportacao: str,
    data_exportacao: str
) -> StepResult:

    zip_path = Path(zip_path)

    if not zip_path.exists():
        return StepResult(
            success=False,
            message=f"Arquivo ZIP não encontrado: {zip_path}"
        )

    extract_dir = zip_path.parent
    arquivos_finais = []

    try:
        if zip_path.suffix.lower() == ".zip":
            # ZIP normal
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                for member in zip_ref.namelist():
                    if not member.lower().endswith(".csv"):
                        continue

                    zip_ref.extract(member, extract_dir)
                    original = extract_dir / member
                    novo_nome = f"{tipo_exportacao}_{data_exportacao}.csv"
                    destino = extract_dir / novo_nome

                    if destino.exists():
                        destino.unlink()

                    original.rename(destino)
                    arquivos_finais.append(str(destino))

        elif zip_path.suffix.lower() == ".gz":
            # GZIP
            destino = extract_dir / f"{tipo_exportacao}_{data_exportacao}.csv"
            with gzip.open(zip_path, "rb") as f_in:
                with open(destino, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            arquivos_finais.append(str(destino))

        else:
            return StepResult(
                success=False,
                message=f"Formato não suportado: {zip_path.suffix}"
            )

        # Remove o arquivo original depois de extrair
        zip_path.unlink()

    except zipfile.BadZipFile:
        logger.debug(f"ZIP Path: {zip_path}, Size: {os.path.getsize(zip_path)}")
        return StepResult(
            success=False,
            message="Arquivo ZIP inválido ou corrompido",
        )
    except Exception as e:
        return StepResult(
            success=False,
            message=f"Erro ao extrair arquivo: {e}"
        )

    if not arquivos_finais:
        return StepResult(
            success=False,
            message="Nenhum CSV encontrado no arquivo"
        )

    return StepResult(
        success=True,
        message="CSVs extraídos e renomeados com sucesso",
        data={
            "csv_files": arquivos_finais
        }
    )
