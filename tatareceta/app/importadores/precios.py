"""Importador de precios de farmacias.

Empareja títulos de productos de tienda (p. ej. "AMOXIL 500MG CAJA X 100
CAPSULAS") con el catálogo de medicamentos y registra el precio en esa
farmacia. El emparejamiento es conservador: ante la duda, el producto se
descarta y queda en el reporte de no-emparejados para revisión manual —
un precio mal asignado es peor que un precio faltante.

Uso:
    # Desde un CSV/JSON relevado a mano o exportado de otra fuente:
    python -m app.importadores.precios --archivo precios.csv --farmacia "Farmacorp Online"

    # Desde una tienda VTEX (Farmacorp), buscando términos del catálogo:
    python -m app.importadores.precios --vtex https://www.farmacorp.com --farmacia "Farmacorp Online"

Formato mínimo del archivo: columnas `producto` y `precio` (se aceptan
sinónimos: nombre/titulo/descripcion y precio_bs/importe). Columna opcional
`farmacia` si el archivo mezcla varias sucursales.
"""

import argparse
import logging
import re
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..modelos import Farmacia, Medicamento, Precio
from ..motor.normalizacion import interpretar_consulta, normalizar_texto
from .agemed import cargar_archivo

logger = logging.getLogger("tatareceta.importador.precios")

_CAMPOS_PRODUCTO = ["producto", "nombre", "titulo", "descripcion", "item", "nombre_producto"]
_CAMPOS_PRECIO = ["precio", "precio_bs", "importe", "monto", "price"]
_CAMPOS_FARMACIA = ["farmacia", "sucursal", "tienda", "cadena"]

# "caja x 100", "x100", "blister x 10", "frasco 120 ml"
_PATRON_PRESENTACION = re.compile(
    r"\b(caja|blister|bl[ií]ster|frasco|sobre|display|pack)?\s*x\s*(\d+)\b", re.IGNORECASE
)


def _campo(fila: dict, variantes: list[str]) -> str:
    claves = {normalizar_texto(str(k)).replace(" ", "_"): v for k, v in fila.items()}
    for variante in variantes:
        valor = claves.get(variante)
        if valor is not None and str(valor).strip():
            return str(valor).strip()
    return ""


def _interpretar_precio(texto: str) -> float | None:
    """'Bs 35,50' → 35.5; '35.50' → 35.5."""
    limpio = re.sub(r"[^\d,.]", "", str(texto))
    if not limpio:
        return None
    # Coma como separador decimal (uso boliviano) si no hay punto posterior
    if "," in limpio and "." not in limpio:
        limpio = limpio.replace(",", ".")
    else:
        limpio = limpio.replace(",", "")
    try:
        valor = float(limpio)
    except ValueError:
        return None
    return valor if valor > 0 else None


def detectar_unidad_venta(titulo: str) -> str:
    coincidencia = _PATRON_PRESENTACION.search(titulo)
    if coincidencia:
        envase = (coincidencia.group(1) or "caja").lower()
        return f"{envase} x {coincidencia.group(2)}"
    return "unidad"


def emparejar_producto(sesion: Session, titulo: str) -> Medicamento | None:
    """Busca el medicamento del catálogo que corresponde a un título de tienda.

    Reglas conservadoras:
    - El nombre comercial (o el principio activo) debe aparecer en el título.
    - Si ambos declaran concentración, deben coincidir exactamente.
    - Si el título tiene concentración y el candidato coincide solo por nombre
      con otra concentración, se descarta (no se adivina).
    """
    consulta = interpretar_consulta(titulo)
    titulo_norm = normalizar_texto(titulo)
    if not titulo_norm:
        return None

    candidatos = []
    for med in sesion.scalars(select(Medicamento)):
        nombre_norm = normalizar_texto(med.nombre_comercial)
        principio_norm = normalizar_texto(med.principio_activo)
        por_nombre = bool(nombre_norm) and nombre_norm in titulo_norm
        por_principio = bool(principio_norm) and principio_norm in titulo_norm
        if not (por_nombre or por_principio):
            continue
        if consulta.concentracion is not None:
            valor, unidad = consulta.concentracion
            if med.concentracion_valor != valor or med.concentracion_unidad != unidad:
                continue
        if consulta.forma is not None and med.forma != consulta.forma:
            continue
        # Prioridad: coincidencia por nombre comercial > por principio activo;
        # entre iguales, el nombre más largo (más específico) gana.
        candidatos.append((por_nombre, len(nombre_norm if por_nombre else principio_norm), med))

    if not candidatos:
        return None
    candidatos.sort(key=lambda c: (c[0], c[1]), reverse=True)

    # Ambigüedad real: dos medicamentos distintos con la misma prioridad máxima
    # (mismo nombre en el título y sin concentración que desambigüe) → descartar.
    maxima = [c for c in candidatos if (c[0], c[1]) == (candidatos[0][0], candidatos[0][1])]
    if len(maxima) > 1 and consulta.concentracion is None:
        logger.warning("Título ambiguo, se descarta: %r", titulo)
        return None
    return candidatos[0][2]


def _obtener_o_crear_farmacia(sesion: Session, nombre: str) -> Farmacia:
    farmacia = sesion.scalar(select(Farmacia).where(Farmacia.nombre == nombre))
    if farmacia is None:
        farmacia = Farmacia(nombre=nombre)
        sesion.add(farmacia)
        sesion.flush()
    return farmacia


