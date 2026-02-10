import requests
from utils.logger import logger
from config.settings import EMAIL_REMETENTE

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


def enviar_email(
    access_token: str,
    assunto: str,
    corpo: str,
    destinatario: str
):
    url = f"{GRAPH_BASE_URL}/users/{EMAIL_REMETENTE}/sendMail"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "message": {
            "subject": assunto,
            "body": {
                "contentType": "Text",
                "content": corpo
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": destinatario
                    }
                }
            ]
        },
        "saveToSentItems": True
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("📧 E-mail de notificação enviado com sucesso")

    except Exception as e:
        # ⚠️ regra de ouro: notificação NUNCA quebra pipeline
        logger.error(f"Falha ao enviar e-mail: {e}")
