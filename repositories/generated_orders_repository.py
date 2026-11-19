"""Órdenes generadas durante la ejecución (artefactos, no datasets)."""

import json
from pathlib import Path

from repositories.execution_repository import GENERATED_DIR, atomic_write_json


class GeneratedOrdersRepository:
    def __init__(self, run_id: str, base_dir: Path | None = None) -> None:
        self._path = (base_dir or GENERATED_DIR) / run_id / "orders.json"

    def add(self, order: dict) -> Path:
        orders = self._read_all()
        orders.append(order)
        atomic_write_json(self._path, {"orders": orders})
        return self._path

    def _read_all(self) -> list:
        if not self._path.is_file():
            return []
        data = json.loads(self._path.read_text(encoding="utf-8"))
        return data.get("orders", [])
