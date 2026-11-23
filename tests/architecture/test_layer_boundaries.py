"""Fronteras entre capas y dependencias circulares (EC-SP01-007)."""

import pytest

from tests.architecture import rules

pytestmark = pytest.mark.architecture


def test_core_no_importa_capas_funcionales():
    violations = rules.violations_importing(
        "core", set(rules.FUNCTIONAL_TOP_LEVELS)
    )
    assert not violations, f"core importa capas funcionales: {violations}"


def test_repositories_no_importan_pages():
    violations = rules.violations_importing("repositories", {"pages"})
    assert not violations, f"repositories importa pages: {violations}"


def test_sin_dependencias_circulares():
    cycles = rules.find_cycles(rules.module_graph())
    assert not cycles, f"dependencias circulares: {cycles}"


def test_conftest_minimo():
    conftest = rules.ROOT / "conftest.py"
    lines = conftest.read_text(encoding="utf-8").splitlines()
    assert len(lines) <= 60, f"conftest.py con {len(lines)} líneas (máximo 60)"
