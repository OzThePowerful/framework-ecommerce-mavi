"""Política de workflows: coordinación sin UI ni asserts (EC-SP01-007)."""

import pytest

from tests.architecture import rules

pytestmark = pytest.mark.architecture


def test_workflows_sin_locators():
    violations = {}
    for path in rules.iter_py("workflows"):
        tree = rules.tree_of(path)
        calls = rules.call_names(tree) & rules.LOCATOR_ACCESSORS
        locator_imports = {
            m for m in rules.import_modules(tree) if m.endswith("_locators")
        }
        if calls or locator_imports:
            violations[str(path.relative_to(rules.ROOT))] = sorted(
                calls | locator_imports
            )
    assert not violations, f"workflows con locators: {violations}"


def test_workflows_sin_asserts():
    violations = {}
    for path in rules.iter_py("workflows"):
        tree = rules.tree_of(path)
        if rules.contains_assert(tree) or "expect" in rules.call_names(tree):
            violations[str(path.relative_to(rules.ROOT))] = True
    assert not violations, f"workflows con asserts/expect: {list(violations)}"
