ADMIN = {"X-Admin-Token": "token-de-prueba"}


def _payload_whatsapp(telefono: str, texto: str) -> dict:
    """Estructura real de un evento de mensaje de WhatsApp Cloud API."""
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "contacts": [
                                {"wa_id": telefono, "profile": {"name": "Prueba"}}
                            ],
                            "messages": [
                                {
                                    "from": telefono,
                                    "type": "text",
                                    "text": {"body": texto},
                                }
                            ],
                        }
                    }
                ]
            }
        ],
    }


def test_salud(cliente):
    assert cliente.get("/salud").json()["estado"] == "ok"


def test_verificacion_webhook_correcta(cliente):
    r = cliente.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "tatareceta-dev",
            "hub.challenge": "12345",
        },
    )
    assert r.status_code == 200
    assert r.text == "12345"


def test_verificacion_webhook_token_invalido(cliente):
    r = cliente.get(
        "/webhook",
        params={"hub.mode": "subscribe", "hub.verify_token": "malo", "hub.challenge": "x"},
    )
    assert r.status_code == 403


def test_consulta_por_webhook_crea_usuario_y_responde(cliente):
    r = cliente.post("/webhook", json=_payload_whatsapp("59170000001", "Amoxil 500 mg"))
    assert r.status_code == 200
    assert r.json()["procesados"] == 1

    consultas = cliente.get("/admin/consultas", headers=ADMIN).json()
    assert len(consultas) == 1
    assert "Amoxicilina" in consultas[0]["respuesta"]
    assert consultas[0]["exitosa"]

    usuarios = cliente.get("/admin/usuarios", headers=ADMIN).json()
    assert usuarios[0]["telefono"] == "59170000001"


def test_cuota_gratuita_y_suscripcion(cliente):
    telefono = "59170000002"
    for _ in range(3):  # agota las 3 consultas gratis
        cliente.post("/webhook", json=_payload_whatsapp(telefono, "ibuprofeno"))

    r = cliente.post("/webhook", json=_payload_whatsapp(telefono, "ibuprofeno"))
    assert r.status_code == 200
    ultima = cliente.get("/admin/consultas", headers=ADMIN).json()[0]
    assert "consultas gratuitas" in ultima["respuesta"]

    # Se confirma el pago por QR → se activa la suscripción → vuelve a funcionar
    r = cliente.post(f"/admin/suscripciones/{telefono}/activar", headers=ADMIN)
    assert r.status_code == 200
    assert r.json()["suscrito_hasta"] is not None

    cliente.post("/webhook", json=_payload_whatsapp(telefono, "ibuprofeno"))
    ultima = cliente.get("/admin/consultas", headers=ADMIN).json()[0]
    assert "Ibuprofeno" in ultima["respuesta"]


def test_admin_requiere_token(cliente):
    assert cliente.get("/admin/medicamentos").status_code == 401
    assert cliente.get("/admin/medicamentos", headers={"X-Admin-Token": "malo"}).status_code == 401


def test_admin_crear_medicamento_normaliza(cliente):
    r = cliente.post(
        "/admin/medicamentos",
        headers=ADMIN,
        json={
            "nombre_comercial": "Azitrocin",
            "principio_activo": "Azitromicina",
            "concentracion_valor": 500,
            "concentracion_unidad": "mg",
            "forma": "tabletas",
        },
    )
    assert r.status_code == 200
    datos = r.json()
    assert datos["principio_activo"] == "azitromicina"
    assert datos["forma"] == "comprimido"
