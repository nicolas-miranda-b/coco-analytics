# TataReceta — Backend

Asistente por WhatsApp para encontrar **medicamentos equivalentes** (mismo
principio activo, concentración y forma farmacéutica) al mejor precio, sin
reemplazar el criterio médico. Ver [`resumen_conciliado.md`](resumen_conciliado.md)
para la visión completa del proyecto.

## Arquitectura

```
tatareceta/
├── app/
│   ├── main.py              # Aplicación FastAPI
│   ├── config.py            # Configuración por variables de entorno
│   ├── db.py                # SQLite (dev) / PostgreSQL (prod)
│   ├── modelos.py           # Medicamento, Farmacia, Precio, Usuario, Consulta
│   ├── esquemas.py          # Esquemas Pydantic del panel admin
│   ├── whatsapp.py          # Cliente WhatsApp Cloud API (simulado sin token)
│   ├── motor/
│   │   ├── normalizacion.py # ⭐ Núcleo: texto libre → consulta estructurada
│   │   ├── equivalencias.py # Búsqueda de equivalentes + comparación de precios
│   │   └── ocr.py           # Lectura de recetas por foto (visión de Claude)
│   ├── importadores/
│   │   ├── agemed.py        # Importador del registro sanitario de AGEMED
│   │   ├── precios.py       # Importador de precios (CSV/JSON + conector VTEX)
│   │   └── navegador.py     # Scraper con Chromium (Hipermaxi, PedidosYa, Chávez)
│   ├── pagos.py             # QR de cobro: proveedor BNB + simulado
│   └── rutas/
│       ├── webhook.py       # GET/POST /webhook (WhatsApp): texto, fotos y suscripción
│       ├── pagos.py         # /pagos: notificación del banco, imagen QR, verificación
│       └── admin.py         # /admin: catálogo, precios, usuarios, pagos
├── semilla.py               # Datos de ejemplo (ilustrativos)
├── tests/
└── requirements.txt
```

## Cómo correr en desarrollo

```bash
cd tatareceta
pip install -r requirements.txt
python semilla.py                    # carga datos de ejemplo en tatareceta.db
uvicorn app.main:app --reload        # API en http://localhost:8000
```

- Documentación interactiva: `http://localhost:8000/docs`
- Sin `WHATSAPP_TOKEN` configurado, los envíos de WhatsApp **se simulan** y se
  escriben en el log — se puede probar todo el flujo sin credenciales de Meta.

### Probar el flujo completo sin WhatsApp real

```bash
curl -X POST http://localhost:8000/webhook -H 'Content-Type: application/json' -d '{
  "entry": [{"changes": [{"value": {
    "contacts": [{"wa_id": "59170000001", "profile": {"name": "Ana"}}],
    "messages": [{"from": "59170000001", "type": "text", "text": {"body": "Amoxil 500 mg"}}]
  }}]}]
}'
```

La respuesta generada queda registrada y visible en
`GET /admin/consultas` (header `X-Admin-Token`).

## Tests

```bash
cd tatareceta
python -m pytest tests/ -v
```

## Modelo de negocio implementado

- **Cuota gratuita:** `CONSULTAS_GRATIS` consultas sin pagar (3 por defecto);
  después se invita a suscribirse (Bs 6–9/mes vía QR).
- **Suscripción automática por QR bancario:** el usuario escribe
  *"quiero suscribirme"* → se genera un QR de cobro y se le envía por
  WhatsApp → cuando el banco notifica el pago (`POST /pagos/notificacion`),
  la suscripción se activa sola y se le confirma por WhatsApp. Respaldo:
  `POST /pagos/{qr_id}/verificar` consulta el estado directamente al banco.
- **Proveedores de QR:** `bnb` (Mercado de APIs del Banco Nacional de
  Bolivia — QR Simple interoperable: el cliente paga desde la app de
  *cualquier* banco) y `simulado` para desarrollo. Credenciales
  `BNB_ACCOUNT_ID`/`BNB_AUTHORIZATION_ID` se solicitan al BNB; ambiente de
  pruebas `http://test.bnb.com.bo`. Las rutas de la API son configurables
  por si el banco las cambia.
- **Respaldo manual (MVP):** sigue disponible
  `POST /admin/suscripciones/{telefono}/activar`.

## Recetas por foto (OCR)

Si el usuario manda la **foto de su receta**, el bot la descarga de
WhatsApp, extrae los medicamentos y responde las equivalencias de cada uno
(máximo 3 por foto). Proveedores (`OCR_PROVEEDOR`):

- `claude` — visión vía API de Anthropic (entiende letra de médico y
  devuelve los medicamentos ya estructurados). Requiere `ANTHROPIC_API_KEY`.
- `simulado` — para desarrollo/tests (`OCR_SIMULADO_TEXTO`).
- `auto` (defecto) — claude si hay API key; si no hay ninguno, el bot pide
  amablemente el nombre por texto.

La IA solo **lee** la receta; nunca recomienda tratamientos.

## Scraper de precios con navegador (Hipermaxi, PedidosYa, Chávez)

