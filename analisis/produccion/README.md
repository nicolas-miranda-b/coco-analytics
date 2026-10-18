# Registro de producción

Tres tablas: `lotes.csv` (una fila por lote de cocos, de la recepción a la pulpa), `prensados.csv` (una fila por corrida de prensa; puede juntar varios lotes, unidos por `prensado_id`) y `cocos.csv` (opcional, una fila por coco). Celdas vacías = no medido; no se inventa ni se promedia.

**IDs:** lote `L` + fecha + número del día (`L20261015-01`); prensado `P` + fecha + número (`P20261016-01`).

## Recepción de cocos (según APCC y manual FAO de VCO, en el Drive)
- Solo cocos **completamente maduros: 12–13 meses desde la polinización**. Señales: cáscara y estopa marrones (no verdes) y que suene el agua al sacudirlos.
- Rechazar cocos **germinados o con haustorio** (la esponja blanca interna): desde que se forma, baja el contenido de aceite.
- Procesar **dentro de los 7 días desde la cosecha**; no dejarlos al sol. Anotar `fecha_cosecha` cuando el proveedor la sepa.
- La fermentación es muy sensible a la madurez: el coco inmaduro tiene más proteína y el aceite cuesta más en separarse.
- Fermentación (FAO): 35–40 °C, 16–24 h, recipiente tapado con tela o tapa suelta, sin restos de jabón. Segunda extracción: torta y agua 2:1, volver a prensar y mezclar las dos leches.

## Qué se mide, en el orden del proceso
| Etapa | Columnas |
| --- | --- |
| Recepción | `origen_cocos`, `proveedor`, `fecha_cosecha`, `precio_bs_coco`, `n_cocos`, `n_cocos_malos`, `peso_cocos_kg` (enteros, sin tara) |
| Abrir y drenar | `agua_g` (pesada en balanza), `min_abrir_drenar` |
| Despulpar | `peso_pulpa_kg` (pulpa blanca, sin cáscara), `min_despulpar` |
| Triturar / rallar | `min_triturar` |
| General del lote | `personas`, `prensado_id`, `notas` |
| Secado (`prensados.csv`, se seca la pulpa ya juntada) | `peso_pulpa_seca_kg`, `secado_metodo`, `secado_temp_c`, `secado_min` |
| Prensado (`prensados.csv`) | `lotes`, `metodo`, `agua_agregada_ml` (agua sumada a la pulpa antes de prensar) (`seco`: pulpa secada y prensada; `húmedo-fermentación`: pulpa remojada, leche fermentada y decantada), `n_cocos`, `peso_pulpa_kg`, `min_prensado`, `temp_max_aceite_c`, `leche_g` (lo que sale de la prensa hidráulica al prensar pulpa fresca: emulsión de aceite y agua), `aceite_bruto_ml` (si sale aceite directo, con pulpa seca), `torta_g` |
| Fermentación (`prensados.csv`) | `ferm_inicio`, `ferm_fin` (fecha y hora), `ferm_lugar` |
| Decantado y filtrado (`prensados.csv`) | `aceite_filtrado_ml` (el aceite separado de la leche, ya filtrado) |

Prensa: hidráulica de 20 t con jaula perforada de acero inoxidable.

## Indicadores que salen de aquí
- Cocos por litro (meta ≤ 15) = `n_cocos` / `aceite_filtrado_ml` × 1000
- ml de aceite por coco y % de aceite sobre pulpa (densidad del aceite ≈ 0,92 g/ml)
- Agua de coco por coco (subproducto vendible)
- Minutos por litro (mano de obra) y costo de coco por litro
- Leche extraída ≈ pulpa + agua agregada − torta
- Merma del filtrado = 1 − filtrado / bruto
