"""Estilo y utilidades de gráficos para los notebooks de coco-analytics.

Paleta y helpers pensados para que todos los gráficos del análisis se vean
como un mismo sistema visual, legible en fondo claro.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl

# --- Paleta de marca (tonos coco/tropical, alto contraste) ---
COCO = {
    "marron": "#6F4E37",      # marrón cáscara de coco
    "marron_claro": "#A9746E",
    "verde": "#2E7D5B",       # verde palmera
    "verde_claro": "#7FB069",
    "arena": "#D9C2A3",       # arena / copra
    "crema": "#F2E9DE",       # pulpa / aceite
    "acento": "#E08D3C",      # acento cálido (naranja tostado)
    "azul": "#2F6690",        # acento frío para importaciones
    "gris": "#5C5552",
}

# Secuencia categórica ordenada (para series múltiples)
PALETA = [
    COCO["verde"], COCO["acento"], COCO["azul"], COCO["marron"],
    COCO["verde_claro"], COCO["marron_claro"], COCO["arena"], COCO["gris"],
]

FIGURAS_DIR = Path(__file__).resolve().parents[1] / "analisis" / "figuras"


def aplicar_estilo():
    """Aplica el estilo global de matplotlib para los notebooks."""
    mpl.rcParams.update({
        "figure.figsize": (9, 5.2),
        "figure.dpi": 110,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linestyle": "-",
        "axes.axisbelow": True,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "axes.edgecolor": COCO["gris"],
        "axes.titlecolor": COCO["marron"],
        "font.size": 11,
        "legend.frameon": False,
    })
    plt.rcParams["axes.prop_cycle"] = mpl.cycler(color=PALETA)


def formato_millones(x, pos=None):
    """Formatea un valor en USD como '$1,2 MM' (miles de millones) o '$M'."""
    if abs(x) >= 1e9:
        return f"${x/1e9:.1f} MM".replace(".", ",")
    if abs(x) >= 1e6:
        return f"${x/1e6:.0f} M".replace(".", ",")
    if abs(x) >= 1e3:
        return f"${x/1e3:.0f} k".replace(".", ",")
    return f"${x:.0f}"


def guardar(nombre):
    """Guarda la figura actual en analisis/figuras/<nombre>.png."""
    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)
    ruta = FIGURAS_DIR / f"{nombre}.png"
    plt.savefig(ruta)
    return ruta
