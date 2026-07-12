"""Webhook de WhatsApp: recibe mensajes, aplica la cuota gratuita y responde."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import whatsapp
from ..config import config
from ..db import obtener_sesion
from ..modelos import Consulta, Usuario
from ..motor.equivalencias import responder_consulta

router = APIRouter(tags=["webhook"])

MENSAJE_SUSCRIPCION = (
    "🙌 Ya usaste tus {gratis} consultas gratuitas.\n\n"
    "Por solo *Bs {precio:g} al mes* tienes consultas ilimitadas: "
    "responde *QUIERO SUSCRIBIRME* y te enviamos el QR de pago."
)


@router.get("/webhook")
def verificar(
    modo: str = Query("", alias="hub.mode"),
    token: str = Query("", alias="hub.verify_token"),
    desafio: str = Query("", alias="hub.challenge"),
):
    respuesta = whatsapp.verificar_webhook(modo, token, desafio)
    if respuesta is None:
        raise HTTPException(status_code=403, detail="Token de verificación inválido")
    return PlainTextResponse(respuesta)


def _obtener_o_crear_usuario(sesion: Session, telefono: str, nombre: str) -> Usuario:
    usuario = sesion.scalar(select(Usuario).where(Usuario.telefono == telefono))
    if usuario is None:
        usuario = Usuario(telefono=telefono, nombre=nombre)
        sesion.add(usuario)
        sesion.flush()
    elif nombre and not usuario.nombre:
        usuario.nombre = nombre
    return usuario


def _procesar_mensaje(sesion: Session, mensaje: whatsapp.MensajeEntrante) -> str:
    usuario = _obtener_o_crear_usuario(sesion, mensaje.telefono, mensaje.nombre)

    usadas = sesion.scalar(
        select(func.count(Consulta.id)).where(Consulta.usuario_id == usuario.id)
    ) or 0
    if not usuario.suscripcion_activa() and usadas >= config.consultas_gratis:
        respuesta = MENSAJE_SUSCRIPCION.format(
            gratis=config.consultas_gratis, precio=config.precio_suscripcion_bs
        )
        exitosa = False
    else:
        resultado = responder_consulta(sesion, mensaje.texto)
        respuesta = resultado.mensaje
        exitosa = resultado.encontrado

    sesion.add(
        Consulta(
            usuario_id=usuario.id,
            texto=mensaje.texto,
            respuesta=respuesta,
            exitosa=exitosa,
        )
    )
    sesion.commit()
    return respuesta


@router.post("/webhook")
async def recibir(request: Request, sesion: Session = Depends(obtener_sesion)):
    payload = await request.json()
    procesados = 0
    for mensaje in whatsapp.extraer_mensajes(payload):
        respuesta = _procesar_mensaje(sesion, mensaje)
        whatsapp.enviar_mensaje(mensaje.telefono, respuesta)
        procesados += 1
    return {"procesados": procesados}
