# steps/powerbi_updater.py
import requests
import msal
from core.step_result import StepResult
from config.settings import POWER_BI, SHAREPOINT

# --- Configurações MSAL ---
AUTHORITY = f"https://login.microsoftonline.com/{SHAREPOINT['tenant_id']}"
SCOPE = ["https://analysis.windows.net/powerbi/api/.default"]

def _get_powerbi_token() -> str:
    """Obtém token de acesso para Power BI usando Client Credentials."""
    app = msal.ConfidentialClientApplication(
        client_id=SHAREPOINT["client_id"],
        authority=AUTHORITY,
        client_credential=SHAREPOINT["client_secret"]
    )

    token_response = app.acquire_token_for_client(scopes=SCOPE)

    if "access_token" not in token_response:
        raise RuntimeError(f"Erro ao obter token Power BI: {token_response}")

    return token_response["access_token"]

def atualizar_dataset(token: str, group_id: str, dataset_id: str) -> StepResult:
    """Dispara refresh de um dataset específico."""
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/datasets/{dataset_id}/refreshes"
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
            message=f"Erro ao disparar refresh do dataset {dataset_id}: {str(e)}"
        )

    return StepResult(
        success=True,
        message=f"Refresh disparado para dataset {dataset_id}",
        data={"dataset_id": dataset_id}
    )

def atualizar_todos_datasets() -> list[StepResult]:
    """Atualiza todos os datasets configurados no POWER_BI de uma só vez."""
    results = []
    try:
        token = _get_powerbi_token()
    except Exception as e:
        # Se não pegar token, todos falham
        for key, dataset_id in POWER_BI["datasets"].items():
            results.append(StepResult(
                success=False,
                message=f"Não foi possível obter token para dataset {key}: {str(e)}"
            ))
        return results

    group_id = POWER_BI["workspace_id"]
    for key, dataset_id in POWER_BI["datasets"].items():
        result = atualizar_dataset(token, group_id, dataset_id)
        results.append(result)

    return results