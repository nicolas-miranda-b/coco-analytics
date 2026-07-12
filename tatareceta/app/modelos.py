"""Modelos de datos.

El catálogo de medicamentos sigue la estructura del registro sanitario de
AGEMED: principio activo + concentración + forma farmacéutica identifican una
equivalencia terapéutica (sin reemplazar el criterio médico).
"""

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


class Medicamento(Base):
    __tablename__ = "medicamentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_comercial: Mapped[str] = mapped_column(String(200), index=True)
    laboratorio: Mapped[str] = mapped_column(String(200), default="")
    registro_sanitario: Mapped[str] = mapped_column(String(50), default="")
    # Campos normalizados (ver motor/normalizacion.py) que definen equivalencia:
    principio_activo: Mapped[str] = mapped_column(String(200), index=True)
    concentracion_valor: Mapped[float] = mapped_column(Float)
    concentracion_unidad: Mapped[str] = mapped_column(String(20))  # mg, mg/ml, ui, %
    forma: Mapped[str] = mapped_column(String(50))  # comprimido, capsula, jarabe...
    es_generico: Mapped[bool] = mapped_column(default=False)

    precios: Mapped[list["Precio"]] = relationship(back_populates="medicamento")


class Farmacia(Base):
    __tablename__ = "farmacias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200), unique=True)
    cadena: Mapped[str] = mapped_column(String(200), default="")
    ciudad: Mapped[str] = mapped_column(String(100), default="")
    aliada: Mapped[bool] = mapped_column(default=False)

    precios: Mapped[list["Precio"]] = relationship(back_populates="farmacia")


class Precio(Base):
    __tablename__ = "precios"
    __table_args__ = (
        UniqueConstraint("medicamento_id", "farmacia_id", name="uq_precio_med_farmacia"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    medicamento_id: Mapped[int] = mapped_column(ForeignKey("medicamentos.id"), index=True)
    farmacia_id: Mapped[int] = mapped_column(ForeignKey("farmacias.id"), index=True)
    precio_bs: Mapped[float] = mapped_column(Float)
    unidad_venta: Mapped[str] = mapped_column(String(50), default="unidad")
    actualizado: Mapped[datetime] = mapped_column(DateTime, default=_ahora)

    medicamento: Mapped[Medicamento] = relationship(back_populates="precios")
    farmacia: Mapped[Farmacia] = relationship(back_populates="precios")


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    telefono: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(200), default="")
    suscrito_hasta: Mapped[date | None] = mapped_column(Date, nullable=True)
    creado: Mapped[datetime] = mapped_column(DateTime, default=_ahora)

    consultas: Mapped[list["Consulta"]] = relationship(back_populates="usuario")

    def suscripcion_activa(self, hoy: date | None = None) -> bool:
        hoy = hoy or date.today()
        return self.suscrito_hasta is not None and self.suscrito_hasta >= hoy


class Consulta(Base):
    __tablename__ = "consultas"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    texto: Mapped[str] = mapped_column(Text)
    respuesta: Mapped[str] = mapped_column(Text, default="")
    exitosa: Mapped[bool] = mapped_column(default=False)
    creado: Mapped[datetime] = mapped_column(DateTime, default=_ahora)

    usuario: Mapped[Usuario] = relationship(back_populates="consultas")
