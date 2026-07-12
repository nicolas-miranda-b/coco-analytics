"""Motor de normalización — la ventaja competitiva del proyecto.

Convierte texto libre ("Amoxil 500mg capsulas", "amoxicilina 1 g comp.") en
una consulta estructurada: nombre + concentración canónica + forma canónica.
Dos medicamentos son equivalentes si comparten principio activo,
concentración y forma farmacéutica.
"""

import re
import unicodedata
from dataclasses import dataclass

# Sinónimos de formas farmacéuticas → forma canónica
FORMAS: dict[str, set[str]] = {
    "comprimido": {"comprimido", "comprimidos", "comp", "tableta", "tabletas", "tab", "tabs", "grageas", "gragea"},
    "capsula": {"capsula", "capsulas", "cap", "caps"},
    "jarabe": {"jarabe", "suspension", "susp", "suspensión"},
    "solucion": {"solucion", "gotas", "solucion oral"},
    "inyectable": {"inyectable", "ampolla", "ampollas", "amp", "vial", "viales"},
    "crema": {"crema", "pomada", "unguento", "gel"},
    "sobre": {"sobre", "sobres", "polvo"},
}

_SINONIMO_A_FORMA = {sin: forma for forma, sinonimos in FORMAS.items() for sin in sinonimos}

# unidad detectada → (unidad canónica, factor de conversión del valor)
_UNIDADES = {
    "mg": ("mg", 1.0),
    "g": ("mg", 1000.0),
    "gr": ("mg", 1000.0),
    "mcg": ("mg", 0.001),
    "ug": ("mg", 0.001),
    "ui": ("ui", 1.0),
    "%": ("%", 1.0),
    "mg/ml": ("mg/ml", 1.0),
    "mg/5ml": ("mg/5ml", 1.0),
}

_PATRON_CONCENTRACION = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(mg/5ml|mg/ml|mcg|mg|gr|g|ug|ui|%)(?![a-z])",
    re.IGNORECASE,
)


def quitar_acentos(texto: str) -> str:
    descompuesto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in descompuesto if not unicodedata.combining(c))


def normalizar_texto(texto: str) -> str:
    """Minúsculas, sin acentos, sin puntuación sobrante, espacios simples."""
    texto = quitar_acentos(texto.lower().strip())
    texto = re.sub(r"[^\w%/.,\s-]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def extraer_concentracion(texto: str) -> tuple[float, str] | None:
    """Devuelve (valor, unidad) canónicos, p. ej. '1 g' → (1000.0, 'mg')."""
    coincidencia = _PATRON_CONCENTRACION.search(normalizar_texto(texto))
    if not coincidencia:
        return None
    valor = float(coincidencia.group(1).replace(",", "."))
    unidad_canonica, factor = _UNIDADES[coincidencia.group(2).lower()]
    return (valor * factor, unidad_canonica)


def normalizar_forma(texto: str) -> str | None:
    """Busca una forma farmacéutica en el texto y devuelve su nombre canónico."""
    for palabra in normalizar_texto(texto).replace(".", " ").split():
        if palabra in _SINONIMO_A_FORMA:
            return _SINONIMO_A_FORMA[palabra]
    return None


@dataclass
class ConsultaInterpretada:
    nombre: str  # lo que queda tras quitar concentración y forma
    concentracion: tuple[float, str] | None
    forma: str | None


def interpretar_consulta(texto: str) -> ConsultaInterpretada:
    """Separa un mensaje libre en nombre + concentración + forma."""
    limpio = normalizar_texto(texto)
    concentracion = extraer_concentracion(limpio)
    forma = normalizar_forma(limpio)

    limpio = _PATRON_CONCENTRACION.sub(" ", limpio)
    palabras = [
        p for p in limpio.replace(".", " ").split()
        if p not in _SINONIMO_A_FORMA
    ]
    return ConsultaInterpretada(
        nombre=" ".join(palabras).strip(),
        concentracion=concentracion,
        forma=forma,
    )
