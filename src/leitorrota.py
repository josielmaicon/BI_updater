from steps.sharepoint import _get_access_token
from config.settings import SHAREPOINT
import requests

GRAPH_URL = "https://graph.microsoft.com/v1.0"


def listar_todas_pastas():
    token = _get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{GRAPH_URL}/sites/{SHAREPOINT['site_id']}/drive/root:/Power BI/Base de Dados/Operacional/Rotas/Atual:/children"
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    for item in r.json().get("value", []):
        print(item["name"])

listar_todas_pastas()