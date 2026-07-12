from sqlalchemy import select

from app.modelos import Pago, Usuario
from app.pagos import ProveedorBNB

ADMIN = {"X-Admin-Token": "token-de-prueba"}


def _mensaje(telefono: str, texto: str) -> dict:
    return {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "contacts": [{"wa_id": telefono, "profile": {"name": "P"}}],
                            "messages": [
                                {"from": telefono, "type": "text", "text": {"body": texto}}
                            ],
                        }
                    }
                ]
            }
        ]
    }


def test_flujo_completo_suscripcion_por_qr(cliente):
    telefono = "59171112222"

    # 1) El usuario pide suscribirse → se genera un QR y un Pago pendiente
    r = cliente.post("/webhook", json=_mensaje(telefono, "Quiero suscribirme"))
    assert r.status_code == 200
    pagos = cliente.get("/admin/pagos", headers=ADMIN).json()
    assert len(pagos) == 1
    assert pagos[0]["estado"] == "pendiente"
    assert pagos[0]["proveedor"] == "simulado"
    qr_id = pagos[0]["qr_id"]

    # 2) La imagen del QR se sirve para que WhatsApp la adjunte
    r = cliente.get(f"/pagos/{qr_id}/qr.png")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert r.content[:8] == b"\x89PNG\r\n\x1a\n"

    # 3) Pedir suscripción otra vez NO genera un segundo QR (reusa el pendiente)
    cliente.post("/webhook", json=_mensaje(telefono, "suscribirme de nuevo"))
    assert len(cliente.get("/admin/pagos", headers=ADMIN).json()) == 1

    # 4) El banco notifica el pago → suscripción activa + pago marcado
    r = cliente.post("/pagos/notificacion", json={"qrId": qr_id})
    assert r.status_code == 200 and r.json()["success"]
    pago = cliente.get("/admin/pagos", headers=ADMIN).json()[0]
    assert pago["estado"] == "pagado"
    assert pago["pagado_en"] is not None
    usuario = next(
        u for u in cliente.get("/admin/usuarios", headers=ADMIN).json()
        if u["telefono"] == telefono
    )
    assert usuario["suscrito_hasta"] is not None

    # 5) Notificación repetida es idempotente
    r = cliente.post("/pagos/notificacion", json={"qrId": qr_id})
    assert r.json()["detalle"] == "Ya estaba pagado"


def test_suscripcion_disponible_con_cuota_agotada(cliente):
    telefono = "59173334444"
    for _ in range(4):  # agota la cuota gratis (3) y una más
        cliente.post("/webhook", json=_mensaje(telefono, "ibuprofeno"))
    # Aun sin cuota, puede iniciar la suscripción
    cliente.post("/webhook", json=_mensaje(telefono, "QUIERO SUSCRIBIRME"))
    pagos = [
        p for p in cliente.get("/admin/pagos", headers=ADMIN).json()
        if p["estado"] == "pendiente"
    ]
    assert pagos, "debe existir un pago pendiente para el usuario sin cuota"


def test_notificacion_qr_desconocido_no_rompe(cliente):
    r = cliente.post("/pagos/notificacion", json={"qrId": "NO-EXISTE"})
    assert r.status_code == 200
    assert r.json()["detalle"] == "QR no registrado"


def test_notificacion_extrae_qr_id_anidado(cliente):
    cliente.post("/webhook", json=_mensaje("59175556666", "suscribirme"))
    qr_id = cliente.get("/admin/pagos", headers=ADMIN).json()[0]["qr_id"]
    # Formato anidado tipo {"data": {"QRId": ...}} que usan algunos bancos
    r = cliente.post("/pagos/notificacion", json={"data": {"QRId": qr_id}})
    assert r.json()["success"]


def test_notificacion_exige_secreto_si_esta_configurado(cliente, monkeypatch):
    from app.config import config

    monkeypatch.setattr(config, "pagos_webhook_secret", "secreto-bnb")
    r = cliente.post("/pagos/notificacion", json={"qrId": "X"})
    assert r.status_code == 401
    r = cliente.post(
        "/pagos/notificacion",
        json={"qrId": "X"},
        headers={"X-Webhook-Secret": "secreto-bnb"},
    )
    assert r.status_code == 200


