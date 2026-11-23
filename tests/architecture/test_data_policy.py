"""Política de datos y configuración (EC-SP01-007)."""

import pytest

from tests.architecture import rules

pytestmark = pytest.mark.architecture


def test_data_providers_no_importan_pages():
    violations = rules.violations_importing("data_providers", {"pages"})
    assert not violations, f"data_providers importa pages: {violations}"


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
