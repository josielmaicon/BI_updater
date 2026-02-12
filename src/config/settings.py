from pathlib import Path
import tempfile
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")
TEMP_DIR = BASE_DIR / "workdir"
TEMP_DIR.mkdir(exist_ok=True)

EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
PROJECT_NAME = "Pipeline Comprovei"

SHAREPOINT = {
    "client_id": os.getenv("CLIENT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),
    "tenant_id": os.getenv("TENANT_ID"),
    "site_id": "translogtransportescombr.sharepoint.com,d18b9970-1888-4f58-8d3d-e237804c8546,6b32fc6f-e1a6-4adc-909c-a50b16bd5c14",
    "drive": "Documents"
}

POWER_BI = {
    "client_id": os.getenv("CLIENT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),
    "tenant_id": os.getenv("TENANT_ID"),
    "workspace_id": "bde55dfd-8938-41ba-a8fb-d852eab61ee0",

    "datasets": {
        "bi_documentos": "BI_DOCUMENTOS",
        "bi_paradas": "96bb3219-5b45-4be5-94d7-d392d19e5121",
        "bi_rotas": "5fcbf785-f997-465a-b061-2d518352130f"
    }
}