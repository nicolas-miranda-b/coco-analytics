# Carpeta de análisis

Análisis de datos del emprendimiento de aceite de coco. El primer estudio es un
**análisis de competencia e importaciones de aceite de coco en Bolivia**.

## Contenido

| Archivo | Qué es |
|---|---|
| [`00_resumen_ejecutivo.md`](00_resumen_ejecutivo.md) | Resumen ejecutivo (lectura de 5 min) con hallazgos y recomendaciones. |
| [`01_analisis_competencia_aceite_coco.ipynb`](01_analisis_competencia_aceite_coco.ipynb) | Notebook completo: contexto global, mercado boliviano, precios, marco legal, materia prima y conclusiones, con gráficos. |
| [`02_costos_produccion.ipynb`](02_costos_produccion.ipynb) | Costos de producción y punto de equilibrio: costo variable por presentación, posición vs. competencia, sensibilidad (precio del coco y rendimiento) y comparación producir vs. envasar importado. **Paramétrico**: los supuestos se editan en la §2 y todo se recalcula. |
| [`03_plan_financiero.ipynb`](03_plan_financiero.ipynb) | Plan financiero 24 meses: inversión inicial, flujo de caja con rampa, payback, **valle de caja** (la plata real a financiar) y escenarios. Paramétrico. |
| [`04_demanda_oferta_local.ipynb`](04_demanda_oferta_local.ipynb) | Demanda (embudo de mercado direccionable, ciudades) y oferta local de coco (mapa real: **Ichilo/Warnes, no Chapare**), con las correcciones de la investigación jul-2026. |
| [`campo/`](campo/) | **Kit de misión de campo**: checklist + plantillas CSV para relevar precio del coco, rendimiento de prensa y precios de góndola. |
| [`legal/checklist_etiqueta.md`](legal/checklist_etiqueta.md) | Checklist de etiqueta NB 314001 + SENASAG (qué debe decir tu etiqueta para aprobar a la primera). |
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
| `ine_aceite_coco_anual.csv` | **Serie oficial** de importaciones de aceite de coco (2015–2026): CIF, FOB, kg, crudo/refinado | Microdato INE (vía `src/preparar_ine.py`) |
| `ine_aceite_coco_origen.csv` | **Serie oficial** por país de origen (total y 2023–2025) | Microdato INE |
| `ine_aceite_coco_departamento.csv` | **Serie oficial** por departamento de destino | Microdato INE |
| `ine_cocos_secos.csv` | Bonus: importaciones de cocos secos (0801) anual y por origen | Microdato INE |
| `importaciones_bolivia_origen.csv` | Datos espejo históricos (superados por la serie INE; se conservan como lección de datos) | OEC (reporters Ecuador/Brasil/Perú/Chile) |
| `empresas_importadoras_bolivia.csv` | Importadores bolivianos registrados en aduana (HS 1513) | Volza |
| `fuentes_oficiales_bolivia.csv` | Directorio de fuentes oficiales (INE COMEX, IBCE, etc.) con URLs y tipo de acceso | Verificación propia |
| `competencia_marcas_bolivia.csv` | Marcas/competidores en Bolivia | Relevamiento web |
| `competencia_listings_bolivia.csv` | Productos concretos con precio, tamaño y **Bs/100ml** por canal (tiendas propias, e-shops, PedidosYa, clasificados) | Relevamiento web jul-2026 |
| `competencia_senales_bolivia.csv` | Señales de venta/presencia digital (likes, seguidores, canales) | Facebook/Instagram/TikTok jul-2026 |
| `precios_bolivia.csv` | Precios de retail en Bolivia | Selina Wamucii, CaliFrut, listados |
| `marco_legal_costos.csv` | Requisitos y costos legales (SENASAG, IBNORCA, aranceles) | SENASAG, IBNORCA, AAI-2026 |

## Nota sobre los datos de Bolivia

Las cifras de importación de Bolivia usan el **microdato oficial del INE**
(620 registros aduaneros 2015–2026, partidas NANDINA de coco). El archivo fuente
`coconut_oil_imports_filtered.csv` vive en el Drive del proyecto
(**Cocoil → 11_Tamanio_de_mercado → Importaciones → processed**) y se coloca en
`data/raw/` (fuera de git). Los agregados versionados de `datos/ine_*.csv` se
regeneran con:

```bash
python src/preparar_ine.py
```

Trazabilidad, esquema del microdato y cómo actualizar cuando salgan nuevos
meses: **§3.8 del notebook**. Directorio de fuentes oficiales (INE COMEX, IBCE,
etc.): `datos/fuentes_oficiales_bolivia.csv`. Marcas y precios de retail siguen
siendo relevamiento web (direccionales).
