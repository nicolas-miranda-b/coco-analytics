"""Cliente de WhatsApp Cloud API (Meta).

Sin WHATSAPP_TOKEN configurado (desarrollo/tests), los envíos se simulan y
quedan en el log — así el MVP se puede probar de punta a punta sin credenciales.
"""

import logging
from dataclasses import dataclass

import httpx

from .config import config

logger = logging.getLogger("tatareceta.whatsapp")

URL_GRAPH = "https://graph.facebook.com/v19.0"


@dataclass
class MensajeEntrante:
    telefono: str
    texto: str
    nombre: str = ""


def verificar_webhook(modo: str, token: str, desafio: str) -> str | None:
    """Verificación GET que exige Meta al registrar el webhook."""
    if modo == "subscribe" and token == config.webhook_verify_token:
        return desafio
    return None


def extraer_mensajes(payload: dict) -> list[MensajeEntrante]:
    """Extrae los mensajes de texto de un evento del webhook de WhatsApp."""
    mensajes: list[MensajeEntrante] = []
    for entrada in payload.get("entry", []):
        for cambio in entrada.get("changes", []):
            valor = cambio.get("value", {})
            contactos = {
                c.get("wa_id"): c.get("profile", {}).get("name", "")
                for c in valor.get("contacts", [])
            }
            for mensaje in valor.get("messages", []):
                if mensaje.get("type") != "text":
                    continue  # imágenes de recetas: etapa posterior del roadmap
                telefono = mensaje.get("from", "")
                mensajes.append(
                    MensajeEntrante(
                        telefono=telefono,
                        texto=mensaje.get("text", {}).get("body", ""),
                        nombre=contactos.get(telefono, ""),
                    )
                )
    return mensajes


def enviar_mensaje(telefono: str, texto: str) -> dict:
    if not config.whatsapp_token or not config.whatsapp_numero_id:
        logger.info("[simulado] → %s: %s", telefono, texto)
        return {"simulado": True, "telefono": telefono}

    respuesta = httpx.post(
        f"{URL_GRAPH}/{config.whatsapp_numero_id}/messages",
        headers={"Authorization": f"Bearer {config.whatsapp_token}"},
        json={
            "messaging_product": "whatsapp",
            "to": telefono,
            "type": "text",
            "text": {"body": texto},
        },
        timeout=15,
    )
    respuesta.raise_for_status()
    return respuesta.json()
