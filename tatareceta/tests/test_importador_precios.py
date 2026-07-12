from sqlalchemy import select

from app.importadores.precios import (
    detectar_unidad_venta,
    emparejar_producto,
    extraer_filas_vtex,
    importar_precios,
)
from app.modelos import Farmacia, Precio


def test_emparejar_por_nombre_comercial_y_concentracion(sesion):
    med = emparejar_producto(sesion, "AMOXIL 500MG CAJA X 100 CAPSULAS")
    assert med is not None
    assert med.nombre_comercial == "Amoxil"


def test_emparejar_por_principio_activo(sesion):
    med = emparejar_producto(sesion, "IBUPROFENO 400 MG X 50 COMPRIMIDOS GENERICO")
    assert med is not None
    assert med.principio_activo == "ibuprofeno"


def test_emparejar_descarta_concentracion_distinta(sesion):
    # Amoxil existe solo en 500 mg; un título de 250 mg no debe emparejarse
    assert emparejar_producto(sesion, "AMOXIL 250MG SUSPENSION") is None


def test_emparejar_descarta_titulo_sin_relacion(sesion):
    assert emparejar_producto(sesion, "SHAMPOO ANTICASPA 400 ML") is None


def test_detectar_unidad_venta():
    assert detectar_unidad_venta("AMOXIL 500MG CAJA X 100") == "caja x 100"
    assert detectar_unidad_venta("PARACETAMOL BLISTER X 10") == "blister x 10"
    assert detectar_unidad_venta("TYLENOL 500 MG") == "unidad"


def test_importar_precios_crea_farmacia_y_precios(sesion):
    filas = [
        {"producto": "AMOXIL 500MG CAJA X 100 CAPSULAS", "precio": "Bs 320,00"},
        {"producto": "TYLENOL 500 MG COMPRIMIDOS", "precio": 2.9},
        {"producto": "PRODUCTO DESCONOCIDO 10MG", "precio": 5},
        {"producto": "SIN PRECIO"},
    ]
    resultado = importar_precios(sesion, filas, farmacia_defecto="Farmacorp Online")
    assert resultado.creados == 2
    assert resultado.sin_emparejar == ["PRODUCTO DESCONOCIDO 10MG"]
    assert resultado.invalidos == 1

    farmacia = sesion.scalar(select(Farmacia).where(Farmacia.nombre == "Farmacorp Online"))
    assert farmacia is not None
    precios = list(sesion.scalars(select(Precio).where(Precio.farmacia_id == farmacia.id)))
    assert len(precios) == 2
    caja = next(p for p in precios if p.unidad_venta == "caja x 100")
    assert caja.precio_bs == 320.0  # "Bs 320,00" interpretado con coma decimal


def test_importar_precios_reimportar_actualiza(sesion):
    filas = [{"producto": "TYLENOL 500 MG", "precio": 2.9}]
    importar_precios(sesion, filas, farmacia_defecto="Farmacorp Online")
    filas[0]["precio"] = 3.1
    resultado = importar_precios(sesion, filas, farmacia_defecto="Farmacorp Online")
    assert resultado.creados == 0
    assert resultado.actualizados == 1


def test_extraer_filas_vtex():
    # Estructura real de /api/catalog_system/pub/products/search de VTEX
    productos = [
        {
            "productName": "Amoxil 500 mg",
            "items": [
                {
                    "name": "AMOXIL 500MG X 100 CAPSULAS",
                    "sellers": [
                        {
                            "commertialOffer": {
                                "Price": 320.0,
                                "IsAvailable": True,
                            }
                        }
                    ],
                }
            ],
        },
        {
            "productName": "Agotado 10 mg",
            "items": [
                {
                    "name": "AGOTADO 10MG",
                    "sellers": [
                        {"commertialOffer": {"Price": 9.0, "IsAvailable": False}}
                    ],
                }
            ],
        },
    ]
    filas = extraer_filas_vtex(productos)
    assert filas == [{"producto": "AMOXIL 500MG X 100 CAPSULAS", "precio": 320.0}]
