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

## Próximos pasos técnicos (según roadmap)

- [ ] Importador del catálogo real de AGEMED (registro sanitario).
- [ ] Relevamiento/carga de precios de Farmacorp, Chávez, Hipermaxi, PedidosYa.
- [ ] Lectura de recetas por foto (OCR + IA) — hoy solo texto.
- [ ] Flujo de suscripción con QR automático.
- [ ] Panel web para farmacias aliadas (modo "solo mi stock").
