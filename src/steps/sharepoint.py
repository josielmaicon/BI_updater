import requests
from pathlib import Path
import msal
import time
from core.step_result import StepResult
from config.settings import SHAREPOINT
from utils.logger import logger


GRAPH_SCOPE = ["https://graph.microsoft.com/.default"]
GRAPH_URL = "https://graph.microsoft.com/v1.0"


def _get_access_token() -> str:
    app = msal.ConfidentialClientApplication(
        SHAREPOINT["client_id"],
        authority=f"https://login.microsoftonline.com/{SHAREPOINT['tenant_id']}",
        client_credential=SHAREPOINT["client_secret"]
    )

    token_response = app.acquire_token_for_client(scopes=GRAPH_SCOPE)

    if "access_token" not in token_response:
        raise RuntimeError(
            f"Erro ao obter token: {token_response}"
        )

    return token_response["access_token"]

CHUNK_SIZE = 5 * 1024 * 1024

def upload_sharepoint(file_path: str, sharepoint_path: str, access_token: str, site_id: str) -> StepResult:
    path = Path(file_path)
    if not path.exists():
        return StepResult(success=False, message=f"Arquivo não encontrado: {file_path}")

    try:
        logger.info(f"Iniciando upload de arquivo grande para SharePoint: {path.name}")
        
        # 1️⃣ Criar a sessão de upload
        url_session = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{sharepoint_path}/{path.name}:/createUploadSession"
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {"item": {"@microsoft.graph.conflictBehavior": "replace"}}
        resp = requests.post(url_session, headers=headers, json=data)
        resp.raise_for_status()
        upload_url = resp.json()["uploadUrl"]
        logger.debug(f"Upload URL: {upload_url}")

        # 2️⃣ Enviar em chunks
        file_size = path.stat().st_size
        with open(path, "rb") as f:
            start = 0
            while start < file_size:
                end = min(start + CHUNK_SIZE - 1, file_size - 1)
                chunk_data = f.read(end - start + 1)

                chunk_headers = {
                    "Content-Range": f"bytes {start}-{end}/{file_size}"
                }
                r = requests.put(upload_url, headers=chunk_headers, data=chunk_data)
                if r.status_code not in (200, 201, 202):
                    logger.error(f"Erro no chunk {start}-{end}: {r.status_code} {r.text}")
                    return StepResult(success=False, message=f"Erro no upload: {r.status_code} {r.text}")

                start = end + 1

        logger.info("Upload concluído com sucesso")
        return StepResult(success=True, message="Arquivo enviado para o SharePoint", data={"filename": path.name})

    except Exception as e:
        logger.exception("Exceção durante upload")
        return StepResult(success=False, message=str(e))