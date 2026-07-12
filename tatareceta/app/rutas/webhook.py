"""Webhook de WhatsApp: recibe mensajes (texto o foto de receta), aplica la
cuota gratuita, maneja la suscripción por QR y responde."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import whatsapp
from ..config import config
from ..db import obtener_sesion
from ..modelos import Consulta, Pago, Usuario
from ..motor.equivalencias import responder_consulta
from ..motor.normalizacion import normalizar_texto
from ..motor.ocr import obtener_ocr
from ..pagos import obtener_proveedor

logger = logging.getLogger("tatareceta.webhook")

router = APIRouter(tags=["webhook"])

MENSAJE_SUSCRIPCION = (
    "🙌 Ya usaste tus {gratis} consultas gratuitas.\n\n"
    "Por solo *Bs {precio:g} al mes* tienes consultas ilimitadas: "
    "responde *QUIERO SUSCRIBIRME* y te envío el QR de pago."
)

MENSAJE_QR = (
    "¡Perfecto! 🎉 Escanea este QR con la app de tu banco para pagar tu "
    "suscripción de *Bs {precio:g}* (30 días de consultas ilimitadas).\n\n"
    "En cuanto el banco confirme el pago, tu suscripción se activa sola y "
    "te aviso por aquí. 🙌"
)

MENSAJE_OCR_NO_DISPONIBLE = (
    "📷 Recibí tu imagen, pero por ahora no puedo leer fotos en este "
    "ambiente. Escríbeme el nombre del medicamento (ej: *Amoxicilina 500 mg*) "
    "y te busco las opciones al instante."
)

MENSAJE_OCR_SIN_MEDICAMENTOS = (
    "📷 Miré tu imagen pero no pude identificar medicamentos legibles 😔. "
    "Prueba con una foto más nítida o escríbeme el nombre del medicamento."
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


def _quiere_suscribirse(texto: str) -> bool:
    return "suscri" in normalizar_texto(texto)


def _flujo_suscripcion(sesion: Session, usuario: Usuario) -> str:
    """Genera el QR de pago y lo envía; devuelve el texto de registro."""
    # Reusar un QR pendiente reciente en vez de generar uno por mensaje
    pendiente = sesion.scalar(
        select(Pago)
        .where(Pago.usuario_id == usuario.id, Pago.estado == "pendiente")
        .order_by(Pago.creado.desc())
    )
    if pendiente is None:
        proveedor = obtener_proveedor()
        qr = proveedor.generar_qr(
            monto_bs=config.precio_suscripcion_bs,
            glosa=f"Suscripción TataReceta {usuario.telefono}",
            referencia=f"TR-{usuario.id}",
        )
        pendiente = Pago(
            usuario_id=usuario.id,
            proveedor=proveedor.nombre,
            qr_id=qr.qr_id,
            monto_bs=config.precio_suscripcion_bs,
            glosa=f"Suscripción TataReceta {usuario.telefono}",
            imagen_qr=qr.imagen_base64,
        )
        sesion.add(pendiente)
        sesion.flush()

    leyenda = MENSAJE_QR.format(precio=pendiente.monto_bs)
    url_imagen = f"{config.base_url_publica.rstrip('/')}/pagos/{pendiente.qr_id}/qr.png"
    whatsapp.enviar_imagen(usuario.telefono, url_imagen, leyenda=leyenda)
    return f"📲 Te envié el QR de pago (imagen de arriba 👆). QR: {pendiente.qr_id}"


def _consultar_por_imagen(sesion: Session, mensaje: whatsapp.MensajeEntrante) -> tuple[str, bool]:
    """Descarga la foto, extrae los medicamentos con OCR y consulta cada uno."""
    ocr = obtener_ocr()
    if ocr is None:
        return MENSAJE_OCR_NO_DISPONIBLE, False

    descarga = whatsapp.descargar_media(mensaje.media_id)
    if descarga is None:  # sin credenciales de WhatsApp (desarrollo)
        return MENSAJE_OCR_NO_DISPONIBLE, False

    try:
        medicamentos = ocr.extraer_medicamentos(*descarga)
    except Exception:
        logger.exception("OCR falló para media %s", mensaje.media_id)
        return MENSAJE_OCR_SIN_MEDICAMENTOS, False

    if not medicamentos:
        return MENSAJE_OCR_SIN_MEDICAMENTOS, False

    respuestas, alguna_exitosa = [], False
    for linea in medicamentos[:3]:  # una receta rara vez trae más
        resultado = responder_consulta(sesion, linea)
        alguna_exitosa = alguna_exitosa or resultado.encontrado
        respuestas.append(resultado.mensaje)
    encabezado = f"📷 Leí tu receta y encontré {len(medicamentos)} medicamento(s):\n\n"
    return encabezado + "\n\n———\n\n".join(respuestas), alguna_exitosa


def _procesar_mensaje(sesion: Session, mensaje: whatsapp.MensajeEntrante) -> str:
    usuario = _obtener_o_crear_usuario(sesion, mensaje.telefono, mensaje.nombre)

    # 1) Intención de suscripción: siempre disponible (incluso sin cuota).
    if mensaje.tipo == "texto" and _quiere_suscribirse(mensaje.texto):
        respuesta = _flujo_suscripcion(sesion, usuario)
        exitosa = True
    else:
        # 2) Cuota gratuita para las consultas.
        usadas = sesion.scalar(
            select(func.count(Consulta.id)).where(Consulta.usuario_id == usuario.id)
        ) or 0
        if not usuario.suscripcion_activa() and usadas >= config.consultas_gratis:
            respuesta = MENSAJE_SUSCRIPCION.format(
                gratis=config.consultas_gratis, precio=config.precio_suscripcion_bs
            )
            exitosa = False
        elif mensaje.tipo == "imagen":
            respuesta, exitosa = _consultar_por_imagen(sesion, mensaje)
        else:
            resultado = responder_consulta(sesion, mensaje.texto)
            respuesta = resultado.mensaje
            exitosa = resultado.encontrado

    sesion.add(
        Consulta(
            usuario_id=usuario.id,
            texto=mensaje.texto if mensaje.tipo == "texto" else f"[imagen] {mensaje.texto}".strip(),
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
