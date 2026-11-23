"""Política de Page Objects: fachadas sin validaciones (EC-SP01-007)."""

import pytest

from tests.architecture import rules

pytestmark = pytest.mark.architecture


def test_page_objects_sin_asserts():
    violations = {}
    for path in rules.iter_py("pages"):
        if path.name.endswith("_locators.py"):
            continue
        tree = rules.tree_of(path)
        if rules.contains_assert(tree) or "expect" in rules.call_names(tree):
            violations[str(path.relative_to(rules.ROOT))] = True
    assert not violations, f"Page Objects con asserts/expect: {list(violations)}"
