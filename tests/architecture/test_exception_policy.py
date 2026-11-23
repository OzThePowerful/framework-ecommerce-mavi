"""Política de errores y diagnóstico (EC-SP01-007)."""

import pytest

from tests.architecture import rules

pytestmark = pytest.mark.architecture


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
