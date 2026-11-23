"""Pruebas negativas del propio gate (EC-SP01-007).

Cada detector debe fallar ante código violador sintético y pasar con
código limpio: una regla que nunca detecta no protege nada.
"""

import pytest

from tests.architecture import rules

pytestmark = pytest.mark.architecture


def test_detector_except_tragado_flag_e_limpia():
    bad = "try:\n    x()\nexcept Exception:\n    pass\n"
    assert rules.forbidden_except_lines(rules.tree_of_source(bad))
    good = "try:\n    x()\nexcept OSError:\n    raise\n"
    assert not rules.forbidden_except_lines(rules.tree_of_source(good))


def test_detector_asserts_flag_e_limpia():
    assert rules.contains_assert(rules.tree_of_source("assert x"))
    assert not rules.contains_assert(rules.tree_of_source("x = 1"))


def test_detector_imports_flag_e_limpia():
    bad = "import pages\nimport workflows\n"
    assert {"pages", "workflows"} <= rules.import_roots(
        rules.tree_of_source(bad)
    )
    assert not (
        rules.import_roots(rules.tree_of_source("import domain\n"))
        & rules.FUNCTIONAL_TOP_LEVELS
    )


def test_detector_locators_flag_e_limpia():
    calls = rules.call_names(rules.tree_of_source("page.locator('div')"))
    assert "locator" in calls
    assert "locator" not in rules.call_names(
        rules.tree_of_source("page.close()")
    )


def test_detector_urls_flag_e_limpia():
    assert rules.url_literals(rules.tree_of_source('u = "https://ejemplo.mx"'))
    assert not rules.url_literals(rules.tree_of_source('u = "sin-url"'))


def test_detector_ciclos_flag_e_limpia():
    assert rules.find_cycles({"a": {"b"}, "b": {"a"}})
    assert not rules.find_cycles(
        {"a": {"b"}, "b": {"c"}, "c": set()}
    )
