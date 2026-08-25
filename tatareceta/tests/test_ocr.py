import base64

from app import whatsapp
from app.motor.ocr import OCRClaude, _lineas_de_medicamentos, obtener_ocr

ADMIN = {"X-Admin-Token": "token-de-prueba"}


def _mensaje_imagen(telefono: str, media_id: str = "MEDIA-1", caption: str = "") -> dict:
    return {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "contacts": [{"wa_id": telefono, "profile": {"name": "P"}}],
                            "messages": [
                                {
                                    "from": telefono,
                                    "type": "image",
                                    "image": {"id": media_id, "caption": caption},
                                }
                            ],
                        }
                    }
                ]
            }
        ]
    }


def test_extraer_mensajes_incluye_imagenes():
    mensajes = whatsapp.extraer_mensajes(_mensaje_imagen("591700", "M-9", "mi receta"))
    assert len(mensajes) == 1
    assert mensajes[0].tipo == "imagen"
    assert mensajes[0].media_id == "M-9"
    assert mensajes[0].texto == "mi receta"


def test_lineas_de_medicamentos_limpia_vinetas_y_ninguno():
    assert _lineas_de_medicamentos("- amoxicilina 500 mg\n• ibuprofeno 400 mg\n") == [
        "amoxicilina 500 mg",
        "ibuprofeno 400 mg",
    ]
    assert _lineas_de_medicamentos("NINGUNO") == []
    assert _lineas_de_medicamentos("") == []


def test_obtener_ocr_por_configuracion(monkeypatch):
    from app.config import config

    monkeypatch.setattr(config, "ocr_proveedor", "auto")
    monkeypatch.setattr(config, "anthropic_api_key", "")
    monkeypatch.setattr(config, "ocr_simulado_texto", "")
    assert obtener_ocr() is None

    monkeypatch.setattr(config, "ocr_simulado_texto", "paracetamol 500 mg")
    assert type(obtener_ocr()).__name__ == "OCRSimulado"

    monkeypatch.setattr(config, "anthropic_api_key", "clave")
    assert type(obtener_ocr()).__name__ == "OCRClaude"


def test_webhook_imagen_sin_ocr_pide_texto(cliente):
    r = cliente.post("/webhook", json=_mensaje_imagen("59178880001"))
    assert r.status_code == 200
    ultima = cliente.get("/admin/consultas", headers=ADMIN).json()[0]
    assert "no puedo leer fotos" in ultima["respuesta"]
    assert ultima["texto"].startswith("[imagen]")


def test_webhook_imagen_con_ocr_simulado_responde_equivalentes(cliente, monkeypatch):
    from app.config import config
    import app.rutas.webhook as modulo_webhook

    monkeypatch.setattr(config, "ocr_proveedor", "simulado")
    monkeypatch.setattr(config, "ocr_simulado_texto", "amoxicilina 500 mg capsulas")
    monkeypatch.setattr(
        modulo_webhook.whatsapp, "descargar_media", lambda media_id: (b"foto", "image/jpeg")
    )

    r = cliente.post("/webhook", json=_mensaje_imagen("59178880002"))
    assert r.status_code == 200
    ultima = cliente.get("/admin/consultas", headers=ADMIN).json()[0]
    assert ultima["exitosa"]
    assert "Leí tu receta" in ultima["respuesta"]
    assert "Amoxicilina" in ultima["respuesta"]
    assert "no reemplaza el criterio" in ultima["respuesta"]


def test_ocr_claude_arma_la_peticion_correcta(monkeypatch):
    from app.config import config

    monkeypatch.setattr(config, "anthropic_api_key", "clave-x")
    capturado = {}

    class RespuestaFalsa:
        def raise_for_status(self):
            pass

        def json(self):
            return {"content": [{"type": "text", "text": "amoxicilina 500 mg\nNINGUNO"}]}

    def post_falso(url, headers=None, json=None, timeout=None):
        capturado.update(url=url, headers=headers, json=json)
        return RespuestaFalsa()

    import httpx

    monkeypatch.setattr(httpx, "post", post_falso)

    lineas = OCRClaude().extraer_medicamentos(b"bytes-de-foto", "image/jpeg")
    assert lineas == ["amoxicilina 500 mg"]
    assert capturado["url"] == OCRClaude.URL
    assert capturado["headers"]["x-api-key"] == "clave-x"
    contenido = capturado["json"]["messages"][0]["content"]
    assert contenido[0]["source"]["data"] == base64.b64encode(b"bytes-de-foto").decode()
    assert "receta" in contenido[1]["text"]
