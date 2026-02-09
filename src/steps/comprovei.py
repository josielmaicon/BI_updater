import requests
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth

from core.step_result import StepResult
from config.mappings import COMPROVEI_EXPORTS


USERNAME = "translog"
PASSWORD = "admin"


def solicitar_exportacao(tipo_exportacao: str, data_exportacao: datetime) -> StepResult:
    if tipo_exportacao not in COMPROVEI_EXPORTS:
        return StepResult(
            success=False,
            message=f"Tipo de exportação inválido: {tipo_exportacao}"
        )

    config = COMPROVEI_EXPORTS[tipo_exportacao]
    url = config["url"]

    payload = {
        "formato_exportacao": "csv",
        "filtros": {
            "data_inicial": data_exportacao.strftime("%Y-%m-%d"),
            "data_final": data_exportacao.strftime("%Y-%m-%d")
        }
    }

    try:
        response = requests.post(
            url=url,
            json=payload,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            timeout=980
        )
        response.raise_for_status()
        data = response.json()

    except requests.RequestException as e:
        return StepResult(
            success=False,
            message=f"Erro de comunicação com Comprovei: {str(e)}"
        )

    if "user_message" not in data:
        return StepResult(
            success=False,
            message=data.get("message", "Erro desconhecido na exportação"),
            data=data
        )

    return StepResult(
        success=True,
        message="Exportação disponível",
        data={
            "tipo": tipo_exportacao,
            "data_exportacao": data_exportacao.strftime("%Y%m%d"),
            "download_url": data["user_message"]
        }
    )
