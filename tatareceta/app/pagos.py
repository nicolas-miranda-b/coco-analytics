"""Pagos por QR para la suscripción.

Proveedores:
- ``bnb``: Mercado de APIs del Banco Nacional de Bolivia (QR Simple).
  Flujo: token con accountId+authorizationId (cache ~45 min) → generar QR
  (devuelve id + imagen PNG en base64 + expiración) → el banco notifica el
  pago a nuestro webhook (`POST /pagos/notificacion`) y además se puede
  consultar el estado. Ambientes: http://test.bnb.com.bo (pruebas) y
  https://marketapi.bnb.com.bo (producción).
- ``simulado``: para desarrollo y tests; el "pago" se dispara llamando al
  mismo webhook de notificación.

Los QR de otros bancos (BCP, Mercantil, etc.) usan el estándar interoperable
QR Simple del BCB, así que cualquier banco puede escanear un QR emitido por
el BNB. Si más adelante se cambia de banco emisor, basta implementar otro
proveedor con esta misma interfaz.
"""

import base64
import logging
import time
import uuid
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol

from .config import config

logger = logging.getLogger("tatareceta.pagos")


@dataclass
class QRGenerado:
    qr_id: str
    imagen_base64: str  # PNG en base64 (sin encabezado data:)
    expira: str  # fecha ISO


class ProveedorQR(Protocol):
    nombre: str

    def generar_qr(self, monto_bs: float, glosa: str, referencia: str) -> QRGenerado: ...

    def consultar_estado(self, qr_id: str) -> str:
        """'pendiente' | 'pagado' | 'expirado' | 'error'"""
        ...


# PNG de 1x1 gris: placeholder de imagen QR en modo simulado.
_PNG_SIMULADO = base64.b64encode(
    bytes.fromhex(
        "89504e470d0a1a0a0000000d49484452000000010000000108020000009077"
        "53de0000000c4944415408d763a8a9a90100029b019ee7b34a480000000049"
        "454e44ae426082"
    )
).decode()


class ProveedorSimulado:
    nombre = "simulado"

    def generar_qr(self, monto_bs: float, glosa: str, referencia: str) -> QRGenerado:
        qr_id = f"SIM-{referencia}-{uuid.uuid4().hex[:8]}"
        logger.info("[simulado] QR generado %s por Bs %.2f (%s)", qr_id, monto_bs, glosa)
        expira = (date.today() + timedelta(days=1)).isoformat()
        return QRGenerado(qr_id=qr_id, imagen_base64=_PNG_SIMULADO, expira=expira)

    def consultar_estado(self, qr_id: str) -> str:
        return "pendiente"  # el pago simulado llega solo por el webhook


class ProveedorBNB:
    """Cliente del QR Simple del BNB (Mercado de APIs).

    Rutas por defecto según la documentación pública del banco; si el banco
    las cambia, se pueden sobreescribir con variables de entorno sin tocar
    código (BNB_RUTA_TOKEN, BNB_RUTA_GENERAR, BNB_RUTA_ESTADO).
    """

    nombre = "bnb"

    RUTA_TOKEN = "/ClientAuthentication.API/api/v1/auth/token"
    RUTA_GENERAR = "/QRSimple.API/api/v1/main/getQRWithImageAsync"
    RUTA_ESTADO = "/QRSimple.API/api/v1/main/getQRStatusAsync"

    # statusId documentados del QR Simple BNB
    ESTADOS = {1: "pendiente", 2: "pagado", 3: "expirado", 4: "error"}

    def __init__(self) -> None:
        import os

        self.url_base = config.bnb_url_base.rstrip("/")
        self.ruta_token = os.getenv("BNB_RUTA_TOKEN", self.RUTA_TOKEN)
        self.ruta_generar = os.getenv("BNB_RUTA_GENERAR", self.RUTA_GENERAR)
        self.ruta_estado = os.getenv("BNB_RUTA_ESTADO", self.RUTA_ESTADO)
        self._token: str | None = None
        self._token_expira = 0.0

    # separado para poder simularlo en tests
    def _post(self, ruta: str, cuerpo: dict, token: str | None = None) -> dict:
        import httpx

        cabeceras = {"Accept": "application/json"}
        if token:
            cabeceras["Authorization"] = f"Bearer {token}"
        respuesta = httpx.post(
            f"{self.url_base}{ruta}", json=cuerpo, headers=cabeceras, timeout=30
        )
        respuesta.raise_for_status()
        return respuesta.json()

    def _obtener_token(self) -> str:
        if self._token and time.monotonic() < self._token_expira:
            return self._token
        if not config.bnb_account_id or not config.bnb_authorization_id:
            raise RuntimeError(
                "Faltan credenciales del BNB: configurar BNB_ACCOUNT_ID y BNB_AUTHORIZATION_ID"
            )
        datos = self._post(
            self.ruta_token,
            {
                "accountId": config.bnb_account_id,
                "authorizationId": config.bnb_authorization_id,
            },
        )
        token = datos.get("message") or datos.get("token") or ""
        if not token or datos.get("success") is False:
            raise RuntimeError(f"El BNB no devolvió token: {datos}")
        self._token = token
        self._token_expira = time.monotonic() + 40 * 60  # el banco lo expira a ~45 min
        return token

    def generar_qr(self, monto_bs: float, glosa: str, referencia: str) -> QRGenerado:
        token = self._obtener_token()
        expira = (date.today() + timedelta(days=1)).isoformat()
        datos = self._post(
            self.ruta_generar,
            {
                "currency": "BOB",
                "amount": round(monto_bs, 2),
                "gloss": glosa,
                "singleUse": True,
                "expirationDate": expira,
                "additionalData": referencia,
            },
            token=token,
        )
        qr_id = str(datos.get("id") or datos.get("qrId") or "")
        imagen = datos.get("qr") or datos.get("qrImage") or ""
        if not qr_id or not imagen or datos.get("success") is False:
            raise RuntimeError(f"El BNB no devolvió el QR: {datos}")
        return QRGenerado(qr_id=qr_id, imagen_base64=imagen, expira=expira)

    def consultar_estado(self, qr_id: str) -> str:
        token = self._obtener_token()
        datos = self._post(self.ruta_estado, {"qrId": qr_id}, token=token)
        estado_crudo = datos.get("statusId", datos.get("status"))
        if isinstance(estado_crudo, int):
            return self.ESTADOS.get(estado_crudo, "error")
        texto = str(estado_crudo or "").lower()
        for estado in ("pagado", "expirado", "pendiente"):
            if estado in texto or texto in ("paid", "expired", "generated"):
                break
        return {"paid": "pagado", "expired": "expirado", "generated": "pendiente"}.get(
            texto, texto or "error"
        )


_PROVEEDORES = {"simulado": ProveedorSimulado, "bnb": ProveedorBNB}
_instancias: dict[str, object] = {}


def obtener_proveedor() -> ProveedorQR:
    nombre = config.pagos_proveedor
    if nombre not in _PROVEEDORES:
        raise RuntimeError(f"Proveedor de pagos desconocido: {nombre!r}")
    if nombre not in _instancias:
        _instancias[nombre] = _PROVEEDORES[nombre]()
    return _instancias[nombre]  # type: ignore[return-value]
