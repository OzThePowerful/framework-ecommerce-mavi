"""Estructura obligatoria de datasets base por ecommerce (EC-SP01-004).

Los tests validan la estructura vía DataProvider, no por rutas
físicas: un dataset ausente produce DataError del propio proveedor.
"""

import pytest

from data_providers.yaml_data_provider import YamlDataProvider

pytestmark = pytest.mark.unit

REQUIRED_DATASETS = (
    "search",
    "products",
    "addresses",
    "checkout",
    "payment",
)
SITES = ("muebles_america", "viu")


@pytest.mark.parametrize("site", SITES)
def test_datasets_base_presentes(site):
    """Los 6 datasets base existen, parsean y contienen registros."""
    provider = YamlDataProvider(site)
    for name in REQUIRED_DATASETS:
        data = provider.get_dataset(name)
        assert isinstance(data, dict) and data, (
            f"{site}/{name}.yaml debe ser un mapa de registros no vacío"
        )


def test_cliente_no_esta_en_dataset():
    """La identidad del comprador es privada del equipo: no existe
    dataset `customers` versionado (resuelve MAVI_GUEST_* del .env)."""
    provider = YamlDataProvider("muebles_america")
    try:
        provider.get_dataset("customers")
    except Exception:
        return
    raise AssertionError("customers.yaml no debe existir en data/")