Para las tiendas sin API (`app/importadores/navegador.py`), se usa Chromium
headless (Playwright) con **extracción heurística**: encuentra los precios
"Bs …" visibles y el título más cercano en el DOM, sin depender de
selectores CSS frágiles. Funciona igual sobre una URL de búsqueda o sobre
una página guardada con Ctrl+S:

```bash
pip install playwright   # usa el Chromium del sistema si existe

# Tiendas preconfiguradas (hipermaxi | chavez | pedidosya):
python -m app.importadores.navegador --tienda hipermaxi --terminos paracetamol,ibuprofeno --solo-mostrar
python -m app.importadores.navegador --tienda hipermaxi --farmacia "Hipermaxi Online"

# Cualquier otra tienda:
python -m app.importadores.navegador --url "https://otra-tienda/buscar?q={termino}" --farmacia "Otra"

# Página guardada desde tu navegador (sirve cuando el sitio bloquea bots):
python -m app.importadores.navegador --html pagina_guardada.html --farmacia "Hipermaxi Online"
```

Los precios extraídos pasan por el mismo emparejador conservador del
importador de precios (lo dudoso se descarta y se reporta). Operar con
respeto: consultas espaciadas y secuenciales, y priorizar acuerdos directos
con las cadenas cuando el piloto avance.

## Conexión con WhatsApp (cuando haya credenciales de Meta)

1. Crear la app en Meta for Developers y obtener `WHATSAPP_TOKEN` y
   `WHATSAPP_NUMERO_ID`.
2. Configurar el webhook apuntando a `https://<tu-dominio>/webhook` con el
   `WEBHOOK_VERIFY_TOKEN` del `.env`.
3. Listo: los mensajes entrantes se responden automáticamente.

## Importar el catálogo de AGEMED

Fuentes oficiales identificadas (julio 2026):

- **API pública:** `https://apiwww.agemed.gob.bo/api/listautcom` — "listado
  oficial diario de registros sanitarios aprobados".
- **Sistema de consulta:** `https://regsanitario.agemed.gob.bo/`
- **Portal:** `https://www.agemed.gob.bo/` (también publica listas de precios
  referenciales de medicamentos).

```bash
cd tatareceta
# Directo desde la API (necesita internet hacia agemed.gob.bo):
python -m app.importadores.agemed --url

# O desde un archivo JSON/CSV descargado a mano:
python -m app.importadores.agemed --archivo registros.json
```

El importador tolera variantes en los nombres de campos (mayúsculas, acentos,
sinónimos como `producto`/`nombre_comercial`, `generico`/`principio_activo`),
extrae concentración y forma del nombre del producto cuando no vienen como
campos separados, detecta genéricos y hace *upsert* por número de registro
sanitario (reimportar no duplica). Los registros sin datos suficientes para
establecer equivalencia se descartan y se informan.

## Importar precios de farmacias

```bash
cd tatareceta
# Desde un CSV/JSON relevado a mano (columnas: producto, precio [, farmacia]):
python -m app.importadores.precios --archivo precios.csv --farmacia "Farmacorp Online"

# Directo desde una tienda VTEX (Farmacorp usa esa plataforma):
python -m app.importadores.precios --vtex https://www.farmacorp.com --farmacia "Farmacorp Online"
# Por defecto busca todos los principios activos del catálogo; se puede acotar:
python -m app.importadores.precios --vtex https://www.farmacorp.com --farmacia "Farmacorp Online" --terminos amoxicilina,ibuprofeno
```

Cómo funciona:

- **Emparejamiento conservador** contra el catálogo: el nombre comercial o el
  principio activo debe aparecer en el título del producto, y si ambos declaran
  concentración deben coincidir. Ante ambigüedad, el producto se **descarta y
  se reporta** para revisión manual — un precio mal asignado es peor que uno
  faltante.
- Detecta la **presentación** ("caja x 100", "blister x 10") y el asistente
  compara y ordena por **precio unitario**, mostrando ambos valores.
- Acepta precios en formato boliviano ("Bs 320,50").
- Reimportar actualiza los precios existentes (no duplica).

Estado de las fuentes (julio 2026): Farmacorp corre sobre **VTEX** (conector
incluido); Farmacias Chávez (`online.farmaciachavez.com.bo`), Hipermaxi y
PedidosYa no exponen API documentada — para esas, usar el relevamiento manual
por CSV o construir conectores específicos cuando se valide que vale la pena.

## Próximos pasos técnicos (según roadmap)

- [x] Importador del catálogo real de AGEMED (registro sanitario).
- [x] Carga de precios: CSV/JSON manual + conector VTEX (Farmacorp).
- [x] Scraper con navegador para Hipermaxi, PedidosYa, Chávez y otras tiendas.
- [x] Flujo de suscripción con QR bancario (BNB) y activación automática.
- [x] Lectura de recetas por foto (OCR con visión de Claude).
- [ ] Validar credenciales reales: API de AGEMED, QR del BNB y WhatsApp Cloud API.
- [ ] Panel web para farmacias aliadas (modo "solo mi stock").
- [ ] Lectura de recetas por foto (OCR + IA) — hoy solo texto.
- [ ] Flujo de suscripción con QR automático.
- [ ] Panel web para farmacias aliadas (modo "solo mi stock").
