"""Pruebas unitarias de resolución de sitio/ambiente."""

import pytest

from core.config.site_config import resolve_site
from core.execution.execution_errors import (
    UnknownEnvironmentError,
    UnknownSiteError,
)

pytestmark = pytest.mark.unit


def test_sitios_soportados_resuelven_stage():
    for site in ("muebles_america", "viu", "mavi"):
        config = resolve_site(site, "stage")
        assert config.site == site
        assert config.code
        assert config.base_url.startswith("http")


def test_sitio_desconocido_falla_explicito():
    with pytest.raises(UnknownSiteError):
        resolve_site("sitio_inexistente", "stage")


def test_ambiente_desconocido_falla_explicito():
    with pytest.raises(UnknownEnvironmentError):
        resolve_site("muebles_america", "ambiente_inexistente")


def test_ambiente_no_declarado_en_catalogo():
    """Un ambiente presente en sites.yaml pero ausente de environments.yaml
    debe fallar: el catálogo de ambientes válidos es environments.yaml."""
    sites = {
        "sites": {
            "muebles_america": {
                "code": "MA",
                "environments": {"qa": {"base_url": "placeholder"}},
            }
        }
    }
    with pytest.raises(UnknownEnvironmentError):
        resolve_site("muebles_america", "qa", sites=sites)


def test_ambiente_declarado_pero_no_disponible_para_sitio():
    """Ambiente válido en el catálogo pero no expuesto por el sitio."""
    sites = {
        "sites": {
            "x": {
                "code": "X",
                "environments": {"prod": {"base_url": "placeholder"}},
            }
        }
    }
    environments = {"environments": {"stage": {}, "prod": {}}}
    with pytest.raises(UnknownEnvironmentError):
        resolve_site("x", "stage", sites=sites, environments=environments)
