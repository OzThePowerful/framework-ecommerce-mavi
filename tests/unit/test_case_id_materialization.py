"""Pruebas del materializador de Case IDs BDD (fixtures/execution)."""

import pytest

from fixtures.execution_fixtures import case_id_from_tags, keep_for_site

SITES = {"muebles_america", "viu", "mavi"}


@pytest.mark.parametrize(
    ("tags", "site_code", "expected"),
    [
        ({"SEARCH_001"}, "MA", "CP_EC_MA_SEARCH_001"),
        ({"E2E_001"}, "VIU", "CP_EC_VIU_E2E_001"),
        ({"pending", "PAY_002", "bdd"}, "MA", "CP_EC_MA_PAY_002"),
        ({"CART_001", "regression"}, "VIU", "CP_EC_VIU_CART_001"),
    ],
)
def test_materializa_el_case_id(tags, site_code, expected):
    assert case_id_from_tags(tags, site_code) == expected


@pytest.mark.parametrize(
    "tags",
    [
        set(),                          # sin tag → sin materialización
        {"regression"},                 # tags que no son de caso
        {"SEARCH_001", "SEARCH_002"},   # más de un tag de caso → ambiguo
        {"search_001"},                 # minúsculas no son Case ID
        {"HOME_1"},                     # formato inválido
    ],
)
def test_sin_case_id_no_materializa(tags):
    assert case_id_from_tags(tags, "MA") is None


# --- Alcance por marca (MA-AISLAMIENTO-001) ---------------------------------
COMMON_HOME = {"HOME_001"}
MA_HOME = {"HOME_001", "muebles_america", "smoke", "home"}
COMMON_CART = {"CART_001"}


def test_escenario_de_marca_reemplaza_al_comun_en_su_marca():
    assert keep_for_site([COMMON_HOME, MA_HOME], "muebles_america", SITES) == [
        False,
        True,
    ]


def test_otra_marca_conserva_el_comun_y_descarta_el_de_marca():
    assert keep_for_site([COMMON_HOME, MA_HOME], "viu", SITES) == [True, False]


def test_comun_sin_override_se_conserva_en_todas_las_marcas():
    for site in ("muebles_america", "viu"):
        assert keep_for_site([COMMON_CART, MA_HOME], site, SITES)[0] is True


def test_items_sin_tags_se_conservan():
    assert keep_for_site([set(), {"unit"}], "viu", SITES) == [True, True]


def test_override_solo_afecta_su_case_id():
    tags = [{"SEARCH_001"}, {"SEARCH_002"}, {"SEARCH_001", "muebles_america"}]
    assert keep_for_site(tags, "muebles_america", SITES) == [False, True, True]
