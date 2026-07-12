"""Configuración central leída de variables de entorno."""

import os
from dataclasses import dataclass, field


def _env(nombre: str, defecto: str = "") -> str:
    return os.getenv(nombre, defecto)


@dataclass
class Config:
    base_datos_url: str = field(
        default_factory=lambda: _env("TATARECETA_DB", "sqlite:///./tatareceta.db")
    )
    whatsapp_token: str = field(default_factory=lambda: _env("WHATSAPP_TOKEN"))
    whatsapp_numero_id: str = field(default_factory=lambda: _env("WHATSAPP_NUMERO_ID"))
    webhook_verify_token: str = field(
        default_factory=lambda: _env("WEBHOOK_VERIFY_TOKEN", "tatareceta-dev")
    )
    consultas_gratis: int = field(
        default_factory=lambda: int(_env("CONSULTAS_GRATIS", "3"))
    )
    precio_suscripcion_bs: float = field(
        default_factory=lambda: float(_env("PRECIO_SUSCRIPCION_BS", "7"))
    )
    admin_token: str = field(default_factory=lambda: _env("ADMIN_TOKEN", "cambia-este-token"))
    # URL pública de esta API (para armar links, p. ej. la imagen del QR)
    base_url_publica: str = field(
        default_factory=lambda: _env("BASE_URL_PUBLICA", "http://localhost:8000")
    )

    # --- Pagos por QR ---
    pagos_proveedor: str = field(default_factory=lambda: _env("PAGOS_PROVEEDOR", "simulado"))
    pagos_webhook_secret: str = field(default_factory=lambda: _env("PAGOS_WEBHOOK_SECRET"))
    # BNB (Mercado de APIs): test http://test.bnb.com.bo | prod https://marketapi.bnb.com.bo
    bnb_url_base: str = field(
        default_factory=lambda: _env("BNB_URL_BASE", "https://marketapi.bnb.com.bo")
    )
    bnb_account_id: str = field(default_factory=lambda: _env("BNB_ACCOUNT_ID"))
    bnb_authorization_id: str = field(default_factory=lambda: _env("BNB_AUTHORIZATION_ID"))

    # --- OCR de recetas ---
    ocr_proveedor: str = field(default_factory=lambda: _env("OCR_PROVEEDOR", "auto"))
    anthropic_api_key: str = field(default_factory=lambda: _env("ANTHROPIC_API_KEY"))
    ocr_modelo: str = field(default_factory=lambda: _env("OCR_MODELO", "claude-haiku-4-5-20251001"))
    ocr_simulado_texto: str = field(default_factory=lambda: _env("OCR_SIMULADO_TEXTO"))


config = Config()
