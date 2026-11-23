"""Política de locators: selectores separados de la lógica (EC-SP01-007)."""

import pytest

from tests.architecture import rules

pytestmark = pytest.mark.architecture


def test_locators_no_contienen_acciones():
    violations = {}
    for path in sorted(rules.ROOT.rglob("*_locators.py")):
        tree = rules.tree_of(path)
        hits = rules.call_names(tree) & (rules.LOCATOR_ACTIONS | {"expect"})
        if hits or rules.contains_assert(tree):
            violations[str(path.relative_to(rules.ROOT))] = sorted(hits)
    assert not violations, f"locators con acciones/lógica: {violations}"


def test_tests_sin_locators_directos():
    violations = {}
    for path in rules.iter_py("tests"):
        if "architecture" in path.parts or "steps" in path.parts:
            continue
        if not path.name.startswith("test_"):
            continue
        hits = rules.call_names(rules.tree_of(path)) & rules.LOCATOR_ACCESSORS
        if hits:
            violations[str(path.relative_to(rules.ROOT))] = sorted(hits)
    assert not violations, f"tests usando locators directos: {violations}"


def test_bdd_steps_sin_secuencias_playwright():
    violations = rules.violations_calls("tests/bdd/steps", rules.LOCATOR_ACCESSORS)
    assert not violations, f"steps BDD con locators: {violations}"
