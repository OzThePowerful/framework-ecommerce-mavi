"""Proveedor Excel: intercambiable con YAML sin tocar consumidores."""

from pathlib import Path

from core.execution.execution_errors import DataError
from data_providers.base_data_provider import BaseDataProvider

try:
    import openpyxl
except ImportError:  # openpyxl se declara en requirements.in
    openpyxl = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ExcelDataProvider(BaseDataProvider):
    """Lee data/<site>/<name>.xlsx con fallback a data/common/<name>.xlsx.

    La primera fila se interpreta como encabezados; cada fila siguiente
    se expone como dict.
    """

    def __init__(self, site: str, data_root: Path | None = None) -> None:
        if openpyxl is None:
            raise DataError("ExcelDataProvider requiere 'openpyxl' instalado.")
        self._site = site
        self._root = data_root or PROJECT_ROOT / "data"

    def get_dataset(self, name: str) -> list[dict]:
        path = self._resolve(name)
        workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
        try:
            sheet = workbook.active
            rows = sheet.iter_rows(values_only=True)
            headers = next(rows, None)
            if not headers:
                return []
            return [dict(zip(headers, row, strict=False)) for row in rows]
        finally:
            workbook.close()

    def get_record(self, dataset: str, key: str) -> dict:
        for item in self.get_dataset(dataset):
            if key in (item.get("id"), item.get("key"), item.get("name")):
                return item
        raise DataError(f"Registro '{key}' ausente en dataset '{dataset}'")

    def _resolve(self, name: str) -> Path:
        candidates = [
            self._root / self._site / f"{name}.xlsx",
            self._root / "common" / f"{name}.xlsx",
        ]
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        raise DataError(
            f"Dataset '{name}' inexistente para sitio '{self._site}'. "
            f"Rutas probadas: {[str(c) for c in candidates]}"
        )
