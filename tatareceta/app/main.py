"""Aplicación TataReceta.

Ejecutar en desarrollo:
    cd tatareceta
    uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import crear_tablas
from .rutas import admin, webhook


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    crear_tablas()
    yield


app = FastAPI(
    title="TataReceta",
    description=(
        "Asistente por WhatsApp para encontrar medicamentos equivalentes "
        "(mismo principio activo, concentración y forma) al mejor precio. "
        "No reemplaza el criterio médico."
    ),
    version="0.1.0",
    lifespan=ciclo_de_vida,
)

app.include_router(webhook.router)
app.include_router(admin.router)


@app.get("/salud", tags=["salud"])
def salud():
    return {"estado": "ok", "servicio": "tatareceta"}
