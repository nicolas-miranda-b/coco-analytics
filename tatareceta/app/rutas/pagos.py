"""Rutas de pagos: notificación del banco, imagen del QR y verificación manual."""

import base64
import logging
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import whatsapp
from ..config import config
from ..db import obtener_sesion
from ..modelos import Pago, Usuario
from ..pagos import obtener_proveedor

logger = logging.getLogger("tatareceta.rutas.pagos")

router = APIRouter(prefix="/pagos", tags=["pagos"])

MENSAJE_CONFIRMACION = (
    "✅ ¡Pago recibido! Tu suscripción TataReceta está activa hasta el *{hasta}*.\n"
    "Envíame el nombre de un medicamento o la foto de tu receta cuando quieras. 💊"
)


def _extraer_qr_id(payload: dict) -> str:
    """El banco puede nombrar el campo de varias formas (qrId, QRId, id...)."""
    for clave in ("qrId", "QRId", "qr_id", "qrID", "id", "QrId"):
        valor = payload.get(clave)
        if valor:
            return str(valor)
    # A veces viene anidado: {"data": {...}} o {"qr": {...}}
    for clave in ("data", "qr", "payment"):
        anidado = payload.get(clave)
        if isinstance(anidado, dict):
            encontrado = _extraer_qr_id(anidado)
            if encontrado:
                return encontrado
    return ""


def marcar_pagado(sesion: Session, pago: Pago) -> Usuario:
    """Marca el pago, extiende la suscripción y avisa por WhatsApp."""
    pago.estado = "pagado"
    pago.pagado_en = datetime.now(timezone.utc)
    usuario = sesion.get(Usuario, pago.usuario_id)
    base = usuario.suscrito_hasta if usuario.suscripcion_activa() else date.today()
    usuario.suscrito_hasta = base + timedelta(days=pago.dias)
    sesion.commit()
    whatsapp.enviar_mensaje(
        usuario.telefono,
        MENSAJE_CONFIRMACION.format(hasta=usuario.suscrito_hasta.strftime("%d/%m/%Y")),
    )
    return usuario


@router.post("/notificacion")
async def notificacion_banco(
    request: Request,
    sesion: Session = Depends(obtener_sesion),
    x_webhook_secret: str = Header(""),
):
    """Webhook que el banco llama cuando alguien paga el QR."""
    if config.pagos_webhook_secret and x_webhook_secret != config.pagos_webhook_secret:
        raise HTTPException(status_code=401, detail="Secreto de webhook inválido")

    payload = await request.json()
    qr_id = _extraer_qr_id(payload if isinstance(payload, dict) else {})
    if not qr_id:
        raise HTTPException(status_code=422, detail="No se encontró el qrId en la notificación")

    pago = sesion.scalar(select(Pago).where(Pago.qr_id == qr_id))
    if pago is None:
        # Se responde 200 para que el banco no reintente eternamente,
        # pero queda registrado para investigar.
        logger.warning("Notificación de pago para QR desconocido: %s", qr_id)
        return {"success": True, "detalle": "QR no registrado"}

    if pago.estado == "pagado":
        return {"success": True, "detalle": "Ya estaba pagado"}

    marcar_pagado(sesion, pago)
    return {"success": True}


@router.get("/{qr_id}/qr.png")
def imagen_qr(qr_id: str, sesion: Session = Depends(obtener_sesion)):
    """Sirve la imagen del QR (WhatsApp la adjunta desde este link)."""
    pago = sesion.scalar(select(Pago).where(Pago.qr_id == qr_id))
    if pago is None or not pago.imagen_qr:
        raise HTTPException(status_code=404, detail="QR no encontrado")
    return Response(content=base64.b64decode(pago.imagen_qr), media_type="image/png")


@router.post("/{qr_id}/verificar")
def verificar_pago(qr_id: str, sesion: Session = Depends(obtener_sesion)):
    """Consulta el estado al proveedor (respaldo por si el webhook no llegó)."""
    pago = sesion.scalar(select(Pago).where(Pago.qr_id == qr_id))
    if pago is None:
        raise HTTPException(status_code=404, detail="QR no encontrado")
    if pago.estado == "pagado":
        return {"estado": "pagado"}

    estado = obtener_proveedor().consultar_estado(qr_id)
    if estado == "pagado":
        marcar_pagado(sesion, pago)
    elif estado in ("expirado", "error"):
        pago.estado = estado
        sesion.commit()
    return {"estado": pago.estado if estado == "pendiente" else estado}
