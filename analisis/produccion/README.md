# Registro de producción

Tres tablas: `lotes.csv` (una fila por lote de cocos, de la recepción a la pulpa), `prensados.csv` (una fila por corrida de prensa; puede juntar varios lotes, unidos por `prensado_id`) y `cocos.csv` (opcional, una fila por coco). Celdas vacías = no medido; no se inventa ni se promedia.

**IDs:** lote `L` + fecha + número del día (`L20261015-01`); prensado `P` + fecha + número (`P20261016-01`).

## Qué se mide, en el orden del proceso
| Etapa | Columnas |
| --- | --- |
| Recepción | `origen_cocos`, `proveedor`, `precio_bs_coco`, `n_cocos`, `n_cocos_malos`, `peso_cocos_kg` (enteros, sin tara) |
| Abrir y drenar | `agua_g` (pesada en balanza), `min_abrir_drenar` |
| Despulpar | `peso_pulpa_kg` (pulpa blanca, sin cáscara), `min_despulpar` |
| Triturar / rallar | `min_triturar` |
| General del lote | `personas`, `prensado_id`, `notas` |
| Secado (`prensados.csv`, se seca la pulpa ya juntada) | `peso_pulpa_seca_kg`, `secado_metodo`, `secado_temp_c`, `secado_min` |
| Prensado (`prensados.csv`) | `lotes`, `metodo` (`seco`: pulpa secada y prensada; `húmedo-fermentación`: pulpa remojada, leche fermentada y decantada), `n_cocos`, `peso_pulpa_kg`, `min_prensado`, `temp_max_aceite_c`, `leche_g` (lo que sale de la prensa hidráulica al prensar pulpa fresca: emulsión de aceite y agua), `aceite_bruto_ml` (si sale aceite directo, con pulpa seca), `torta_g` |
| Decantado 24 h y filtrado (`prensados.csv`) | `aceite_filtrado_ml` (el aceite separado de la leche, ya filtrado) |

Prensa: hidráulica de 20 t con jaula perforada de acero inoxidable.

## Indicadores que salen de aquí
- Cocos por litro (meta ≤ 15) = `n_cocos` / `aceite_filtrado_ml` × 1000
- ml de aceite por coco y % de aceite sobre pulpa (densidad del aceite ≈ 0,92 g/ml)
- Agua de coco por coco (subproducto vendible)
- Minutos por litro (mano de obra) y costo de coco por litro
- Pulpa seca / pulpa fresca (agua evaporada en el secado)
- Merma del filtrado = 1 − filtrado / bruto
