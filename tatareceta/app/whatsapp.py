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
    tipo: str = "texto"  # texto | imagen
    media_id: str = ""  # id del adjunto en WhatsApp (si tipo == imagen)


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
                telefono = mensaje.get("from", "")
                tipo = mensaje.get("type")
                if tipo == "text":
                    mensajes.append(
                        MensajeEntrante(
                            telefono=telefono,
                            texto=mensaje.get("text", {}).get("body", ""),
                            nombre=contactos.get(telefono, ""),
                        )
                    )
                elif tipo == "image":
                    imagen = mensaje.get("image", {})
                    mensajes.append(
                        MensajeEntrante(
                            telefono=telefono,
                            texto=imagen.get("caption", ""),
                            nombre=contactos.get(telefono, ""),
                            tipo="imagen",
                            media_id=imagen.get("id", ""),
                        )
                    )
    return mensajes


def _enviar(telefono: str, contenido: dict, descripcion: str) -> dict:
    if not config.whatsapp_token or not config.whatsapp_numero_id:
        logger.info("[simulado] → %s: %s", telefono, descripcion)
        return {"simulado": True, "telefono": telefono}

    respuesta = httpx.post(
        f"{URL_GRAPH}/{config.whatsapp_numero_id}/messages",
        headers={"Authorization": f"Bearer {config.whatsapp_token}"},
        json={"messaging_product": "whatsapp", "to": telefono} | contenido,
        timeout=15,
    )
    respuesta.raise_for_status()
    return respuesta.json()


def enviar_mensaje(telefono: str, texto: str) -> dict:
    return _enviar(telefono, {"type": "text", "text": {"body": texto}}, texto)


def enviar_imagen(telefono: str, url: str, leyenda: str = "") -> dict:
    """Envía una imagen por link (p. ej. el QR de pago servido por nuestra API)."""
    return _enviar(
        telefono,
        {"type": "image", "image": {"link": url, "caption": leyenda}},
        f"[imagen] {url} — {leyenda}",
    )


def descargar_media(media_id: str) -> tuple[bytes, str] | None:
    """Descarga un adjunto de WhatsApp (dos pasos: metadatos → binario).

    Devuelve (bytes, tipo_mime) o None si no hay credenciales (desarrollo).
    """
    if not config.whatsapp_token:
        logger.info("[simulado] descarga de media %s omitida (sin token)", media_id)
        return None
    cabeceras = {"Authorization": f"Bearer {config.whatsapp_token}"}
    metadatos = httpx.get(f"{URL_GRAPH}/{media_id}", headers=cabeceras, timeout=15)
    metadatos.raise_for_status()
    datos = metadatos.json()
    binario = httpx.get(datos["url"], headers=cabeceras, timeout=30)
    binario.raise_for_status()
    return binario.content, datos.get("mime_type", "image/jpeg")
