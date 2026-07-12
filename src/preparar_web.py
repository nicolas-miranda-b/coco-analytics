"""Genera docs/datos.js para el dashboard web (GitHub Pages).

Combina el microdato oficial del INE (data/raw/coconut_oil_imports_filtered.csv)
con los datasets curados de analisis/datos/*.csv y emite un único archivo JS
con `window.DATOS = {...}` que el dashboard consume sin servidor ni CORS.

Uso: python src/preparar_web.py
"""
import json
from datetime import date
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATOS = BASE / "analisis" / "datos"
RAW = BASE / "data" / "raw" / "coconut_oil_imports_filtered.csv"
OUT = BASE / "docs" / "datos.js"

ACEITE = {1513110000: "crudo", 1513190000: "refinado"}
COCOS = [801119000, 801190000, 801111000]


def cargar(nombre):
    return pd.read_csv(DATOS / nombre)


def main():
    micro = pd.read_csv(RAW)
    micro["kg"] = micro["KILBRU"].fillna(micro["KILOS"]).fillna(0)

    # --- Aceite de coco: nivel transacción compacto (para filtrado dinámico) ---
    ac = micro[micro["NANDINA_CLEAN"].isin(ACEITE)].copy()
    ac["tipo"] = ac["NANDINA_CLEAN"].map(ACEITE)
    aceite = [
        {
            "anio": int(r.GESTION_CLEAN), "tipo": r.tipo,
            "origen": str(r.DESPAI).title().replace("Ð", "Ñ"),
            "depto": str(r.DESDEPTO).title(),
            "cif": round(float(r.PAG_NUM or 0)), "fob": round(float(r.FOB_NUM or 0)),
            "kg": round(float(r.kg)),
        }
        for r in ac.itertuples()
    ]

    # --- Cocos secos: agregado año × origen ---
    co = micro[micro["NANDINA_CLEAN"].isin(COCOS)]
    cg = co.groupby(["GESTION_CLEAN", "DESPAI"]).agg(cif=("PAG_NUM", "sum"), kg=("kg", "sum")).reset_index()
    cocos = [
        {"anio": int(r.GESTION_CLEAN), "origen": str(r.DESPAI).title(),
         "cif": round(float(r.cif)), "kg": round(float(r.kg))}
        for r in cg.itertuples()
    ]

    mundo = {
        "valorAnual": cargar("valor_mundial_por_anio.csv").rename(columns={
            "valor_exportacion_mundial_usd": "usd"})[["anio", "usd", "fuente"]].to_dict("records"),
        "exportadores": cargar("exportadores_mundo_2024.csv").rename(columns={
            "valor_exportacion_usd": "usd", "participacion_pct_aprox": "pct",
            "tipo": "rol"})[["pais", "usd", "pct", "rol"]].to_dict("records"),
        "importadores": cargar("importadores_mundo_2024.csv").rename(columns={
            "valor_importacion_usd": "usd"})[["pais", "usd", "rol"]].to_dict("records"),
        "precios": cargar("precios_internacionales.csv").rename(columns={
            "precio_usd_tonelada": "usd_t"})[["periodo", "anio", "usd_t", "base"]].to_dict("records"),
        "empresas": cargar("empresas_exportadoras.csv")[
            ["empresa", "pais_sede", "rol", "nota"]].to_dict("records"),
    }

    competencia = {
        "marcas": cargar("competencia_marcas_bolivia.csv")[
            ["marca", "origen", "tipo_producto", "presentaciones", "precio_bs_rango", "canal"]].to_dict("records"),
        "importadores": cargar("empresas_importadoras_bolivia.csv")[
            ["empresa", "envios_registrados", "participacion_pct", "nota"]].to_dict("records"),
        "preciosRetail": cargar("precios_bolivia.csv")[
            ["segmento", "precio_bs", "unidad", "equivalente_bs_100ml"]].to_dict("records"),
        "listings": cargar("competencia_listings_bolivia.csv").to_dict("records"),
        "senales": cargar("competencia_senales_bolivia.csv").to_dict("records"),
    }

    legal = cargar("marco_legal_costos.csv").to_dict("records")
    fuentes = cargar("fuentes_oficiales_bolivia.csv")[["fuente", "url", "contenido", "acceso"]].to_dict("records")

    datos = {
        "actualizado": date.today().isoformat(),
        "mundo": mundo,
        "bolivia": {"aceite": aceite, "cocos": cocos},
        "competencia": competencia,
        "legal": legal,
        "fuentes": fuentes,
    }

    OUT.parent.mkdir(exist_ok=True)
    js = "// Generado por src/preparar_web.py — no editar a mano\nwindow.DATOS = " + json.dumps(
        datos, ensure_ascii=False, separators=(",", ":")) + ";\n"
    OUT.write_text(js, encoding="utf-8")
    print(f"Escrito {OUT} ({len(js)//1024} KB, {len(aceite)} transacciones de aceite)")


if __name__ == "__main__":
    main()
