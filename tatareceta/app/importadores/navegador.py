"""Scraper de precios con navegador (Playwright) para tiendas sin API.

Hipermaxi (plataforma propia, 2024), Farmacias Chávez online y PedidosYa son
aplicaciones JavaScript sin API pública documentada, así que se scrapean con
un navegador real. La extracción es HEURÍSTICA en vez de depender de
selectores CSS frágiles: busca todos los precios "Bs 12,50" visibles y toma
el título más cercano en el árbol DOM. Eso la hace tolerante a rediseños y
reutilizable entre tiendas.

Uso (requiere `pip install playwright`; usa el Chromium del sistema):
    python -m app.importadores.navegador --tienda hipermaxi --farmacia "Hipermaxi Online" --terminos paracetamol,ibuprofeno
    python -m app.importadores.navegador --url "https://.../buscar?q={termino}" --farmacia "Otra" --terminos amoxicilina
    # También sirve para páginas guardadas con Ctrl+S en el navegador:
    python -m app.importadores.navegador --html pagina_guardada.html --farmacia "Hipermaxi Online"

Nota legal/operativa: scrapear catálogos públicos para comparar precios es el
mismo uso que hace cualquier comparador; aun así, respetar robots.txt,
espaciar las consultas (este scraper es secuencial y con pausas) y priorizar
acuerdos directos con las cadenas cuando el piloto avance.
"""

import argparse
import logging
from pathlib import Path

logger = logging.getLogger("tatareceta.importador.navegador")

# Plantillas de búsqueda por tienda ({termino} se reemplaza por la búsqueda).
TIENDAS: dict[str, dict] = {
    "hipermaxi": {
        "url": "https://www.hipermaxi.com/buscador?busqueda={termino}",
        "farmacia": "Hipermaxi Online",
    },
    "chavez": {
        "url": "https://online.farmaciachavez.com.bo/busqueda?q={termino}",
        "farmacia": "Farmacias Chávez Online",
    },
    "pedidosya": {
        # PedidosYa agrupa farmacias por cadena; esta es la búsqueda global de la vertical
        "url": "https://www.pedidosya.com.bo/farmacias/busqueda?query={termino}",
        "farmacia": "PedidosYa Farmacias",
    },
}

# JavaScript que corre DENTRO de la página: encuentra nodos de precio y les
# asigna el mejor título cercano subiendo por el DOM.
_JS_EXTRAER = r"""
() => {
  const RE_PRECIO = /Bs\.?\s*([0-9]{1,6}(?:[.,][0-9]{1,2})?)/;
  const esVisible = (el) => {
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  // nodos "hoja" cuyo texto contiene un precio
  const candidatos = [];
  for (const el of document.querySelectorAll("body *")) {
    if (el.children.length > 2) continue;
    const texto = (el.textContent || "").trim();
    if (texto.length > 60) continue;
    const m = texto.match(RE_PRECIO);
    if (m && esVisible(el)) candidatos.push([el, m[1]]);
  }
  const filas = [];
  const usados = new Set();
  for (const [el, precio] of candidatos) {
    // subir hasta encontrar un contenedor con un texto "título" razonable
    let nodo = el, titulo = "";
    for (let nivel = 0; nivel < 6 && nodo; nivel++, nodo = nodo.parentElement) {
      if (usados.has(nodo)) { titulo = ""; break; }
      const textos = Array.from(nodo.querySelectorAll("h1,h2,h3,h4,a,p,span,div"))
        .map(n => (n.childElementCount === 0 ? (n.textContent || "").trim() : ""))
        .filter(t => t.length >= 8 && t.length <= 150 && !RE_PRECIO.test(t));
      if (textos.length) {
        titulo = textos.sort((a, b) => b.length - a.length)[0];
        usados.add(nodo);
        break;
      }
    }
    if (titulo) filas.push({ producto: titulo, precio: precio.replace(",", ".") });
  }
  // dedup por producto+precio
  const vistos = new Set();
  return filas.filter(f => {
    const clave = f.producto + "|" + f.precio;
    if (vistos.has(clave)) return false;
    vistos.add(clave);
    return true;
  });
}
"""


