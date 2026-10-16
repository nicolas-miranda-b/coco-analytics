# Registro de producción

Una fila por lote en `lotes.csv` y una fila por coco en `cocos.csv` (opcional, cuando se pesa coco por coco). Celdas vacías = no medido; no se inventa ni se promedia.

**ID de lote:** `L` + fecha + número del día (`L20261015-01`).

## Qué se mide, en el orden del proceso
| Etapa | Columnas |
| --- | --- |
| Recepción | `origen_cocos`, `proveedor`, `precio_bs_coco`, `n_cocos`, `n_cocos_malos`, `peso_cocos_kg` (enteros, sin tara) |
| Abrir y drenar | `agua_ml`, `min_abrir_drenar` |
| Despulpar | `peso_pulpa_kg` (pulpa blanca, sin cáscara), `min_despulpar` |
| Triturar / rallar | `min_triturar` |
| Secado (si se seca antes de prensar) | `peso_pulpa_seca_kg`, `secado_metodo`, `secado_temp_c`, `secado_min` |
| Prensado | `min_prensar`, `temp_max_aceite_c`, `aceite_bruto_ml`, `torta_g` |
| Decantado 24 h y filtrado | `aceite_filtrado_ml` |
| General | `personas`, `notas` |

## Indicadores que salen de aquí
- Cocos por litro (meta ≤ 15) = `n_cocos` / `aceite_filtrado_ml` × 1000
- ml de aceite por coco y % de aceite sobre pulpa (densidad del aceite ≈ 0,92 g/ml)
- Agua de coco por coco (subproducto vendible)
- Minutos por litro (mano de obra) y costo de coco por litro
- Merma del filtrado = 1 − filtrado / bruto
