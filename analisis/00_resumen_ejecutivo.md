# Resumen ejecutivo — Aceite de coco en Bolivia (análisis de competencia)

*Julio 2026 · coco-analytics · Documento de acompañamiento del notebook `01_analisis_competencia_aceite_coco.ipynb`*

> ⚠️ **Calidad de datos.** Bolivia es un actor muy pequeño en el comercio mundial de aceite de coco, así que sus cifras de importación no se publican de forma limpia. Los números de Bolivia provienen de *datos espejo* (lo que los países exportadores declaran haber enviado a Bolivia) y de relevamiento de precios/marcas en retail. Son **direccionales, no auditados**. Cada dato lleva su fuente en `datos/*.csv`.

---

## 1. En una frase

El aceite de coco en Bolivia es un **producto premium de nicho** (virgen/extra virgen, salud y belleza), con un mercado pequeño (~US$ 0,8–1,5 M/año importados), donde la competencia son sobre todo **pequeños productores locales** y algo de importación regional vía **Ecuador** — con una **barrera legal de entrada baja** y una **ventana arancelaria (DS 5516)** para importar equipo con 0 % este 2026.

## 2. Contexto global — de dónde viene y cuánto vale

- Comercio mundial (HS 1513): **~US$ 7,95 mil millones en 2024** (+20 % vs 2023, **por precio, no por volumen**).
- Exportadores: **Indonesia (35 %)**, **Filipinas (23 %)**, **Malasia (16 %)**. Países Bajos figura alto pero es **re-exportador**, no productor.
- Importadores: **EE.UU.**, **China**, **Países Bajos** (hub UE).
- Precio: **máximo histórico ~US$ 3.000/tonelada** en 2025 (casi el triple que en 2024), por El Niño/La Niña y demanda creciente.

## 3. Bolivia — el mercado y la competencia

| Dimensión | Hallazgo |
|---|---|
| Tamaño | Nicho: ~US$ 0,8–1,5 M/año importados; no aparece en rankings de OEC. |
| Origen importado | **Ecuador** dominante (~US$ 765k en 2023, 5º destino de Ecuador, flujo creciente); Brasil **< US$ 249k/año**, Perú **< US$ 678k/año** (cotas), Chile ~0. ⚠️ Parte del flujo 1513 puede ser **palmiste**, no coco. |
| Importadores directos | **DREAMCO SRL** (~25 % de los envíos), **ANTORVA S.R.L** (~11 %), **HANSA LTDA** (~9 %) — registros aduaneros vía Volza. |
| Competencia | Marcas **locales/artesanales**: Becoco, Madre Tierra, Dream Cos, Viasana. 💡 DREAMCO SRL ≈ marca "Dream Cos": el principal competidor "local" probablemente **importa**, no produce → el posicionamiento "coco boliviano" está **vacante**. |
| Canal | Tiendas naturales, e-commerce, redes. Supermercados (Ketal/Hipermaxi/Fidalga) esporádicamente. |
| Precio | Premium: **~Bs 15–28 / 100 ml**, unas **5–20×** el aceite de cocina común (soya FINO ~Bs 14/L). |
| Exportaciones BO | Bolivia **no exporta** partida 1513 (no figura en ningún ranking exportador). |

## 4. Marco legal (producir y vender en Bolivia)

- **SENASAG — Registro sanitario** obligatorio. Costo por 2 años: Industrial **Bs 1.600** · Semi-industrial **Bs 1.000** · **Artesanal Bs 500**. Incluye visita a planta y análisis de muestras.
- **Etiquetado:** **NB 314001:2015** (IBNORCA) + aprobación del modelo de etiqueta por SENASAG.
- **Importación (tu competencia):** GA **~10 %** (confirmar en AAI-2026) + **IVA 14,94 %**; el ICE no aplica.
- 🎯 **DS 5516 (Arancel Cero 2026):** **0 % de arancel** para maquinaria/equipo agroalimentario hasta el **31-dic-2026** → importá tu prensa/embotelladora con arancel cero este año.

## 5. Materia prima local

Hay coco en Bolivia (**Santa Cruz, Chapare, Beni, Pando**) pero a **escala modesta** y orientado a fruta/agua de coco, no a aceite. Asegurar suministro local de nuez/copra es el **cuello de botella** y la clave para sostener la ventaja "hecho en Bolivia".

## 6. Recomendaciones

1. **Posicionamiento premium/salud-belleza**, no cocina masiva.
2. **Diferenciación "producido en Bolivia con coco boliviano"**: el hallazgo DREAMCO sugiere que ese posicionamiento está **vacante** — el principal competidor "local" probablemente importa.
3. **Asegurar materia prima local primero** (Santa Cruz/Chapare/Beni).
4. **Usar el DS 5516 este año** para importar equipo con 0 % de arancel.
5. **Registro SENASAG desde el inicio** (arrancar como *artesanal*, Bs 500).
6. **Bajar la serie oficial del INE**: sistema COMEX (`http://web3.ine.gob.bo:8082/comex/Main`), partidas NANDINA **1513.11.00 / 1513.19.00** por año y origen. La §3.5 del notebook trae la receta paso a paso y una celda que integra el archivo automáticamente. Confirmar también el GA exacto (AAI-2026) y la identidad DREAMCO ↔ Dream Cos.

## 7. Sobre la serie oficial del INE

Los datos oficiales de importación **existen y son gratuitos**, pero requieren consulta manual (el entorno de esta sesión no puede acceder a ellos por restricciones de red): **INE COMEX** (consulta NANDINA interactiva), **INE importaciones** (Excel), portal **COMEX de Producción** (data-bolivia.produccion.gob.bo), anuarios **IBCE** (PDF) y **TrendEconomy** (serie 2012–2023 base Comtrade). URLs completas en `datos/fuentes_oficiales_bolivia.csv` y en la §3.5 del notebook.

---

*Fuentes principales: OEC, PCA, Banco Mundial, ICC, SENASAG, IBNORCA, IBCE/INE Bolivia, Selina Wamucii, relevamiento de retail. Detalle y URLs en el notebook y en `datos/*.csv`.*