def _lanzar_navegador(p):
    """Chromium del sistema si existe (imagen preconfigurada) o el de Playwright."""
    argumentos = ["--no-sandbox", "--disable-dev-shm-usage"]
    try:
        return p.chromium.launch(headless=True, args=argumentos)
    except Exception:
        return p.chromium.launch(
            headless=True, args=argumentos, executable_path="/opt/pw-browsers/chromium"
        )


def extraer_de_url(url: str, espera_ms: int = 4000) -> list[dict]:
    """Abre la URL en Chromium headless y extrae pares producto/precio."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        navegador = _lanzar_navegador(p)
        try:
            pagina = navegador.new_page(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
                )
            )
            pagina.goto(url, wait_until="domcontentloaded", timeout=45000)
            pagina.wait_for_timeout(espera_ms)  # dejar que el catálogo cargue
            # scroll para disparar carga perezosa
            for _ in range(3):
                pagina.mouse.wheel(0, 2000)
                pagina.wait_for_timeout(800)
            filas = pagina.evaluate(_JS_EXTRAER)
        finally:
            navegador.close()
    logger.info("%s → %d productos con precio", url, len(filas))
    return filas


def extraer_de_archivo(ruta: str | Path) -> list[dict]:
    """Extrae de una página guardada localmente (Ctrl+S en el navegador)."""
    return extraer_de_url(Path(ruta).resolve().as_uri(), espera_ms=500)


def scrapear_tienda(
    tienda: str | None,
    terminos: list[str],
    url_plantilla: str | None = None,
    pausa_ms: int = 2500,
) -> list[dict]:
    if url_plantilla is None:
        if tienda not in TIENDAS:
            raise SystemExit(f"Tienda desconocida: {tienda!r}. Opciones: {sorted(TIENDAS)}")
        url_plantilla = TIENDAS[tienda]["url"]
    filas: list[dict] = []
    for i, termino in enumerate(terminos):
        if i:
            import time

            time.sleep(pausa_ms / 1000)  # no golpear al sitio
        try:
            filas.extend(extraer_de_url(url_plantilla.format(termino=termino)))
        except Exception as error:
            logger.warning("Fallo scrapeando %r: %s", termino, error)
    return filas


def main() -> None:
    parser = argparse.ArgumentParser(description="Scraper de precios con navegador")
    origen = parser.add_mutually_exclusive_group(required=True)
    origen.add_argument("--tienda", choices=sorted(TIENDAS), help="Tienda preconfigurada")
    origen.add_argument("--url", help="Plantilla de URL de búsqueda con {termino}")
    origen.add_argument("--html", help="Página HTML guardada localmente")
    parser.add_argument("--farmacia", help="Nombre de farmacia (por defecto, el de la tienda)")
    parser.add_argument("--terminos", help="Términos separados por coma (por defecto: principios activos del catálogo)")
    parser.add_argument("--solo-mostrar", action="store_true", help="No importar: solo listar lo extraído")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    from ..db import SesionLocal, crear_tablas
    from .precios import importar_precios

    crear_tablas()
    with SesionLocal() as sesion:
        if args.html:
            filas = extraer_de_archivo(args.html)
        else:
            if args.terminos:
                terminos = [t.strip() for t in args.terminos.split(",")]
            else:
                from sqlalchemy import select

                from ..modelos import Medicamento

                terminos = sorted(
                    {m.principio_activo for m in sesion.scalars(select(Medicamento))}
                )
            filas = scrapear_tienda(args.tienda, terminos, url_plantilla=args.url)

        if args.solo_mostrar:
            for fila in filas:
                print(f"  Bs {fila['precio']:>8} — {fila['producto']}")
            return

        farmacia = args.farmacia or (TIENDAS.get(args.tienda or "", {}).get("farmacia", ""))
        if not farmacia:
            raise SystemExit("Falta --farmacia")
        resultado = importar_precios(sesion, filas, farmacia_defecto=farmacia)
        logger.info("Importación terminada: %s", resultado)
        for titulo in resultado.sin_emparejar:
            logger.info("  sin emparejar: %s", titulo)


if __name__ == "__main__":
    main()
