from app.motor.equivalencias import (
    buscar_equivalentes,
    buscar_medicamento,
    responder_consulta,
)


def test_buscar_por_nombre_comercial(sesion):
    medicamento = buscar_medicamento(sesion, "Amoxil 500 mg")
    assert medicamento is not None
    assert medicamento.nombre_comercial == "Amoxil"


def test_buscar_por_principio_activo(sesion):
    medicamento = buscar_medicamento(sesion, "amoxicilina 500mg capsulas")
    assert medicamento is not None
    assert medicamento.principio_activo == "amoxicilina"


def test_buscar_tolera_errores_de_tipeo(sesion):
    medicamento = buscar_medicamento(sesion, "amoxicilna")  # falta la 'i'
    assert medicamento is not None
    assert medicamento.principio_activo == "amoxicilina"


def test_equivalentes_mismo_principio_concentracion_y_forma(sesion):
    amoxil = buscar_medicamento(sesion, "Amoxil")
    equivalentes = {m.nombre_comercial for m in buscar_equivalentes(sesion, amoxil)}
    assert equivalentes == {"Amoxibol", "Amoxicilina Genérica"}


def test_respuesta_ordena_por_precio_y_calcula_ahorro(sesion):
    resultado = responder_consulta(sesion, "Amoxil 500 mg")
    assert resultado.encontrado
    # El más barato es el genérico en La Económica (Bs 0.90)
    assert resultado.opciones[0].precio_bs == 0.90
    assert "Ahorro potencial" in resultado.mensaje
    # Ahorro = Amoxil más caro (3.50) - opción más barata (0.90)
    assert "Bs 2.60" in resultado.mensaje
    assert "no reemplaza el criterio" in resultado.mensaje


def test_medicamento_desconocido(sesion):
    resultado = responder_consulta(sesion, "xyzabc123")
    assert not resultado.encontrado
    assert "No encontré" in resultado.mensaje
