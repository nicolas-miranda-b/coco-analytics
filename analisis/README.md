# Carpeta de análisis

Análisis de datos del emprendimiento de aceite de coco. El primer estudio es un
**análisis de competencia e importaciones de aceite de coco en Bolivia**.

## Contenido

| Archivo | Qué es |
|---|---|
| [`00_resumen_ejecutivo.md`](00_resumen_ejecutivo.md) | Resumen ejecutivo (lectura de 5 min) con hallazgos y recomendaciones. |
| [`01_analisis_competencia_aceite_coco.ipynb`](01_analisis_competencia_aceite_coco.ipynb) | Notebook completo: contexto global, mercado boliviano, precios, marco legal, materia prima y conclusiones, con gráficos. |
| `datos/` | Datasets curados en CSV, cada uno con su columna de **fuente**. |
| `figuras/` | Gráficos exportados por el notebook (PNG). |

## Cómo ejecutar el notebook

```bash
# desde la raíz del repo
pip install -r requirements.txt
cd analisis
jupyter nbconvert --to notebook --execute --inplace 01_analisis_competencia_aceite_coco.ipynb
# o abrilo en Jupyter:  jupyter lab
```

El notebook lee los CSV de `datos/`, usa el estilo de gráficos de `../src/estilo.py`
y guarda las figuras en `figuras/`.

## Datasets (`datos/`)

| CSV | Contenido | Fuente principal |
|---|---|---|
| `valor_mundial_por_anio.csv` | Valor mundial de exportación (2018–2024) | OEC / IndexBox |
| `exportadores_mundo_2024.csv` | Top países exportadores + participación | OEC |
| `importadores_mundo_2024.csv` | Top países importadores | OEC |
| `precios_internacionales.csv` | Precio internacional (USD/t) por período | TM Duché, ICC, Banco Mundial |
| `empresas_exportadoras.csv` | Principales empresas exportadoras/procesadoras | Tendata, Mordor |
| `filipinas_destinos_2024.csv` | Destinos de exportación de Filipinas | PCA |
| `importaciones_bolivia_origen.csv` | Origen de importaciones de Bolivia (datos espejo) | OEC (reporters Ecuador/Brasil) |
| `competencia_marcas_bolivia.csv` | Marcas/competidores en Bolivia | Relevamiento web |
| `precios_bolivia.csv` | Precios de retail en Bolivia | Selina Wamucii, CaliFrut, listados |
| `marco_legal_costos.csv` | Requisitos y costos legales (SENASAG, IBNORCA, aranceles) | SENASAG, IBNORCA, AAI-2026 |

## Nota sobre los datos de Bolivia

Bolivia es un actor muy pequeño en el comercio mundial de aceite de coco; sus
cifras de importación no se publican de forma limpia en los agregadores. Los
números de Bolivia son **direccionales** (datos espejo + relevamiento de retail),
no auditados. Para una serie exacta conviene comprar/pulir los datos NANDINA
1513.11 / 1513.19 por año y origen en INE/IBCE/Aduana o en Veritrade/Nosis.
