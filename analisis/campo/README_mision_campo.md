# 📋 Misión de campo — los datos que faltan

El modelo de costos depende de **2 números que hoy son supuestos**. Esta carpeta
tiene las plantillas para relevarlos. Llená los CSV con lo que consigas y avisá
a Claude (o corré `python src/preparar_web.py`) para que notebook y dashboard
se actualicen con datos reales.

## Prioridad 1 — Precio del coco puesto en planta 🥥

**Plantilla:** `cotizaciones_coco.csv`

Dónde preguntar:
- **Mercado Abasto** (Santa Cruz) — puestos mayoristas de fruta
- **La Cancha** (Cochabamba) — sector frutas
- **Chapare** (Villa Tunari / Shinahota / Ivirgarzama) — productores directos al borde de la carretera
- Preguntar SIEMPRE: precio por unidad **y por ciento (100 cocos)**, si es coco seco
  (maduro, para aceite) o verde (para agua), y si pueden entregar volumen semanal.

## Prioridad 2 — Rendimiento real de tu prensa

**Plantilla:** `pruebas_rendimiento.csv`

Cuando llegue la prensa: pesá la pulpa que entra y medí el aceite que sale,
al menos 5 corridas con cocos de distinto origen. Anotá también el tiempo por
corrida (define la mano de obra real).

## Prioridad 3 — Precios de góndola que no se pudieron capturar online

**Plantilla:** `precios_gondola.csv`

En cualquier visita al súper: **Hipermaxi** (tiene BeCoco 370 ml cód. 660094 y
720 ml cód. 015550), **Ketal**, **Fidalga**, **IC Norte**. Foto del precio y a la
planilla. También sirven farmacias (Farmacorp) y tiendas naturales.

## Reglas de oro

1. Una fila por observación (aunque repitas producto en otra sucursal).
2. Siempre con **fecha** y **lugar** — los precios en Bolivia varían por ciudad.
3. Si no hay dato, dejá la celda vacía (no inventes ni promedies).
