"""Prepara los agregados del microdato oficial del INE (importaciones de coco).

Entrada:  data/raw/coconut_oil_imports_filtered.csv
          (microdato INE 2015-2026 filtrado por productos de coco; origen:
          Google Drive / Cocoil / 11_Tamanio_de_mercado / Importaciones / processed)

Salida:   analisis/datos/ine_aceite_coco_anual.csv
          analisis/datos/ine_aceite_coco_origen.csv
          analisis/datos/ine_aceite_coco_departamento.csv
          analisis/datos/ine_cocos_secos.csv

Uso:      python src/preparar_ine.py

Notas de esquema del microdato INE:
- FOB_NUM = valor FOB (USD); FRO_NUM = valor CIF frontera (USD);
  PAG_NUM = valor CIF aduana (USD)  ->  usamos PAG_NUM como "valor de importación".
- El peso viene en KILBRU (2015-2020) o KILOS (2021+): se unifican en kg.
- 2026 es año parcial.
"""
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw" / "coconut_oil_imports_filtered.csv"
OUT = BASE / "analisis" / "datos"

ACEITE = {1513110000: "crudo", 1513190000: "refinado"}
COCOS = [801119000, 801190000, 801111000]  # cocos secos / los demás / para siembra


def main():
    df = pd.read_csv(RAW)
    df["kg"] = df["KILBRU"].fillna(df["KILOS"])

    ac = df[df["NANDINA_CLEAN"].isin(ACEITE)].copy()
    ac["tipo"] = ac["NANDINA_CLEAN"].map(ACEITE)

    # --- Serie anual (con partición crudo/refinado) ---
    anual = ac.groupby("GESTION_CLEAN").agg(
        cif_usd=("PAG_NUM", "sum"), fob_usd=("FOB_NUM", "sum"),
        kg=("kg", "sum"), transacciones=("GESTION", "count"),
    )
    pivote = ac.pivot_table(index="GESTION_CLEAN", columns="tipo",
                            values="PAG_NUM", aggfunc="sum", fill_value=0)
    anual["cif_crudo_usd"] = pivote.get("crudo", 0)
    anual["cif_refinado_usd"] = pivote.get("refinado", 0)
    anual["usd_kg_cif"] = (anual["cif_usd"] / anual["kg"]).round(2)
    anual = anual.round(0).reset_index().rename(columns={"GESTION_CLEAN": "anio"})
    anual["nota"] = ""
    anual.loc[anual["anio"] == 2026, "nota"] = "año parcial"
    anual.to_csv(OUT / "ine_aceite_coco_anual.csv", index=False)

    # --- Por origen (total del período y ventana reciente 2023-2025) ---
    def por_origen(sub, etiqueta):
        g = sub.groupby("DESPAI").agg(cif_usd=("PAG_NUM", "sum"), kg=("kg", "sum"),
                                      transacciones=("GESTION", "count"))
        g["ventana"] = etiqueta
        return g.reset_index().rename(columns={"DESPAI": "origen"})

    origen = pd.concat([
        por_origen(ac, "2015-2026"),
        por_origen(ac[ac["GESTION_CLEAN"].between(2023, 2025)], "2023-2025"),
    ]).round(0)
    origen.to_csv(OUT / "ine_aceite_coco_origen.csv", index=False)

    # --- Por departamento de destino ---
    depto = ac.groupby("DESDEPTO").agg(cif_usd=("PAG_NUM", "sum"), kg=("kg", "sum"))
    depto = depto.sort_values("cif_usd", ascending=False).round(0).reset_index()
    depto = depto.rename(columns={"DESDEPTO": "departamento"})
    depto.to_csv(OUT / "ine_aceite_coco_departamento.csv", index=False)

    # --- Bonus: cocos secos (materia prima importada) ---
    co = df[df["NANDINA_CLEAN"].isin(COCOS)]
    cocos_anual = co.groupby("GESTION_CLEAN").agg(cif_usd=("PAG_NUM", "sum"), kg=("kg", "sum"))
    cocos_anual = cocos_anual.round(0).reset_index().rename(columns={"GESTION_CLEAN": "anio"})
    cocos_origen = co.groupby("DESPAI")["PAG_NUM"].sum().sort_values(ascending=False)
    cocos_origen = cocos_origen.round(0).rename("cif_usd").reset_index().rename(columns={"DESPAI": "origen"})
    cocos_anual["seccion"] = "anual"
    cocos_origen["seccion"] = "origen"
    pd.concat([cocos_anual, cocos_origen]).to_csv(OUT / "ine_cocos_secos.csv", index=False)

    print("Agregados escritos en", OUT)
    for f in ["ine_aceite_coco_anual.csv", "ine_aceite_coco_origen.csv",
              "ine_aceite_coco_departamento.csv", "ine_cocos_secos.csv"]:
        print(" -", f)


if __name__ == "__main__":
    main()
