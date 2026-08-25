"""Importador del registro sanitario de AGEMED.

Fuentes conocidas (julio 2026):
- API pública: https://apiwww.agemed.gob.bo/api/listautcom
  ("listado oficial diario de registros sanitarios aprobados")
- Sistema de gestión: https://regsanitario.agemed.gob.bo/
- Listados semanales en PDF: https://www.agemed.gob.bo/archivo_regsan/tramites/...

Como el esquema exacto de la API no está documentado públicamente, el
importador usa un mapeo flexible de campos: reconoce variantes de nombre
(con o sin acentos, mayúsculas, prefijos) y, si el registro no trae
concentración o forma farmacéutica como campos separados, las extrae de la
descripción del producto con el motor de normalización.

Uso:
    # Desde un archivo descargado (JSON o CSV):
    python -m app.importadores.agemed --archivo registros.json

    # Directo desde la API (requiere salida a internet hacia agemed.gob.bo):
    python -m app.importadores.agemed --url https://apiwww.agemed.gob.bo/api/listautcom
"""

import argparse
import csv
import json
import logging
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..modelos import Medicamento
from ..motor.normalizacion import (
    extraer_concentracion,
    normalizar_forma,
    normalizar_texto,
)

logger = logging.getLogger("tatareceta.importador.agemed")

URL_API_AGEMED = "https://apiwww.agemed.gob.bo/api/listautcom"

# Variantes conocidas/esperables de cada campo (comparadas ya normalizadas).
_CAMPOS = {
    "registro_sanitario": [
        "registro_sanitario", "registro", "reg_san", "regsan", "nro_registro",
        "numero_registro", "num_registro", "nro_reg_san", "codigo_registro",
    ],
    "nombre_comercial": [
        "nombre_comercial", "producto", "nombre_producto", "descripcion_comercial",
        "nombre", "descripcion", "medicamento", "denominacion_comercial",
    ],
    "principio_activo": [
        "principio_activo", "principio", "generico", "denominacion_generica",
        "nombre_generico", "dci", "composicion",
    ],
    "concentracion": [
        "concentracion", "dosis", "dosificacion", "potencia",
    ],
    "forma": [
        "forma_farmaceutica", "forma", "presentacion", "forma_farm",
    ],
    "laboratorio": [
        "laboratorio", "fabricante", "titular", "empresa", "importador",
        "laboratorio_fabricante", "razon_social",
    ],
}


def _clave_normalizada(clave: str) -> str:
    return normalizar_texto(str(clave)).replace(" ", "_").replace("-", "_")


def _extraer_campo(registro: dict, nombre_campo: str) -> str:
    """Busca un campo probando todas las variantes de nombre conocidas."""
    claves = {_clave_normalizada(k): v for k, v in registro.items()}
    for variante in _CAMPOS[nombre_campo]:
        valor = claves.get(variante)
        if valor is not None and str(valor).strip():
            return str(valor).strip()
    return ""


@dataclass
class RegistroAgemed:
    registro_sanitario: str
    nombre_comercial: str
    principio_activo: str
    concentracion_valor: float | None
    concentracion_unidad: str | None
    forma: str | None
    laboratorio: str

    @property
    def completo(self) -> bool:
        return bool(
            self.nombre_comercial
            and self.principio_activo
            and self.concentracion_valor is not None
            and self.forma
        )


def interpretar_registro(crudo: dict) -> RegistroAgemed:
    """Convierte un registro crudo de AGEMED al formato interno."""
    nombre = _extraer_campo(crudo, "nombre_comercial")
    principio = _extraer_campo(crudo, "principio_activo")
    texto_concentracion = _extraer_campo(crudo, "concentracion")
    texto_forma = _extraer_campo(crudo, "forma")

    # Concentración: del campo propio o, si falta, del nombre del producto.
    concentracion = extraer_concentracion(texto_concentracion) if texto_concentracion else None
    if concentracion is None and nombre:
        concentracion = extraer_concentracion(nombre)
    # El principio activo a veces también la trae ("amoxicilina 500 mg").
    if concentracion is None and principio:
        concentracion = extraer_concentracion(principio)

    # Forma farmacéutica: campo propio → nombre del producto.
    forma = normalizar_forma(texto_forma) if texto_forma else None
    if forma is None and nombre:
        forma = normalizar_forma(nombre)

    # Limpiar concentración/forma del principio activo si vienen incrustadas.
    principio_limpio = normalizar_texto(principio)
    if principio_limpio:
        from ..motor.normalizacion import interpretar_consulta

        principio_limpio = interpretar_consulta(principio_limpio).nombre or principio_limpio

    return RegistroAgemed(
        registro_sanitario=_extraer_campo(crudo, "registro_sanitario"),
        nombre_comercial=nombre,
        principio_activo=principio_limpio,
        concentracion_valor=concentracion[0] if concentracion else None,
        concentracion_unidad=concentracion[1] if concentracion else None,
        forma=forma,
        laboratorio=_extraer_campo(crudo, "laboratorio"),
    )


