# Resumen ejecutivo — Aceite de coco en Bolivia (análisis de competencia)

*Julio 2026 · coco-analytics · Documento de acompañamiento del notebook `01_analisis_competencia_aceite_coco.ipynb`*

> ✅ **Calidad de datos.** Las cifras de importación de Bolivia provienen del **microdato oficial del INE** (registros aduaneros 2015–2026, partidas NANDINA de coco), aportado desde el Drive del proyecto (Cocoil → 11_Tamanio_de_mercado → Importaciones). Marcas y precios de retail son relevamiento web (direccionales). Cada dato lleva su fuente en `datos/*.csv`.

---

## 1. En una frase

El aceite de coco en Bolivia es un **producto premium de nicho** (importa **US$ 150–300 mil CIF y 40–100 t/año**, con volumen en crecimiento y récord de ~104 t en 2025), que llega **de Asia y de hubs europeos** — la competencia son pequeños jugadores locales e importadores directos como DREAMCO — con una **barrera legal de entrada baja** y una **ventana arancelaria (DS 5516)** para importar equipo con 0 % este 2026.

## 2. Contexto global — de dónde viene y cuánto vale

- Comercio mundial (HS 1513): **~US$ 7,95 mil millones en 2024** (+20 % vs 2023, **por precio, no por volumen**).
- Exportadores: **Indonesia (35 %)**, **Filipinas (23 %)**, **Malasia (16 %)**. Países Bajos figura alto pero es **re-exportador**, no productor.
- Importadores: **EE.UU.**, **China**, **Países Bajos** (hub UE).
- Precio: **máximo histórico ~US$ 3.000/tonelada** en 2025 (casi el triple que en 2024), por El Niño/La Niña y demanda creciente.

## 3. Bolivia — el mercado y la competencia

| Dimensión | Hallazgo (microdato oficial INE) |
|---|---|
| Tamaño | Nicho: **US$ 150–300 mil CIF y 40–100 t/año** recientes; pico atípico 2023 (US$ 977 mil). **Volumen creciendo**: récord ~104 t en 2025. Refinado = ~88 %. |
| Origen importado | **Sri Lanka** (volumen, ~$1,6–2,8/kg), **Malasia** (premium ~$44/kg, explicó el pico 2023), **Países Bajos/Alemania** (re-export UE). **Ecuador ≈ US$ 16**: el dato espejo de $765k era palmiste, no coco. |
| Dónde está el mercado | **Santa Cruz ~63 %**, Cochabamba ~27 %, La Paz ~8 % del valor importado. |
| Importadores directos | **DREAMCO SRL** (~25 % de los envíos), **ANTORVA S.R.L** (~11 %), **HANSA LTDA** (~9 %) — registros aduaneros vía Volza. |
| Competencia | Marcas **locales/artesanales**: Becoco, Madre Tierra, Dream Cos, Viasana. 💡 DREAMCO SRL ≈ marca "Dream Cos": el principal competidor "local" probablemente **importa**, no produce → el posicionamiento "coco boliviano" está **vacante**. |
| Materia prima | Bolivia importa **más cocos secos (US$ 4,9 M acum.) que aceite (US$ 2,3 M)** — de Indonesia/Malasia/Vietnam. Hasta el insumo es importado. |
| Canal | Tiendas naturales, e-commerce, redes. Supermercados (Ketal/Hipermaxi/Fidalga) esporádicamente. |
| Precio | CIF granel **US$ 2,6–5/kg** vs retail **~US$ 29/L** → **markup de cadena 6–10×**. Retail premium: ~Bs 15–28/100 ml. |
| Exportaciones BO | Bolivia **no exporta** partida 1513 (no figura en ningún ranking exportador). |

## 4. Marco legal (producir y vender en Bolivia)

- **SENASAG — Registro sanitario** obligatorio. Costo por 2 años: Industrial **Bs 1.600** · Semi-industrial **Bs 1.000** · **Artesanal Bs 500**. Incluye visita a planta y análisis de muestras.
- **Etiquetado:** **NB 314001:2015** (IBNORCA) + aprobación del modelo de etiqueta por SENASAG.
- **Importación (tu competencia):** GA **~10 %** (confirmar en AAI-2026) + **IVA 14,94 %**; el ICE no aplica.
- 🎯 **DS 5516 (Arancel Cero 2026):** **0 % de arancel** para maquinaria/equipo agroalimentario hasta el **31-dic-2026** → importá tu prensa/embotelladora con arancel cero este año.

## 5. Materia prima local

Hay coco en Bolivia (**Santa Cruz, Chapare, Beni, Pando**) pero a **escala modesta** y orientado a fruta/agua de coco, no a aceite. Asegurar suministro local de nuez/copra es el **cuello de botella** y la clave para sostener la ventaja "hecho en Bolivia".

## 6. Recomendaciones

1. **Posicionamiento premium/salud-belleza**, no cocina masiva. El markup CIF→góndola (6–10×) muestra dónde está el margen.
2. **Diferenciación "producido en Bolivia con coco boliviano"**: DREAMCO (mayor importador) ≈ marca Dream Cos, y hasta la materia prima del mercado es importada — ese posicionamiento está **vacante**.
3. **Empezar por Santa Cruz y Cochabamba** (~90 % del mercado importado, y las zonas con coco local).
4. **Asegurar materia prima local** (Santa Cruz/Chapare/Beni) — los competidores la resuelven importando de Asia.
5. **Usar el DS 5516 este año** (equipo con 0 % de arancel) y **registro SENASAG desde el inicio** (*artesanal*, Bs 500).
6. **Dimensionar bien el plan**: 40–100 t/año importadas es un nicho chico pero **en crecimiento** (récord 2025). El plan debe capturar una parte + crear demanda nueva. Pendientes: GA exacto (AAI-2026) e identidad DREAMCO ↔ Dream Cos.

## 7. Sobre la serie oficial del INE (integrada ✅)

El análisis usa el **microdato oficial del INE** (620 registros aduaneros 2015–2026, partidas NANDINA de coco), que vive en el Drive del proyecto (**Cocoil → 11_Tamanio_de_mercado → Importaciones → processed**). Los agregados se regeneran con `python src/preparar_ine.py` y la trazabilidad completa está en la **§3.8 del notebook**. Directorio de fuentes oficiales para actualizaciones: `datos/fuentes_oficiales_bolivia.csv`.

---

*Fuentes principales: OEC, PCA, Banco Mundial, ICC, SENASAG, IBNORCA, IBCE/INE Bolivia, Selina Wamucii, relevamiento de retail. Detalle y URLs en el notebook y en `datos/*.csv`.*