@dataclass
class ResultadoPrecios:
    creados: int = 0
    actualizados: int = 0
    sin_emparejar: list[str] = field(default_factory=list)
    invalidos: int = 0

    def __str__(self) -> str:
        return (
            f"{self.creados} precios creados, {self.actualizados} actualizados, "
            f"{len(self.sin_emparejar)} sin emparejar, {self.invalidos} inválidos"
        )


def importar_precios(
    sesion: Session, filas: list[dict], farmacia_defecto: str = ""
) -> ResultadoPrecios:
    resultado = ResultadoPrecios()
    for fila in filas:
        titulo = _campo(fila, _CAMPOS_PRODUCTO)
        precio = _interpretar_precio(_campo(fila, _CAMPOS_PRECIO))
        nombre_farmacia = _campo(fila, _CAMPOS_FARMACIA) or farmacia_defecto
        if not titulo or precio is None or not nombre_farmacia:
            resultado.invalidos += 1
            continue

        medicamento = emparejar_producto(sesion, titulo)
        if medicamento is None:
            resultado.sin_emparejar.append(titulo)
            continue

        farmacia = _obtener_o_crear_farmacia(sesion, nombre_farmacia)
        existente = sesion.scalar(
            select(Precio).where(
                Precio.medicamento_id == medicamento.id,
                Precio.farmacia_id == farmacia.id,
            )
        )
        unidad = detectar_unidad_venta(titulo)
        if existente:
            existente.precio_bs = precio
            existente.unidad_venta = unidad
            resultado.actualizados += 1
        else:
            sesion.add(
                Precio(
                    medicamento_id=medicamento.id,
                    farmacia_id=farmacia.id,
                    precio_bs=precio,
                    unidad_venta=unidad,
                )
            )
            resultado.creados += 1
    sesion.commit()
    return resultado


# ---------------------------------------------------------------------------
# Conector VTEX (Farmacorp usa esta plataforma). La API pública de búsqueda
# de VTEX es estándar: /api/catalog_system/pub/products/search/?ft=<término>
# ---------------------------------------------------------------------------

def extraer_filas_vtex(productos: list[dict]) -> list[dict]:
    """Convierte la respuesta de la API de búsqueda de VTEX en filas planas."""
    filas = []
    for producto in productos:
        titulo = producto.get("productName") or producto.get("productTitle") or ""
        for item in producto.get("items", []):
            for vendedor in item.get("sellers", []):
                oferta = vendedor.get("commertialOffer") or {}
                precio = oferta.get("Price") or oferta.get("price")
                disponible = oferta.get("IsAvailable", True)
                if precio and disponible:
                    filas.append(
                        {"producto": item.get("name") or titulo, "precio": precio}
                    )
                    break  # un precio por ítem es suficiente
    return filas


def buscar_vtex(dominio: str, termino: str, cantidad: int = 50) -> list[dict]:
    """Busca productos en una tienda VTEX y devuelve filas producto/precio."""
    import httpx

    url = f"{dominio.rstrip('/')}/api/catalog_system/pub/products/search/"
    respuesta = httpx.get(
        url,
        params={"ft": termino, "_from": 0, "_to": max(0, cantidad - 1)},
        timeout=30,
        follow_redirects=True,
        headers={"Accept": "application/json"},
    )
    respuesta.raise_for_status()
    return extraer_filas_vtex(respuesta.json())


def importar_desde_vtex(
    sesion: Session, dominio: str, farmacia: str, terminos: list[str] | None = None
) -> ResultadoPrecios:
    """Busca en la tienda VTEX cada término (por defecto, los principios
    activos del catálogo) e importa los precios encontrados."""
    if not terminos:
        terminos = sorted(
            {m.principio_activo for m in sesion.scalars(select(Medicamento))}
        )
    filas: list[dict] = []
    for termino in terminos:
        try:
            encontradas = buscar_vtex(dominio, termino)
        except Exception as error:  # red, HTTP, JSON: se informa y se sigue
            logger.warning("Búsqueda VTEX falló para %r: %s", termino, error)
            continue
        logger.info("VTEX %r: %d productos", termino, len(encontradas))
        filas.extend(encontradas)
    return importar_precios(sesion, filas, farmacia_defecto=farmacia)


def main() -> None:
    parser = argparse.ArgumentParser(description="Importa precios de farmacias")
    origen = parser.add_mutually_exclusive_group(required=True)
    origen.add_argument("--archivo", help="CSV/JSON con columnas producto y precio")
    origen.add_argument("--vtex", help="Dominio de tienda VTEX, p. ej. https://www.farmacorp.com")
    parser.add_argument("--farmacia", required=True, help='Nombre de la farmacia, p. ej. "Farmacorp Online"')
    parser.add_argument(
        "--terminos",
        help="Términos de búsqueda VTEX separados por coma (por defecto: principios activos del catálogo)",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    from ..db import SesionLocal, crear_tablas

    crear_tablas()
    with SesionLocal() as sesion:
        if args.archivo:
            filas = cargar_archivo(args.archivo)
            logger.info("Filas recibidas: %d", len(filas))
            resultado = importar_precios(sesion, filas, farmacia_defecto=args.farmacia)
        else:
            terminos = [t.strip() for t in args.terminos.split(",")] if args.terminos else None
            resultado = importar_desde_vtex(sesion, args.vtex, args.farmacia, terminos)

    logger.info("Importación terminada: %s", resultado)
    if resultado.sin_emparejar:
        logger.info("Sin emparejar (revisar manualmente):")
        for titulo in resultado.sin_emparejar:
            logger.info("  - %s", titulo)


if __name__ == "__main__":
    main()
