"""Pruebas unitarias del YamlDataProvider."""

from pathlib import Path

import pytest

from core.execution.execution_errors import DataError
from data_providers.yaml_data_provider import YamlDataProvider

pytestmark = pytest.mark.unit


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_dataset_del_sitio(tmp_path):
    _write(tmp_path / "muebles_america" / "products.yaml", "item: 1")
    provider = YamlDataProvider("muebles_america", data_root=tmp_path)
    assert provider.get_dataset("products") == {"item": 1}


def test_fallback_common(tmp_path):
    _write(tmp_path / "common" / "shared.yaml", "shared: true")
    provider = YamlDataProvider("viu", data_root=tmp_path)
    assert provider.get_dataset("shared") == {"shared": True}


def test_dataset_inexistente_error_explicito(tmp_path):
    provider = YamlDataProvider("viu", data_root=tmp_path)
    with pytest.raises(DataError):
        provider.get_dataset("inexistente")


def test_yaml_invalido_error_explicito(tmp_path):
    _write(tmp_path / "viu" / "broken.yaml", "a: [unclosed")
    provider = YamlDataProvider("viu", data_root=tmp_path)
    with pytest.raises(DataError):
        provider.get_dataset("broken")
