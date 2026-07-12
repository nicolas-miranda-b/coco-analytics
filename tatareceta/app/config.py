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


config = Config()
