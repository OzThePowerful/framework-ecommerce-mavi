"""Fixtures de datos de entrada vía DataProvider (nunca rutas físicas)."""

import os

import pytest

from core.execution.execution_errors import ConfigError
from data_providers.yaml_data_provider import YamlDataProvider

_CARD_ENV_VARS = (
    "MAVI_PAY_CARD_NUMBER",
    "MAVI_PAY_CARD_CVV",
    "MAVI_PAY_CARD_EXP_MONTH",
    "MAVI_PAY_CARD_EXP_YEAR",
)


@pytest.fixture(scope="session")
def data_provider(execution_context) -> YamlDataProvider:
    return YamlDataProvider(site=execution_context.site)


@pytest.fixture
def payment_card() -> dict[str, str]:
    """Tarjeta de prueba desde variables de entorno (nunca versionada).

    En stage se usan las tarjetas públicas de sandbox del proveedor
    (OpenPay); el fixture falla con instrucciones si faltan.
    """
    missing = [name for name in _CARD_ENV_VARS if not os.environ.get(name)]
    if missing:
        raise ConfigError(
            "Datos de tarjeta de prueba ausentes; definir "
            + ", ".join(missing)
        )
    return {
        "number": os.environ["MAVI_PAY_CARD_NUMBER"],
        "cvv": os.environ["MAVI_PAY_CARD_CVV"],
        "exp_month": os.environ["MAVI_PAY_CARD_EXP_MONTH"],
        "exp_year": os.environ["MAVI_PAY_CARD_EXP_YEAR"],
    }