def test_verificar_pago_consulta_al_proveedor(cliente, monkeypatch):
    cliente.post("/webhook", json=_mensaje("59177778888", "suscribirme"))
    qr_id = cliente.get("/admin/pagos", headers=ADMIN).json()[0]["qr_id"]

    r = cliente.post(f"/pagos/{qr_id}/verificar")
    assert r.json()["estado"] == "pendiente"  # el simulado nunca paga solo

    import app.rutas.pagos as rutas_pagos

    class ProveedorPagado:
        def consultar_estado(self, qr_id):
            return "pagado"

    monkeypatch.setattr(rutas_pagos, "obtener_proveedor", lambda: ProveedorPagado())
    r = cliente.post(f"/pagos/{qr_id}/verificar")
    assert r.json()["estado"] == "pagado"


# --- Proveedor BNB (sin red: se intercepta el transporte HTTP) ---


def _bnb_con_respuestas(monkeypatch, respuestas):
    from app.config import config

    monkeypatch.setattr(config, "bnb_account_id", "cuenta-1")
    monkeypatch.setattr(config, "bnb_authorization_id", "auth-1")
    proveedor = ProveedorBNB()
    llamadas = []

    def _post_falso(ruta, cuerpo, token=None):
        llamadas.append({"ruta": ruta, "cuerpo": cuerpo, "token": token})
        return respuestas[ruta]

    monkeypatch.setattr(proveedor, "_post", _post_falso)
    return proveedor, llamadas


def test_bnb_genera_qr_con_token(monkeypatch):
    proveedor, llamadas = _bnb_con_respuestas(
        monkeypatch,
        {
            ProveedorBNB.RUTA_TOKEN: {"success": True, "message": "jwt-123"},
            ProveedorBNB.RUTA_GENERAR: {"success": True, "id": 998877, "qr": "aW1n"},
            ProveedorBNB.RUTA_ESTADO: {"success": True, "statusId": 1},
        },
    )
    qr = proveedor.generar_qr(7.0, "Suscripción TataReceta 591...", "TR-1")
    assert qr.qr_id == "998877"
    assert qr.imagen_base64 == "aW1n"

    assert llamadas[0]["ruta"] == ProveedorBNB.RUTA_TOKEN
    assert llamadas[0]["cuerpo"] == {"accountId": "cuenta-1", "authorizationId": "auth-1"}
    generar = llamadas[1]
    assert generar["token"] == "jwt-123"
    assert generar["cuerpo"]["amount"] == 7.0
    assert generar["cuerpo"]["currency"] == "BOB"
    assert generar["cuerpo"]["singleUse"] is True
    assert generar["cuerpo"]["additionalData"] == "TR-1"

    # Segunda operación: el token se reusa (cache), no se vuelve a pedir
    proveedor.consultar_estado("998877")
    pedidos_de_token = [l for l in llamadas if l["ruta"] == ProveedorBNB.RUTA_TOKEN]
    assert len(pedidos_de_token) == 1


def test_bnb_mapea_estados(monkeypatch):
    proveedor, _ = _bnb_con_respuestas(
        monkeypatch,
        {
            ProveedorBNB.RUTA_TOKEN: {"success": True, "message": "jwt"},
            ProveedorBNB.RUTA_ESTADO: {"success": True, "statusId": 2},
        },
    )
    assert proveedor.consultar_estado("1") == "pagado"


def test_bnb_sin_credenciales_da_error_claro(monkeypatch):
    from app.config import config

    monkeypatch.setattr(config, "bnb_account_id", "")
    proveedor = ProveedorBNB()
    try:
        proveedor.generar_qr(7, "x", "r")
        assert False, "debió fallar"
    except RuntimeError as error:
        assert "BNB_ACCOUNT_ID" in str(error)
