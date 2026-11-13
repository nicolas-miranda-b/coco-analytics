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
| Menos de US$ 2/kg | 10 | 135,9 | 48 % | 0,95 | 10 | Contenedores de 9–25 t de Sri Lanka a Cochabamba, a US$ 0,46–1,33/kg. Está por debajo del precio mundial del aceite de coco crudo (US$ 1,5–3,0/kg CIF Rotterdam en 2024–2025). No es extra virgen: es insumo industrial, o está subvaluado o mal clasificado. |
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
- Sobre eso se paga 20 % de arancel (0 % desde Brasil y otros con preferencia) e IVA.
- Pendiente: el peso desde 2021 viene en la columna `KILOS`; si es peso bruto con frasco de vidrio, el costo por litro de aceite envasado es mayor que el calculado.
