"""Lectura de recetas por foto.

Proveedores:
- ``claude``: visión vía API de Anthropic. Además de transcribir, entiende
  letra de médico y devuelve los medicamentos ya estructurados (uno por
  línea: nombre + concentración + forma). Requiere ANTHROPIC_API_KEY.
- ``simulado``: devuelve OCR_SIMULADO_TEXTO (para desarrollo y tests).
- ``auto`` (por defecto): claude si hay API key; si no, simulado si hay
  texto configurado; si no, OCR deshabilitado (el bot pide el nombre por
  texto).

La IA solo LEE la receta; nunca recomienda tratamientos (límite definido en
el resumen del proyecto).
"""

import base64
import logging
from typing import Protocol

from ..config import config

logger = logging.getLogger("tatareceta.ocr")

INSTRUCCION_LECTURA = (
    "Esta imagen es una receta médica o el empaque de un medicamento. "
    "Extrae ÚNICAMENTE los medicamentos que aparecen, uno por línea, con el "
    "formato: nombre concentración forma (ej: 'amoxicilina 500 mg capsulas'). "
    "Si un dato no se lee, omítelo. No incluyas dosis/frecuencia, nombres de "
    "personas ni ningún otro texto. Si no hay medicamentos legibles, responde "
    "exactamente: NINGUNO"
)


class ProveedorOCR(Protocol):
    def extraer_medicamentos(self, imagen: bytes, tipo_mime: str) -> list[str]: ...


class OCRClaude:
    """Lee la receta con un modelo de visión de Anthropic."""

    URL = "https://api.anthropic.com/v1/messages"

    def extraer_medicamentos(self, imagen: bytes, tipo_mime: str) -> list[str]:
        import httpx

        respuesta = httpx.post(
            self.URL,
            headers={
                "x-api-key": config.anthropic_api_key,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": config.ocr_modelo,
                "max_tokens": 500,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": tipo_mime,
                                    "data": base64.b64encode(imagen).decode(),
                                },
                            },
                            {"type": "text", "text": INSTRUCCION_LECTURA},
                        ],
                    }
                ],
            },
            timeout=60,
        )
        respuesta.raise_for_status()
        texto = "".join(
            bloque.get("text", "")
            for bloque in respuesta.json().get("content", [])
            if bloque.get("type") == "text"
        )
        return _lineas_de_medicamentos(texto)


class OCRSimulado:
    def extraer_medicamentos(self, imagen: bytes, tipo_mime: str) -> list[str]:
        logger.info("[simulado] OCR de imagen de %d bytes", len(imagen))
        return _lineas_de_medicamentos(config.ocr_simulado_texto)


def _lineas_de_medicamentos(texto: str) -> list[str]:
    lineas = [linea.strip(" -*•") for linea in (texto or "").splitlines()]
    return [l for l in lineas if l and l.upper() != "NINGUNO"]


def obtener_ocr() -> ProveedorOCR | None:
    """Devuelve el proveedor configurado, o None si el OCR está deshabilitado."""
    eleccion = config.ocr_proveedor
    if eleccion == "claude" or (eleccion == "auto" and config.anthropic_api_key):
        return OCRClaude()
    if eleccion == "simulado" or (eleccion == "auto" and config.ocr_simulado_texto):
        return OCRSimulado()
    return None
