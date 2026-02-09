import requests
import msal

from core.step_result import StepResult
from config.settings import SHAREPOINT, POWER_BI


AUTHORITY = f"https://login.microsoftonline.com/{SHAREPOINT['tenant_id']}"
SCOPE = ["https://analysis.windows.net/powerbi/api/.default"]


def _get_powerbi_token() -> str:
    app = msal.ConfidentialClientApplication(
        SHAREPOINT["client_id"],
        authority=AUTHORITY,
        client_credential=SHAREPOINT["client_secret"]
    )

    token_response = app.acquire_token_for_client(scopes=SCOPE)

    if "access_token" not in token_response:
        raise RuntimeError(
            f"Erro ao obter token Power BI: {token_response}"
        )

    return token_response["access_token"]

def atualizar_powerbi(dataset_key: str) -> StepResult:
    if dataset_key not in POWER_BI["datasets"]:
        return StepResult(
            success=False,
            message=f"Dataset não configurado: {dataset_key}"
        )

    dataset_id = POWER_BI["datasets"][dataset_key]
    group_id = POWER_BI["group_id"]

    try:
        token = _get_powerbi_token()
    except Exception as e:
        return StepResult(
            success=False,
            message=str(e)
        )

    url = (
        f"https://api.powerbi.com/v1.0/myorg"
        f"/groups/{group_id}"
        f"/datasets/{dataset_id}/refreshes"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, timeout=30)
        response.raise_for_status()

    except requests.RequestException as e:
        return StepResult(
            success=False,
            message=f"Erro ao disparar refresh do Power BI: {str(e)}"
        )

    return StepResult(
        success=True,
        message="Refresh do Power BI disparado",
        data={
            "dataset_id": dataset_id
        }
    )
