"""Controles ejecutables de las reglas arquitectónicas (EC-SP01-001 §17)."""

import pytest

from tests.architecture import rules

pytestmark = pytest.mark.architecture


def _violations_importing(directory: str, forbidden: set[str]) -> dict:
    result = {}
    for path in rules.iter_py(directory):
        hits = rules.import_roots(rules.tree_of(path)) & forbidden
        if hits:
            result[str(path.relative_to(rules.ROOT))] = sorted(hits)
    return result


def _violations_calls(directory: str, forbidden: frozenset) -> dict:
    result = {}
    for path in rules.iter_py(directory):
        hits = rules.call_names(rules.tree_of(path)) & forbidden
        if hits:
            result[str(path.relative_to(rules.ROOT))] = sorted(hits)
    return result


def test_core_no_importa_capas_funcionales():
    violations = _violations_importing("core", set(rules.FUNCTIONAL_TOP_LEVELS))
    assert not violations, f"core importa capas funcionales: {violations}"


def test_data_providers_no_importan_pages():
    violations = _violations_importing("data_providers", {"pages"})
    assert not violations, f"data_providers importa pages: {violations}"


def test_repositories_no_importan_pages():
    violations = _violations_importing("repositories", {"pages"})
    assert not violations, f"repositories importa pages: {violations}"


def test_locators_no_contienen_acciones():
    violations = {}
    for path in sorted(rules.ROOT.rglob("*_locators.py")):
        tree = rules.tree_of(path)
        hits = rules.call_names(tree) & (rules.LOCATOR_ACTIONS | {"expect"})
        if hits or rules.contains_assert(tree):
            violations[str(path.relative_to(rules.ROOT))] = sorted(hits)
    assert not violations, f"locators con acciones/lógica: {violations}"


def test_page_objects_sin_asserts():
    violations = {}
    for path in rules.iter_py("pages"):
        if path.name.endswith("_locators.py"):
            continue
        tree = rules.tree_of(path)
        if rules.contains_assert(tree) or "expect" in rules.call_names(tree):
            violations[str(path.relative_to(rules.ROOT))] = True
    assert not violations, f"Page Objects con asserts/expect: {list(violations)}"


def test_workflows_sin_locators():
    violations = {}
    for path in rules.iter_py("workflows"):
        tree = rules.tree_of(path)
        calls = rules.call_names(tree) & rules.LOCATOR_ACCESSORS
        modules = rules.import_modules(tree)
        locator_imports = {m for m in modules if m.endswith("_locators")}
        if calls or locator_imports:
            violations[str(path.relative_to(rules.ROOT))] = sorted(
                calls | locator_imports
            )
    assert not violations, f"workflows con locators: {violations}"


def test_bdd_steps_sin_secuencias_playwright():
    violations = _violations_calls("tests/bdd/steps", rules.LOCATOR_ACCESSORS)
    assert not violations, f"steps BDD con locators: {violations}"


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


def test_sin_except_exception_tragado():
    violations = {}
    for path in rules.iter_all_framework_py():
        lines = rules.forbidden_except_lines(rules.tree_of(path))
        if lines:
            violations[str(path.relative_to(rules.ROOT))] = lines
    assert not violations, f"except Exception/bare tragados: {violations}"


def test_sin_print_en_framework():
    violations = {}
    for directory in rules.FRAMEWORK_DIRS:
        if directory == "scripts":  # las herramientas CLI sí reportan por stdout
            continue
        for path in rules.iter_py(directory):
            if "print" in rules.call_names(rules.tree_of(path)):
                violations[str(path.relative_to(rules.ROOT))] = True
    assert not violations, f"print() en framework (usar logging): {list(violations)}"


def test_sin_urls_en_capas_funcionales():
    violations = {}
    for directory in ("pages", "workflows", "tests", "fixtures"):
        for path in rules.iter_py(directory):
            if "architecture" in path.parts:
                continue
            hits = rules.url_literals(rules.tree_of(path))
            if hits:
                violations[str(path.relative_to(rules.ROOT))] = hits
    assert not violations, f"URLs literales en capas funcionales: {violations}"


def test_conftest_minimo():
    conftest = rules.ROOT / "conftest.py"
    lines = conftest.read_text(encoding="utf-8").splitlines()
    assert len(lines) <= 60, f"conftest.py con {len(lines)} líneas (máximo 60)"
