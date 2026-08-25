"""Carga datos de ejemplo para probar el MVP.

⚠️ Datos ILUSTRATIVOS (nombres y precios inventados/aproximados). Los reales
vendrán de AGEMED (registro) y de los relevamientos de precios en farmacias.

Uso:
    cd tatareceta
    python semilla.py
"""

from app.db import SesionLocal, crear_tablas
from app.modelos import Farmacia, Medicamento, Precio

FARMACIAS = [
    {"nombre": "Farmacorp Equipetrol", "cadena": "Farmacorp", "ciudad": "Santa Cruz"},
    {"nombre": "Farmacias Chávez Centro", "cadena": "Farmacias Chávez", "ciudad": "Santa Cruz"},
    {"nombre": "Farmacia Hipermaxi Norte", "cadena": "Hipermaxi", "ciudad": "Santa Cruz"},
    {"nombre": "Farmacia La Económica", "cadena": "", "ciudad": "Santa Cruz", "aliada": True},
]

MEDICAMENTOS = [
    # (nombre_comercial, laboratorio, principio_activo, valor, unidad, forma, generico)
    ("Amoxil", "GSK", "amoxicilina", 500, "mg", "capsula", False),
    ("Amoxibol", "Laboratorio Bolívar", "amoxicilina", 500, "mg", "capsula", False),
    ("Amoxicilina Genérica", "Inti", "amoxicilina", 500, "mg", "capsula", True),
    ("Tylenol", "J&J", "paracetamol", 500, "mg", "comprimido", False),
    ("Paracetamol Genérico", "Cofar", "paracetamol", 500, "mg", "comprimido", True),
    ("Ibupirac", "Pfizer", "ibuprofeno", 400, "mg", "comprimido", False),
    ("Ibuprofeno Genérico", "Inti", "ibuprofeno", 400, "mg", "comprimido", True),
]

# (nombre_comercial, nombre_farmacia, precio_bs)
PRECIOS = [
    ("Amoxil", "Farmacorp Equipetrol", 3.50),
    ("Amoxil", "Farmacias Chávez Centro", 3.20),
    ("Amoxibol", "Farmacia Hipermaxi Norte", 2.10),
    ("Amoxicilina Genérica", "Farmacia La Económica", 0.90),
    ("Amoxicilina Genérica", "Farmacorp Equipetrol", 1.20),
    ("Tylenol", "Farmacorp Equipetrol", 2.80),
    ("Paracetamol Genérico", "Farmacia La Económica", 0.50),
    ("Ibupirac", "Farmacias Chávez Centro", 3.00),
    ("Ibuprofeno Genérico", "Farmacia La Económica", 0.80),
]


def sembrar(sesion) -> None:
    farmacias = {}
    for datos in FARMACIAS:
        farmacia = Farmacia(**datos)
        sesion.add(farmacia)
        farmacias[datos["nombre"]] = farmacia

    medicamentos = {}
    for nombre, lab, principio, valor, unidad, forma, generico in MEDICAMENTOS:
        medicamento = Medicamento(
            nombre_comercial=nombre,
            laboratorio=lab,
            principio_activo=principio,
            concentracion_valor=valor,
            concentracion_unidad=unidad,
            forma=forma,
            es_generico=generico,
        )
        sesion.add(medicamento)
        medicamentos[nombre] = medicamento
    sesion.flush()

    for nombre_med, nombre_farm, precio in PRECIOS:
        sesion.add(
            Precio(
                medicamento_id=medicamentos[nombre_med].id,
                farmacia_id=farmacias[nombre_farm].id,
                precio_bs=precio,
            )
        )
    sesion.commit()


if __name__ == "__main__":
    crear_tablas()
    with SesionLocal() as sesion:
        sembrar(sesion)
    print(f"Semilla cargada: {len(MEDICAMENTOS)} medicamentos, "
          f"{len(FARMACIAS)} farmacias, {len(PRECIOS)} precios.")