def _es_generico(registro: RegistroAgemed) -> bool:
    """Heurística: es genérico si el nombre comercial ES el principio activo."""
    nombre = normalizar_texto(registro.nombre_comercial)
    return bool(registro.principio_activo) and nombre.startswith(registro.principio_activo)


@dataclass
class ResultadoImportacion:
    creados: int = 0
    actualizados: int = 0
    descartados: int = 0

    def __str__(self) -> str:
        return (
            f"{self.creados} creados, {self.actualizados} actualizados, "
            f"{self.descartados} descartados (datos incompletos)"
        )


def importar_registros(sesion: Session, crudos: list[dict]) -> ResultadoImportacion:
    """Inserta o actualiza medicamentos a partir de registros crudos de AGEMED.

    La clave de upsert es el número de registro sanitario; si no viene, se usa
    (nombre comercial + concentración + forma).
    """
    resultado = ResultadoImportacion()
    for crudo in crudos:
        registro = interpretar_registro(crudo)
        if not registro.completo:
            resultado.descartados += 1
            logger.debug("Registro incompleto descartado: %s", crudo)
            continue

        existente = None
        if registro.registro_sanitario:
            existente = sesion.scalar(
                select(Medicamento).where(
                    Medicamento.registro_sanitario == registro.registro_sanitario
                )
            )
        if existente is None:
            existente = sesion.scalar(
                select(Medicamento).where(
                    Medicamento.nombre_comercial == registro.nombre_comercial,
                    Medicamento.concentracion_valor == registro.concentracion_valor,
                    Medicamento.concentracion_unidad == registro.concentracion_unidad,
                    Medicamento.forma == registro.forma,
                )
            )

        if existente is not None:
            existente.principio_activo = registro.principio_activo
            existente.laboratorio = registro.laboratorio or existente.laboratorio
            if registro.registro_sanitario:
                existente.registro_sanitario = registro.registro_sanitario
            existente.es_generico = _es_generico(registro)
            resultado.actualizados += 1
        else:
            sesion.add(
                Medicamento(
                    nombre_comercial=registro.nombre_comercial,
                    laboratorio=registro.laboratorio,
                    registro_sanitario=registro.registro_sanitario,
                    principio_activo=registro.principio_activo,
                    concentracion_valor=registro.concentracion_valor,
                    concentracion_unidad=registro.concentracion_unidad,
                    forma=registro.forma,
                    es_generico=_es_generico(registro),
                )
            )
            resultado.creados += 1
    sesion.commit()
    return resultado


def cargar_archivo(ruta: str | Path) -> list[dict]:
    """Lee registros desde un archivo JSON (lista u objeto con lista) o CSV."""
    ruta = Path(ruta)
    if ruta.suffix.lower() == ".csv":
        with ruta.open(newline="", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))

    datos = json.loads(ruta.read_text(encoding="utf-8"))
    if isinstance(datos, list):
        return datos
    if isinstance(datos, dict):
        # Respuestas tipo {"data": [...]} o {"registros": [...]}
        for valor in datos.values():
            if isinstance(valor, list) and valor and isinstance(valor[0], dict):
                return valor
    raise ValueError(f"No encontré una lista de registros en {ruta}")


def descargar_api(url: str = URL_API_AGEMED) -> list[dict]:
    """Descarga los registros directamente de la API de AGEMED."""
    import httpx

    respuesta = httpx.get(url, timeout=60, follow_redirects=True)
    respuesta.raise_for_status()
    datos = respuesta.json()
    if isinstance(datos, dict):
        for valor in datos.values():
            if isinstance(valor, list):
                return valor
    return datos


def main() -> None:
    parser = argparse.ArgumentParser(description="Importa el registro sanitario de AGEMED")
    origen = parser.add_mutually_exclusive_group(required=True)
    origen.add_argument("--archivo", help="Archivo JSON o CSV descargado de AGEMED")
    origen.add_argument(
        "--url",
        nargs="?",
        const=URL_API_AGEMED,
        help=f"URL de la API (por defecto: {URL_API_AGEMED})",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    from ..db import SesionLocal, crear_tablas

    crudos = cargar_archivo(args.archivo) if args.archivo else descargar_api(args.url)
    logger.info("Registros recibidos: %d", len(crudos))

    crear_tablas()
    with SesionLocal() as sesion:
        resultado = importar_registros(sesion, crudos)
    logger.info("Importación terminada: %s", resultado)


if __name__ == "__main__":
    main()
