"""Esquemas Pydantic para el panel administrativo."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class MedicamentoCrear(BaseModel):
    nombre_comercial: str
    principio_activo: str
    concentracion_valor: float
    concentracion_unidad: str = "mg"
    forma: str = "comprimido"
    laboratorio: str = ""
    registro_sanitario: str = ""
    es_generico: bool = False


class MedicamentoVer(MedicamentoCrear):
    model_config = ConfigDict(from_attributes=True)
    id: int


class FarmaciaCrear(BaseModel):
    nombre: str
    cadena: str = ""
    ciudad: str = ""
    aliada: bool = False


class FarmaciaVer(FarmaciaCrear):
    model_config = ConfigDict(from_attributes=True)
    id: int


class PrecioCrear(BaseModel):
    medicamento_id: int
    farmacia_id: int
    precio_bs: float
    unidad_venta: str = "unidad"


class PrecioVer(PrecioCrear):
    model_config = ConfigDict(from_attributes=True)
    id: int
    actualizado: datetime


class ConsultaVer(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    usuario_id: int
    texto: str
    respuesta: str
    exitosa: bool
    creado: datetime


class UsuarioVer(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    telefono: str
    nombre: str
    suscrito_hasta: date | None
    creado: datetime


class PagoVer(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    usuario_id: int
    proveedor: str
    qr_id: str
    monto_bs: float
    dias: int
    estado: str
    creado: datetime
    pagado_en: datetime | None
