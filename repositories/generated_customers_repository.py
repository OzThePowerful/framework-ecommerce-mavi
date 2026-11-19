"""Clientes generados durante la ejecución (artefactos, no datasets)."""

import json
from pathlib import Path

from repositories.execution_repository import GENERATED_DIR, atomic_write_json


class GeneratedCustomersRepository:
    def __init__(self, run_id: str, base_dir: Path | None = None) -> None:
        self._path = (base_dir or GENERATED_DIR) / run_id / "customers.json"

    def add(self, customer: dict) -> Path:
        customers = self._read_all()
        customers.append(customer)
        atomic_write_json(self._path, {"customers": customers})
        return self._path

    def _read_all(self) -> list:
        if not self._path.is_file():
            return []
        data = json.loads(self._path.read_text(encoding="utf-8"))
        return data.get("customers", [])
