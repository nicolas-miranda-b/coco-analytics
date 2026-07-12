import json

from sqlalchemy import select

from app.importadores.agemed import (
    cargar_archivo,
    importar_registros,
    interpretar_registro,
)
from app.modelos import Medicamento
from app.motor.equivalencias import buscar_equivalentes


def test_interpretar_registro_con_campos_estandar():
    registro = interpretar_registro(
        {
            "REGISTRO_SANITARIO": "I-12345/2024",
            "NOMBRE_COMERCIAL": "Amoxil",
            "PRINCIPIO_ACTIVO": "Amoxicilina",
            "CONCENTRACION": "500 mg",
            "FORMA_FARMACEUTICA": "Cápsulas",
            "LABORATORIO": "GSK",
        }
    )
    assert registro.completo
    assert registro.registro_sanitario == "I-12345/2024"
    assert registro.principio_activo == "amoxicilina"
    assert registro.concentracion_valor == 500.0
    assert registro.concentracion_unidad == "mg"
    assert registro.forma == "capsula"


def test_interpretar_registro_con_nombres_de_campo_alternativos():
    # Variantes de nombre de campo que podría usar la API (minúsculas, sinónimos)
    registro = interpretar_registro(
        {
            "nro_registro": "N-777/2023",
            "producto": "Ibupirac 400 mg comprimidos",
            "generico": "ibuprofeno",
            "titular": "Pfizer",
        }
    )
    # Sin campos de concentración/forma: se extraen del nombre del producto
    assert registro.completo
    assert registro.concentracion_valor == 400.0
    assert registro.forma == "comprimido"
    assert registro.laboratorio == "Pfizer"


def test_interpretar_registro_concentracion_incrustada_en_principio():
    registro = interpretar_registro(
        {
            "registro": "G-1/2022",
            "descripcion": "Azitrocin tabletas",
            "denominacion_generica": "azitromicina 500 mg",
        }
    )
    assert registro.completo
    assert registro.principio_activo == "azitromicina"
    assert registro.concentracion_valor == 500.0
    assert registro.forma == "comprimido"


def test_registro_incompleto_no_es_valido():
    registro = interpretar_registro({"producto": "Producto misterioso"})
    assert not registro.completo


def test_importar_crea_y_reimportar_actualiza(sesion):
    crudos = [
        {
            "registro": "I-11111/2024",
            "producto": "Azitrocin",
            "principio_activo": "azitromicina",
            "concentracion": "500 mg",
            "forma_farmaceutica": "comprimidos",
            "laboratorio": "Lab A",
        },
        {
            "registro": "I-22222/2024",
            "producto": "Azitromicina IFA",
            "principio_activo": "azitromicina",
            "concentracion": "500 mg",
            "forma_farmaceutica": "tabletas",
            "laboratorio": "IFA",
        },
        {"producto": "incompleto"},
    ]
    resultado = importar_registros(sesion, crudos)
    assert resultado.creados == 2
    assert resultado.descartados == 1

    # El genérico se detecta porque el nombre empieza con el principio activo
    generico = sesion.scalar(
        select(Medicamento).where(Medicamento.nombre_comercial == "Azitromicina IFA")
    )
    assert generico.es_generico
    assert not sesion.scalar(
        select(Medicamento).where(Medicamento.nombre_comercial == "Azitrocin")
    ).es_generico

    # Los dos quedan como equivalentes entre sí (misma tripleta)
    azitrocin = sesion.scalar(
        select(Medicamento).where(Medicamento.nombre_comercial == "Azitrocin")
    )
    equivalentes = {m.nombre_comercial for m in buscar_equivalentes(sesion, azitrocin)}
    assert "Azitromicina IFA" in equivalentes

    # Reimportar el mismo listado no duplica: actualiza por registro sanitario
    crudos[0]["laboratorio"] = "Lab A actualizado"
    resultado2 = importar_registros(sesion, crudos[:2])
    assert resultado2.creados == 0
    assert resultado2.actualizados == 2
    azitrocin = sesion.scalar(
        select(Medicamento).where(Medicamento.nombre_comercial == "Azitrocin")
    )
    assert azitrocin.laboratorio == "Lab A actualizado"


def test_cargar_archivo_json_lista_y_envuelto(tmp_path):
    lista = [{"producto": "X"}]
    directo = tmp_path / "directo.json"
    directo.write_text(json.dumps(lista))
    assert cargar_archivo(directo) == lista

    envuelto = tmp_path / "envuelto.json"
    envuelto.write_text(json.dumps({"status": "ok", "data": lista}))
    assert cargar_archivo(envuelto) == lista


def test_cargar_archivo_csv(tmp_path):
    archivo = tmp_path / "registros.csv"
    archivo.write_text(
        "registro,producto,principio_activo,concentracion,forma_farmaceutica\n"
        "I-1/2024,Amoxil,amoxicilina,500 mg,capsulas\n",
        encoding="utf-8",
    )
    filas = cargar_archivo(archivo)
    assert len(filas) == 1
    assert filas[0]["producto"] == "Amoxil"
