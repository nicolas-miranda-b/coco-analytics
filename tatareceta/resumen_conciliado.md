# TataReceta — Resumen Conciliado del Proyecto

> Este documento unifica los dos resúmenes previos del proyecto:
> **"Resumen del Proyecto (Ecoreceta, nombre descartado)"** y
> **"Resumen Ejecutivo del Proyecto Startup – TataReceta"**.
> Donde coinciden, se consolida; donde difieren, se toma una decisión y se deja
> registrada; lo que queda abierto está en la sección final.

---

## 1. Identidad y visión

- **Nombre:** TataReceta. (El documento anterior indicaba "nombre por definir" y
  descartaba explícitamente "Ecoreceta"; el documento más reciente ya adopta
  TataReceta, que cumple los criterios de marca definidos: confianza, salud,
  simplicidad, sin confrontar a médicos, laboratorios ni farmacias.)
- **Visión:** construir una plataforma nacional de inteligencia farmacéutica
  basada en IA, que conecte pacientes, empresas y farmacias, empezando como un
  asistente inteligente por WhatsApp.

## 2. Problema (fusión de ambos enfoques)

Los dos documentos describen dos caras del mismo dolor:

1. **Asimetría de información (doc. Ecoreceta):** los pacientes reciben recetas
   con marcas comerciales y no saben que existen alternativas equivalentes
   (mismo principio activo, concentración y forma farmacéutica) más económicas.
2. **Fricción y tiempo (doc. TataReceta):** los usuarios pierden tiempo
   consultando varias farmacias, interpretando recetas y buscando
   disponibilidad; muchas de esas consultas ya empiezan por WhatsApp.

**Formulación conciliada:** comprar medicamentos en Bolivia es caro y engorroso
porque el paciente no sabe qué equivalentes existen, cuánto cuestan ni dónde
están disponibles — y no tiene un canal simple para averiguarlo.

## 3. Propuesta de valor (conciliada)

Un **asistente por WhatsApp** al que el usuario envía la foto de su receta o el
nombre del medicamento, y recibe de forma organizada:

- el **principio activo** y las **alternativas equivalentes** (misma
  concentración y forma farmacéutica),
- **precios comparados** y **farmacias donde encontrarlas**,
- todo **sin reemplazar el criterio médico** (punto en el que ambos documentos
  coinciden explícitamente: la IA asiste, no recomienda tratamientos).

Decisión de conciliación: el **núcleo diferenciador es el ahorro vía
equivalencias** (motor de normalización del doc. Ecoreceta); la **conveniencia
conversacional** (doc. TataReceta) es el empaque y el canal. El gancho de
adquisición es "paga menos por el mismo medicamento"; la retención viene de la
comodidad del asistente.

## 4. Canal

Coincidencia total entre ambos documentos:

- **WhatsApp primero** (menor barrera de entrada en el mercado boliviano; se
  evita el costo y la fricción de una app móvil en etapas tempranas).
- **Web** solo como panel administrativo, dashboard para empresas/farmacias y
  página institucional.

## 5. Cliente objetivo

(Solo el doc. TataReceta segmenta; se adopta su definición.)

- **Etapa 1:** padres y madres de familia y personas que compran medicamentos
  de forma recurrente para familiares.
- **Etapa 2:** pacientes crónicos y público general.
- **En paralelo (del doc. Ecoreceta):** empresas (beneficio para colaboradores)
  y farmacias como clientes B2B.

## 6. Modelo de negocio (consolidado)

| Línea | Descripción | Fuente |
|---|---|---|
| **B2C** | Suscripción de **Bs 6–9/mes** por consultas ilimitadas por WhatsApp, cobrada por QR. | Ambos documentos (coinciden en el precio) |
| **B2B Empresas** | Planes corporativos como beneficio de salud y ahorro para colaboradores. | Doc. Ecoreceta (se mantiene) |
| **B2B Farmacias** | Dos variantes propuestas que hay que reconciliar en la validación: (a) tablets/pantallas en farmacias aliadas que muestran equivalentes **solo del stock de esa farmacia**, con instalación + mensualidad de **Bs 500–1.000 por sucursal** (doc. Ecoreceta); (b) generación de clientes, automatización y servicios premium (doc. TataReceta). | Ambos — **no son excluyentes**: (b) es el valor que se vende, (a) es un formato/pricing concreto. Validar ambos en el piloto con farmacias. |

