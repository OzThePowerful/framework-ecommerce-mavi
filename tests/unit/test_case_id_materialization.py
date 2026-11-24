"""Pruebas del materializador de Case IDs BDD (fixtures/execution)."""

import pytest

from fixtures.execution_fixtures import case_id_from_tags


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
