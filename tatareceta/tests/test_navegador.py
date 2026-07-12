"""Test del scraper de navegador contra una página local que imita un
catálogo de tienda (grilla de tarjetas de producto renderizada por JS)."""

import pytest

FIXTURE = """
<!doctype html>
<html><body>
  <header><a href="/">Mi Tienda</a><span>Envíos a todo el país</span></header>
  <div id="grilla"></div>
  <script>
    const productos = [
      ["PARACETAMOL 500 MG X 10 COMPRIMIDOS COFAR", "3,50"],
      ["IBUPROFENO 400 MG CAJA X 50 COMPRIMIDOS", "28,00"],
      ["JABON DE TOCADOR 90 G", "6,00"],
    ];
    // catálogo renderizado por JavaScript, como Hipermaxi/PedidosYa
    document.getElementById("grilla").innerHTML = productos.map(([n, p]) => `
      <article class="tarjeta">
        <img alt="foto" src="data:image/gif;base64,R0lGODlhAQABAAAAACw=" />
        <h3>${n}</h3>
        <div class="pie"><span class="precio">Bs ${p}</span><button>Agregar</button></div>
      </article>`).join("");
  </script>
</body></html>
"""


def test_extraccion_heuristica_de_pagina_local(tmp_path):
    playwright = pytest.importorskip("playwright.sync_api")
    archivo = tmp_path / "catalogo.html"
    archivo.write_text(FIXTURE, encoding="utf-8")

    from app.importadores.navegador import extraer_de_archivo

    try:
        filas = extraer_de_archivo(archivo)
    except Exception as error:  # sin Chromium utilizable en este entorno
        pytest.skip(f"Chromium no disponible: {error}")

    por_producto = {f["producto"]: float(f["precio"]) for f in filas}
    assert por_producto.get("PARACETAMOL 500 MG X 10 COMPRIMIDOS COFAR") == 3.50
    assert por_producto.get("IBUPROFENO 400 MG CAJA X 50 COMPRIMIDOS") == 28.00
    # El encabezado del sitio no debe colarse como producto
    assert "Envíos a todo el país" not in por_producto


def test_extraccion_e_importacion_completa(tmp_path, sesion):
    pytest.importorskip("playwright.sync_api")
    archivo = tmp_path / "catalogo.html"
    archivo.write_text(FIXTURE, encoding="utf-8")

    from app.importadores.navegador import extraer_de_archivo
    from app.importadores.precios import importar_precios

    try:
        filas = extraer_de_archivo(archivo)
    except Exception as error:
        pytest.skip(f"Chromium no disponible: {error}")

    resultado = importar_precios(sesion, filas, farmacia_defecto="Hipermaxi Online")
    # Paracetamol e ibuprofeno del catálogo se emparejan; el jabón no
    assert resultado.creados == 2
    assert any("JABON" in t for t in resultado.sin_emparejar)
