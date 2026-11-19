"""Proveedor YAML: resolución por sitio con fallback a common."""

from pathlib import Path
from typing import Any

import yaml

from core.execution.execution_errors import DataError
from data_providers.base_data_provider import BaseDataProvider

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class YamlDataProvider(BaseDataProvider):
    """Lee data/<site>/<name>.yaml con fallback a data/common/<name>.yaml."""

    def __init__(self, site: str, data_root: Path | None = None) -> None:
        self._site = site
        self._root = data_root or PROJECT_ROOT / "data"

    def get_dataset(self, name: str) -> Any:
        path = self._resolve(name)
        try:
            return yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise DataError(f"YAML inválido en {path}: {exc}") from exc

    def get_record(self, dataset: str, key: str) -> Any:
        data = self.get_dataset(dataset)
        if isinstance(data, dict) and key in data:
            return data[key]
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and key in (
                    item.get("id"),
                    item.get("key"),
                    item.get("name"),
                ):
                    return item
        raise DataError(f"Registro '{key}' ausente en dataset '{dataset}'")

    def _resolve(self, name: str) -> Path:
        candidates = [
            self._root / self._site / f"{name}.yaml",
            self._root / "common" / f"{name}.yaml",
        ]
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        raise DataError(
            f"Dataset '{name}' inexistente para sitio '{self._site}'. "
            f"Rutas probadas: {[str(c) for c in candidates]}"
        )
