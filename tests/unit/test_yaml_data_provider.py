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


def test_sitio_valido_prioriza_su_dataset(tmp_path):
    """Sitio con dataset propio: gana sobre el de common."""
    _write(tmp_path / "viu" / "products.yaml", "src: sitio")
    _write(tmp_path / "common" / "products.yaml", "src: comun")
    provider = YamlDataProvider("viu", data_root=tmp_path)
    assert provider.get_dataset("products") == {"src": "sitio"}


def test_sitio_inexistente_error_explicito(tmp_path):
    """Sitio sin carpeta ni fallback common: error que nombra el sitio."""
    provider = YamlDataProvider("sitio_falso", data_root=tmp_path)
    with pytest.raises(DataError, match="sitio_falso"):
        provider.get_dataset("products")


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


def test_registro_inexistente_error_explicito(tmp_path):
    _write(tmp_path / "viu" / "products.yaml", "uno: {}")
    provider = YamlDataProvider("viu", data_root=tmp_path)
    with pytest.raises(DataError, match="dos"):
        provider.get_record("products", "dos")
