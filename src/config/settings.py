from pathlib import Path
import tempfile
import os

BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE_DIR / "workdir"
TEMP_DIR.mkdir(exist_ok=True)

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
    "workspace_id": "SEU_WORKSPACE_ID_AQUI",

    "datasets": {
        "bi_documentos": "DATASET_ID_DOCUMENTOS",
        "bi_paradas": "DATASET_ID_PARADAS",
        "bi_rotas": "DATASET_ID_ROTAS"
    }
}