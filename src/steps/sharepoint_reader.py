import re
import requests
from datetime import date
from config.settings import SHAREPOINT
from utils.logger import logger
from steps.sharepoint import _get_access_token

GRAPH_URL = "https://graph.microsoft.com/v1.0"

DATE_REGEX = re.compile(r"(\d{4}-\d{2}-\d{2})")  # YYYY-MM-DD


def get_last_processed_date(sharepoint_path: str) -> date | None:
    token = _get_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    site_id = SHAREPOINT["site_id"]
    atual_path = sharepoint_path
    historico_path = sharepoint_path.replace("/Atual", "/Histórico")

    list_url = (
        f"{GRAPH_URL}/sites/{site_id}"
        f"/drive/root:/{atual_path}:/children"
    )

    logger.debug(f"Consultando SharePoint (Atual): {atual_path}")
    r = requests.get(list_url, headers=headers)
    r.raise_for_status()

    hoje = date.today()
    datas_validas = []

    for item in r.json().get("value", []):
        nome = item["name"]
        item_id = item["id"]

        m = DATE_REGEX.search(nome)
        if not m:
            logger.debug(f"Ignorando arquivo sem data: {nome}")
            continue

        try:
            data_arquivo = date.fromisoformat(m.group(1))
        except ValueError:
            logger.warning(f"Data inválida no nome do arquivo: {nome}")
            continue

        # 🔄 Se não for do mês atual → mover para Histórico
        if data_arquivo.year != hoje.year or data_arquivo.month != hoje.month:
            logger.info(
                f"Movendo para histórico: {nome} ({data_arquivo})"
            )

            move_url = (
                f"{GRAPH_URL}/sites/{site_id}"
                f"/drive/items/{item_id}"
            )

            payload = {
                "parentReference": {
                    "path": f"/drive/root:/{historico_path}"
                },
                "name": nome
            }

            mr = requests.patch(move_url, headers=headers, json=payload)
            mr.raise_for_status()
            continue

        # ✔️ Arquivo válido do mês atual
        datas_validas.append(data_arquivo)

    return max(datas_validas) if datas_validas else None
