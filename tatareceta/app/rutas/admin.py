"""Panel administrativo: catálogo, precios, usuarios y suscripciones (pago QR manual)."""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import esquemas
from ..config import config
from ..db import obtener_sesion
from ..modelos import Consulta, Farmacia, Medicamento, Pago, Precio, Usuario
from ..motor.normalizacion import normalizar_forma, normalizar_texto

router = APIRouter(prefix="/admin", tags=["admin"])


def exigir_admin(x_admin_token: str = Header("")) -> None:
    if x_admin_token != config.admin_token:
        raise HTTPException(status_code=401, detail="Token administrativo inválido")


@router.post("/medicamentos", response_model=esquemas.MedicamentoVer, dependencies=[Depends(exigir_admin)])
def crear_medicamento(datos: esquemas.MedicamentoCrear, sesion: Session = Depends(obtener_sesion)):
    medicamento = Medicamento(
        **datos.model_dump()
        | {
            "principio_activo": normalizar_texto(datos.principio_activo),
            "forma": normalizar_forma(datos.forma) or normalizar_texto(datos.forma),
        }
    )
    sesion.add(medicamento)
    sesion.commit()
    return medicamento


@router.get("/medicamentos", response_model=list[esquemas.MedicamentoVer], dependencies=[Depends(exigir_admin)])
def listar_medicamentos(sesion: Session = Depends(obtener_sesion)):
    return list(sesion.scalars(select(Medicamento)))


@router.post("/farmacias", response_model=esquemas.FarmaciaVer, dependencies=[Depends(exigir_admin)])
def crear_farmacia(datos: esquemas.FarmaciaCrear, sesion: Session = Depends(obtener_sesion)):
    farmacia = Farmacia(**datos.model_dump())
    sesion.add(farmacia)
    sesion.commit()
    return farmacia


@router.post("/precios", response_model=esquemas.PrecioVer, dependencies=[Depends(exigir_admin)])
def crear_precio(datos: esquemas.PrecioCrear, sesion: Session = Depends(obtener_sesion)):
    if sesion.get(Medicamento, datos.medicamento_id) is None:
        raise HTTPException(status_code=404, detail="Medicamento no encontrado")
    if sesion.get(Farmacia, datos.farmacia_id) is None:
        raise HTTPException(status_code=404, detail="Farmacia no encontrada")
    precio = sesion.scalar(
        select(Precio).where(
            Precio.medicamento_id == datos.medicamento_id,
            Precio.farmacia_id == datos.farmacia_id,
        )
    )
    if precio:  # actualización de precio existente
        precio.precio_bs = datos.precio_bs
        precio.unidad_venta = datos.unidad_venta
    else:
        precio = Precio(**datos.model_dump())
        sesion.add(precio)
    sesion.commit()
    return precio


@router.get("/consultas", response_model=list[esquemas.ConsultaVer], dependencies=[Depends(exigir_admin)])
def listar_consultas(sesion: Session = Depends(obtener_sesion)):
    return list(sesion.scalars(select(Consulta).order_by(Consulta.creado.desc())))


@router.get("/usuarios", response_model=list[esquemas.UsuarioVer], dependencies=[Depends(exigir_admin)])
def listar_usuarios(sesion: Session = Depends(obtener_sesion)):
    return list(sesion.scalars(select(Usuario)))


@router.get("/pagos", response_model=list[esquemas.PagoVer], dependencies=[Depends(exigir_admin)])
def listar_pagos(sesion: Session = Depends(obtener_sesion)):
    return list(sesion.scalars(select(Pago).order_by(Pago.creado.desc())))


@router.post(
    "/suscripciones/{telefono}/activar",
    response_model=esquemas.UsuarioVer,
    dependencies=[Depends(exigir_admin)],
)
def activar_suscripcion(
    telefono: str, dias: int = 30, sesion: Session = Depends(obtener_sesion)
):
    """Registra manualmente un pago por QR confirmado (flujo del MVP manual)."""
    usuario = sesion.scalar(select(Usuario).where(Usuario.telefono == telefono))
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    base = usuario.suscrito_hasta if usuario.suscripcion_activa() else date.today()
    usuario.suscrito_hasta = base + timedelta(days=dias)
    sesion.commit()
    return usuario
