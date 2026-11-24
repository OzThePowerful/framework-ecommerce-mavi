"""Resolución de identidad de comprador desde variables de entorno.

Los datos del cliente son privados del equipo (correo real, teléfono):
viven en `.env` o secrets de CI bajo `MAVI_GUEST_<SITIO>_*`, nunca en
datasets versionados — un correo ficticio es rechazado por la
validación externa del checkout al confirmar la orden.
"""

import os

from core.execution.execution_errors import ConfigError
from domain.models.customer import Customer

_SITE_KEYS = {
    "muebles_america": "MA",
    "viu": "VIU",
}

_REQUIRED = ("FIRST_NAME", "LAST_NAME", "EMAIL", "PHONE")
_OPTIONAL = ("MOTHERS_NAME",)


def resolve_guest_customer(site: str) -> Customer:
    """Customer de dominio desde `MAVI_GUEST_<SITIO>_*` en el entorno."""
    key = _SITE_KEYS.get(site, site.upper())
    prefix = f"MAVI_GUEST_{key}_"
    missing = [
        f"{prefix}{field}"
        for field in _REQUIRED
        if not os.environ.get(f"{prefix}{field}")
    ]
    if missing:
        raise ConfigError(
            "Identidad del comprador ausente; definir en .env o entorno: "
            + ", ".join(missing)
        )
    return Customer(
        name=os.environ[f"{prefix}FIRST_NAME"],
        last_name=os.environ[f"{prefix}LAST_NAME"],
        mothers_name=os.environ.get(f"{prefix}MOTHERS_NAME") or None,
        email=os.environ[f"{prefix}EMAIL"],
        phone=os.environ[f"{prefix}PHONE"],
    )
