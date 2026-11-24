"""Contrato del selector de Case ID (EC-SP01-020).

Cubre: formato, código de marca desconocido, ID inexistente en el
catálogo, derivación de sitio por marca, precedencia env/--site y
conflicto explícito entre --case-id y el sitio declarado.
"""

import pytest

from core.execution.case_selector import (
    CaseSelection,
    catalog_case_ids,
    parse_case_id,
    resolve_run_site,
)
from core.execution.execution_errors import ConfigError

_SITES = {
    "sites": {
        "muebles_america": {"code": "MA"},
        "viu": {"code": "VIU"},
    }
}
_CATALOG = frozenset(
    {"CP_EC_MA_CART_001", "CP_EC_VIU_CART_001", "CP_EC_MA_HOME_001"}
)


def _parse(raw: str) -> CaseSelection:
    return parse_case_id(raw, sites=_SITES, catalog=_CATALOG)


def test_case_id_valido_deriva_sitio_ma():
    sel = _parse("CP_EC_MA_CART_001")
    assert sel.site == "muebles_america"
    assert sel.site_code == "MA"
    assert sel.case_id == "CP_EC_MA_CART_001"


def test_case_id_valido_deriva_sitio_viu():
    sel = _parse("CP_EC_VIU_CART_001")
    assert sel.site == "viu"
    assert sel.site_code == "VIU"


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "MA_CART_001",
        "CP_MA_CART_001",
        "CP_EC_MA_CART",
        "CP_EC_MA_CART_1",
        "CP_EC_MA_CART_001_EXTRA",
        "cp_ec_ma_cart_001",
    ],
)
def test_formato_invalido_falla_explicito(raw):
    with pytest.raises(ConfigError, match="Formato esperado"):
        _parse(raw)


def test_codigo_de_marca_desconocido_falla_explicito():
    with pytest.raises(ConfigError, match="'XX'"):
        _parse("CP_EC_XX_CART_001")


def test_case_id_inexistente_falla_explicito_con_sugerencia():
    with pytest.raises(ConfigError, match="inexistente"):
        _parse("CP_EC_MA_PDP_999")


def test_catalogo_real_contiene_los_ids_validacion_contrato():
    """Los IDs de la validación obligatoria existen en el catálogo."""
    ids = catalog_case_ids()
    for case_id in (
        "CP_EC_MA_HOME_001",
        "CP_EC_VIU_HOME_001",
        "CP_EC_MA_CART_001",
        "CP_EC_VIU_CART_001",
    ):
        assert case_id in ids


def test_sitio_sin_case_id_conserva_precedencia_env_sobre_opcion():
    site = resolve_run_site(
        case_id=None,
        site_option="muebles_america",
        site_env="viu",
        site_option_explicit=True,
        sites=_SITES,
    )
    assert site == "viu"


def test_sitio_sin_case_id_usa_opcion():
    site = resolve_run_site(
        case_id=None,
        site_option="viu",
        site_env=None,
        site_option_explicit=True,
        sites=_SITES,
    )
    assert site == "viu"


def test_case_id_deriva_sitio_ignorando_default_no_explicito():
    """--site con su default (muebles_america) no cuenta como explícito."""
    site = resolve_run_site(
        case_id="CP_EC_VIU_CART_001",
        site_option="muebles_america",
        site_env=None,
        site_option_explicit=False,
        sites=_SITES,
    )
    assert site == "viu"


def test_conflicto_site_explicito_falla_explicito():
    with pytest.raises(ConfigError, match="Conflicto"):
        resolve_run_site(
            case_id="CP_EC_VIU_CART_001",
            site_option="muebles_america",
            site_env=None,
            site_option_explicit=True,
            sites=_SITES,
        )


def test_conflicto_env_falla_explicito():
    with pytest.raises(ConfigError, match="Conflicto"):
        resolve_run_site(
            case_id="CP_EC_MA_CART_001",
            site_option="muebles_america",
            site_env="viu",
            site_option_explicit=False,
            sites=_SITES,
        )
