import os
import sys
from pathlib import Path

# BD en memoria compartida para toda la sesión de tests (antes de importar la app)
os.environ["TATARECETA_DB"] = "sqlite://"
os.environ["ADMIN_TOKEN"] = "token-de-prueba"
os.environ["CONSULTAS_GRATIS"] = "3"

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient

from app.db import Base, SesionLocal, crear_tablas, engine
from app.main import app
from semilla import sembrar


@pytest.fixture()
def cliente():
    crear_tablas()
    with SesionLocal() as sesion:
        sembrar(sesion)
    with TestClient(app) as tc:
        yield tc
    Base.metadata.drop_all(engine)


@pytest.fixture()
def sesion():
    crear_tablas()
    with SesionLocal() as s:
        sembrar(s)
        yield s
    Base.metadata.drop_all(engine)