⚠️ **Tensión a vigilar:** el B2C promete "dónde está más barato" y el B2B
farmacias limita resultados al stock de la farmacia aliada. El doc. Ecoreceta ya
lo resuelve parcialmente (la tablet solo compara dentro de esa farmacia), pero
hay que cuidar que el canal B2C no pierda neutralidad al firmar alianzas.

## 7. Datos y ventaja competitiva

(Definidos solo en el doc. Ecoreceta; se adoptan íntegros.)

- **Base regulatoria:** AGEMED (registro sanitario, principio activo,
  concentración, forma farmacéutica).
- **Precios:** Farmacorp, Farmacias Chávez, Hipermaxi, PedidosYa y otras fuentes.
- **Ventaja competitiva:** un **motor de normalización** que identifica
  equivalencias correctas entre marcas distintas y compara precios reales. La
  "IA de clasificación y asistencia" del doc. TataReceta es la capa
  conversacional sobre ese motor — son complementarios, no alternativas.

## 8. Estrategia de validación y roadmap (fusionados)

Ambos documentos siguen Customer Development (Steve Blank): **validar antes de
construir, invertir solo con tracción real**. Roadmap unificado:

1. **Descubrimiento del cliente** — entrevistas: **≥30 usuarios/pacientes, 10
   farmacias, 5 profesionales de salud** (metas del doc. TataReceta) **+
   empresas** (segmento del doc. Ecoreceta).
2. **Landing + MVP manual** — WhatsApp Business operado a mano, cobros por QR,
   registro interno de consultas. Objetivo: validar dolor, disposición de pago
   y recurrencia.
3. **Pilotos pagados** — usuarios B2C, **1 farmacia** y **1 empresa**.
4. **Automatización parcial** — backend y base de datos (ver §9).
5. **Producto beta escalable.**
6. **Inversión** — solo después de demostrar métricas reales y clientes pagando.

## 9. Arquitectura futura

(Del doc. TataReceta; consistente con el doc. Ecoreceta.)

WhatsApp Cloud API · backend Python (FastAPI) · PostgreSQL · motor de IA
(normalización de equivalencias + clasificación/asistencia) · panel
administrativo web · integración de pagos (QR) · analítica.

## 10. Indicadores clave

Usuarios que pagan · tasa de conversión · retención mensual · consultas
atendidas · tiempo de respuesta · farmacias aliadas · empresas cliente ·
ingresos recurrentes mensuales (MRR). *(Lista del doc. TataReceta + "empresas
cliente" por el segmento B2B empresas del doc. Ecoreceta.)*

## 11. Riesgos y mitigación

- Baja disposición de pago · confianza del usuario · adopción por farmacias ·
  complejidad operativa (doc. TataReceta).
- **Adicionales implícitos del doc. Ecoreceta:** calidad/actualización de los
  datos de AGEMED y precios; sensibilidad regulatoria y relación con médicos,
  laboratorios y farmacias (la marca y el mensaje deben evitar la confrontación).
- **Mitigación:** validar manualmente antes de automatizar; iterar rápido;
  posicionarse como aliado del ecosistema, no como competidor.

## 12. Decisiones abiertas (a resolver antes o durante la validación)

1. **Pitch principal B2C:** liderar con "ahorra en tus medicamentos"
   (equivalencias) — recomendado — o con "tu asistente de farmacia" (conveniencia).
2. **B2B farmacias:** validar en el piloto cuál formato monetiza mejor —
   tablet/pantalla con mensualidad (Bs 500–1.000/sucursal) vs. servicios de
   generación de clientes/automatización — o una combinación.
3. **Neutralidad vs. alianzas:** definir la política de cómo se muestran las
   farmacias aliadas en el canal B2C sin sesgar la comparación de precios.
4. **Alcance del MVP manual:** ¿incluye ya la comparación de equivalencias
   (buscada a mano en AGEMED/listas de precios) o solo disponibilidad y precio
   del medicamento recetado? Recomendado: incluirla, porque es el diferenciador
   que se quiere validar.
