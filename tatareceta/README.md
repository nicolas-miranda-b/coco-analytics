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
│   │   └── equivalencias.py # Búsqueda de equivalentes + comparación de precios
│   ├── importadores/
│   │   └── agemed.py        # Importador del registro sanitario de AGEMED
│   └── rutas/
│       ├── webhook.py       # GET/POST /webhook (WhatsApp)
│       └── admin.py         # /admin: catálogo, precios, suscripciones
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
- **Suscripción (MVP manual):** el pago QR se confirma a mano con
  `POST /admin/suscripciones/{telefono}/activar`.

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

## Próximos pasos técnicos (según roadmap)

- [x] Importador del catálogo real de AGEMED (registro sanitario).
- [ ] Relevamiento/carga de precios de Farmacorp, Chávez, Hipermaxi, PedidosYa.
- [ ] Lectura de recetas por foto (OCR + IA) — hoy solo texto.
- [ ] Flujo de suscripción con QR automático.
- [ ] Panel web para farmacias aliadas (modo "solo mi stock").
