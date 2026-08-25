"""Conexión a la base de datos (SQLite en desarrollo, PostgreSQL en producción)."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import config


class Base(DeclarativeBase):
    pass


def _crear_engine(url: str):
    kwargs = {}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
        # Una BD en memoria vive en una sola conexión: hay que compartirla.
        if url in ("sqlite://", "sqlite:///:memory:"):
            kwargs["poolclass"] = StaticPool
    return create_engine(url, **kwargs)


engine = _crear_engine(config.base_datos_url)
SesionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def crear_tablas() -> None:
    from . import modelos  # noqa: F401  (registra los modelos en Base.metadata)

    Base.metadata.create_all(engine)


def obtener_sesion():
    with SesionLocal() as sesion:
        yield sesion
