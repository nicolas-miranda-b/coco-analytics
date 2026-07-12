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


def test_ahorro_compara_precio_unitario_no_de_envase(sesion):
    # Bug detectado en pruebas reales: una caja x 100 a Bs 320 no debe
    # compararse contra un precio por unidad como si fuera lo mismo.
    from app.importadores.precios import importar_precios

    importar_precios(
        sesion,
        [{"producto": "AMOXIL 500MG CAJA X 100 CAPSULAS", "precio": 320}],
        farmacia_defecto="Farmacorp Online",
    )
    resultado = responder_consulta(sesion, "Amoxil 500 mg")
    # La caja (Bs 3.20 c/u) se ordena por precio unitario, no por precio total
    assert [round(o.precio_unitario, 2) for o in resultado.opciones] == sorted(
        round(o.precio_unitario, 2) for o in resultado.opciones
    )
    # Ahorro: Amoxil más caro por unidad (3.50) - genérico más barato (0.90)
    assert "Bs 2.60" in resultado.mensaje
    assert "por unidad" in resultado.mensaje
    assert "(Bs 3.20 c/u)" in resultado.mensaje  # la caja muestra su precio unitario


def test_medicamento_desconocido(sesion):
    resultado = responder_consulta(sesion, "xyzabc123")
    assert not resultado.encontrado
    assert "No encontré" in resultado.mensaje
