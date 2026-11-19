"""Fixtures de datos de entrada vía DataProvider (nunca rutas físicas)."""

import pytest

from data_providers.yaml_data_provider import YamlDataProvider


@pytest.fixture(scope="session")
def data_provider(execution_context) -> YamlDataProvider:
    return YamlDataProvider(site=execution_context.site)
