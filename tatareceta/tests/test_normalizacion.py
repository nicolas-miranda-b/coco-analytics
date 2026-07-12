from app.motor.normalizacion import (
    extraer_concentracion,
    interpretar_consulta,
    normalizar_forma,
    normalizar_texto,
)


def test_normalizar_texto_quita_acentos_y_mayusculas():
    assert normalizar_texto("  Suspensión ORAL ") == "suspension oral"


def test_extraer_concentracion_mg():
    assert extraer_concentracion("amoxicilina 500 mg") == (500.0, "mg")
    assert extraer_concentracion("amoxicilina 500mg") == (500.0, "mg")


def test_extraer_concentracion_convierte_gramos_y_microgramos():
    assert extraer_concentracion("azitromicina 1 g") == (1000.0, "mg")
    assert extraer_concentracion("levotiroxina 50 mcg") == (0.05, "mg")


def test_extraer_concentracion_unidades_especiales():
    assert extraer_concentracion("insulina 100 UI") == (100.0, "ui")
    assert extraer_concentracion("jarabe 250 mg/5ml") == (250.0, "mg/5ml")


def test_normalizar_forma_sinonimos():
    assert normalizar_forma("tabletas") == "comprimido"
    assert normalizar_forma("caps") == "capsula"
    assert normalizar_forma("suspensión") == "jarabe"
    assert normalizar_forma("crema dental") == "crema"
    assert normalizar_forma("texto sin forma") is None


def test_interpretar_consulta_completa():
    consulta = interpretar_consulta("Amoxil 500mg cápsulas")
    assert consulta.nombre == "amoxil"
    assert consulta.concentracion == (500.0, "mg")
    assert consulta.forma == "capsula"


def test_interpretar_consulta_solo_nombre():
    consulta = interpretar_consulta("ibuprofeno")
    assert consulta.nombre == "ibuprofeno"
    assert consulta.concentracion is None
    assert consulta.forma is None
