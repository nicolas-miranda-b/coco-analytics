# Valor de importación del aceite de coco: verificación del 12-nov-2026

Pregunta: ¿cuánto cuesta en aduana un litro de aceite de coco extra virgen importado?

## 1. Corrección de la base
- En el microdato del INE, `FRO` es el CIF frontera en US$ y `FOB` el FOB en US$. `ADU` es el CIF en bolivianos (ADU/FRO = 6,96). `PAG` es el gravamen arancelario pagado en bolivianos: 20 % de `ADU` en 125 de 178 despachos y 0 en los 36 con preferencia MERCOSUR/CAN.
- `src/preparar_ine.py` y `src/preparar_web.py` sumaban `PAG` como si fuera CIF en US$. Eso inflaba el valor ~39 %. Ya usan `FRO`.
- Cruce con la segunda fuente oficial: 2024 da US$ 114.921 CIF y 44,2 t con `FRO`; UN Comtrade / WITS (Bolivia como reportante) da US$ 115 mil.

| Año | t | CIF US$ | US$/kg |
|---|---|---|---|
| 2023 | 76,1 | 706.190 | 9,29 |
| 2024 | 44,2 | 114.921 | 2,60 |
| 2025 | 104,2 | 218.756 | 2,10 |

## 2. La aduana no distingue el extra virgen
La NANDINA solo tiene dos líneas: 1513.11.00.00 "aceite en bruto" y 1513.19.00.00 "los demás". El microdato no trae descripción comercial, marca ni importador. El aceite virgen puede entrar por cualquiera de las dos.

## 3. Lectura por despacho (2021 a abril de 2026, despachos de 20 kg o más)
| Tramo de valor CIF | Despachos | t | % del volumen | US$/kg | Bs/litro a 11,70 | Qué es |
|---|---|---|---|---|---|---|
| Menos de US$ 2/kg | 10 | 135,9 | 48 % | 0,95 | 10 | Contenedores de 9–25 t de Sri Lanka a Cochabamba, a US$ 0,46–1,33/kg. No es extra virgen. Los despachos de 2023 y 2024 (US$ 1,26–1,96/kg) son compatibles con aceite convencional para industria: el precio mundial fue US$ 1,08/kg en 2023 y US$ 1,52/kg en 2024 (Banco Mundial, CFR noroeste de Europa). Los de 2025 (US$ 0,46–1,02/kg) están muy por debajo del precio mundial de ese año (US$ 2,48/kg): subvaluación, error de peso u otro producto. |
| US$ 2 a 5/kg | 19 | 109,0 | 39 % | 3,70 | 40 | Lotes de 0,6–14 t de Países Bajos, Alemania, Sri Lanka y EE. UU. Granel de calidad (virgen o refinado orgánico); no se puede separar. |
| US$ 5/kg o más | 35 | 18,8 | 7 % | 7,00 | 75 | Lotes chicos, casi todos de menos de 1 t: Brasil a Santa Cruz (US$ 6,4–10,9), EE. UU. a Cochabamba (US$ 5,3–6,8), Sri Lanka, India, Vietnam, España. Producto envasado para góndola. |
| Malasia 2023 | 4 | 18,4 | 7 % | 31,62 | 340 | Atípico; no es aceite de coco común. |

Bs/litro = US$/kg × 0,92 kg/L × 11,70 (dólar oficial BCB del 12-nov-2026).

## 4. Referencia internacional del virgen
- Sri Lanka, valor unitario de exportación de VCO: Rs 1.176,73/kg (ene–nov 2024) y Rs 1.900,86/kg (ene–nov 2025). A ~300 rupias por dólar son ≈ US$ 3,9 y ≈ US$ 6,3 por kg (conversión propia). Fuente: Nutioils, white paper de enero de 2026.
- Precio EXW de VCO, octubre de 2026: Filipinas US$ 3,01/kg, Sri Lanka US$ 3,85/kg, India US$ 4,10/kg. Fuente: Procurement Resource.

## 5. Conclusión
- Extra virgen a granel puesto en frontera: US$ 3,5–6,5/kg, unos Bs 38–70 por litro.
- Extra virgen envasado puesto en frontera: US$ 6–10/kg, unos Bs 65–110 por litro. Es la referencia para las marcas de góndola.
- Sobre eso se paga el gravamen arancelario e IVA. El gravamen era 20 % (es lo que muestra `PAG` en la base). El DS 5646 lo bajó 5 puntos, a 15 %, desde el 6-jul-2026 y hasta el 31-dic-2027. Con preferencia de origen (Brasil y otros) es 0 %.
- Pendiente: el peso desde 2021 viene en la columna `KILOS`; si es peso bruto con frasco de vidrio, el costo por litro de aceite envasado es mayor que el calculado.

## 6. Contraste con una investigación independiente (ChatGPT, 12-nov-2026)
- **Valores: coinciden al dólar.** WITS / UN Comtrade da US$ 114.930 en 2024 y US$ 218.760 en 2025, y los mismos montos por origen y subpartida que el microdato con `FRO` (por ejemplo, 2024 "los demás": Sri Lanka 44.750, Países Bajos 37.670). Confirma que `FRO` es la columna correcta.
- **Kilos: no usar los de WITS.** WITS reporta 52,2 t en 2024 y 76,7 t en 2025, contra 44,2 t y 104,2 t del microdato. En WITS todos los orígenes de una subpartida tienen el mismo valor unitario (US$ 2,04/kg en 2024, US$ 2,68/kg en 2025), señal de que las cantidades están imputadas. El microdato trae el peso de cada despacho.
- **Malasia 2023: el peso es dudoso.** El valor coincide (FOB US$ 546 mil en el INE; Malasia declara US$ 539 mil exportados), pero el peso no: 18,4 t en el INE, 76,5 t según Malasia, 274 t en WITS. El valor unitario queda entre US$ 7 y US$ 32/kg según la fuente. Sigue siendo atípico y es una alerta sobre la calidad del campo de peso.
- **Referencias de precio del virgen que aportó:** Filipinas exportó 29.337 t de VCO en 2023 por US$ 76,8 M (US$ 2,62/kg, UCAP); el CBI usa ~€3/kg FOB para VCO de Sri Lanka a granel en 2024.
- **Su estimación CIF Bolivia:** granel US$ 4–6/kg (Bs 43–65 por litro); envasado US$ 5,5–8/kg (Bs 59–86 por litro). Es una triangulación de precios internacionales, no datos de despachos.
- **Rango en que coinciden las dos lecturas:** extra virgen envasado US$ 6–8/kg en frontera, Bs 65–86 por litro; granel US$ 4–6/kg, Bs 43–65 por litro. Los despachos chicos de Brasil llegan hasta US$ 10,9/kg.
- **Objeción válida:** un valor unitario alto no prueba que el producto venga envasado. Que el tramo de US$ 5/kg o más sea producto de góndola es una inferencia (lotes chicos, Brasil a Santa Cruz, marcas brasileñas en góndola), no un dato.
