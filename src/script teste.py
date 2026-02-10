import requests
from utils.logger import logger
from steps.sharepoint import _get_access_token

destinatario="josiel.maicon@translogtransportes.com.br"

def enviar_email(token: str, assunto: str, corpo: str, remetente: str, destinatario: str):
    url = f"https://graph.microsoft.com/v1.0/users/{remetente}/sendMail"

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


    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    resp = requests.post(url, json=payload, headers=headers)

    if not resp.ok:
        logger.error(f"Falha ao enviar e-mail: {resp.status_code} {resp.text}")
        resp.raise_for_status()

    logger.info("E-mail enviado com sucesso.")

token = _get_access_token()

enviar_email(
    token,
    "Teste pipeline",
    "Se chegou, o envio funciona.",
    remetente="planejamento@translogtransportes.com.br",
    destinatario="josielmaicon.a@gmail.com"
)
