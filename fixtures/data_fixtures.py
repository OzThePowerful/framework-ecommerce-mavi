"""Fixtures de datos de entrada vía DataProvider (nunca rutas físicas)."""

import os

import pytest

from core.execution.execution_errors import ConfigError
from data_providers.customer_provider import resolve_guest_customer
from data_providers.yaml_data_provider import YamlDataProvider
from domain.models.customer import Customer


@pytest.fixture(scope="session")
def data_provider(execution_context) -> YamlDataProvider:
    return YamlDataProvider(site=execution_context.site)


@pytest.fixture
def payment_card(data_provider) -> dict[str, str]:
    """Tarjeta de prueba del dataset `payment`/`card`.

    Son datos ficticios de sandbox (OpenPay público): versionados por
    decisión del equipo. Las credenciales reales viven en .env.
    """
    record = data_provider.get_record("payment", "card")
    return {
        "number": record["number"],
        "cvv": record["cvv"],
        "exp_month": record["exp_month"],
        "exp_year": record["exp_year"],
    }


@pytest.fixture
def guest_customer(execution_context) -> Customer:
    """Identidad del comprador invitado desde `MAVI_GUEST_<SITIO>_*`
    (.env / entorno; nunca versionada)."""
    return resolve_guest_customer(execution_context.site)


@pytest.fixture
def site_credentials(execution_context) -> dict[str, str]:
    """Credenciales de login del sitio activo desde .env / variables
    de entorno (datos privados del equipo, nunca versionados)."""
    site_key = {
        "muebles_america": "MA",
        "viu": "VIU",
    }.get(execution_context.site, execution_context.site.upper())
    prefix = f"MAVI_LOGIN_{site_key}_"
    missing = [
        f"{prefix}{field}"
        for field in ("EMAIL", "PASSWORD")
        if not os.environ.get(f"{prefix}{field}")
    ]
    if missing:
        raise ConfigError(
            "Credenciales de login ausentes; definir en .env o entorno: "
            + ", ".join(missing)
        )
    return {
        "email": os.environ[f"{prefix}EMAIL"],
        "password": os.environ[f"{prefix}PASSWORD"],
    }
