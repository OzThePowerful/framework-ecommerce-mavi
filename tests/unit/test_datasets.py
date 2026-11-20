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
    "customers",
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


def test_fallback_common_resuelve_cliente():
    """mavi aún no tiene datasets propios: customers viene de common."""
    data = YamlDataProvider("mavi").get_dataset("customers")
    assert "default_guest" in data
