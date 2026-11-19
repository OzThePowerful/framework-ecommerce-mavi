"""Repositorio de estado de ejecución con escritura atómica."""

import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIR = PROJECT_ROOT / "artifacts" / "generated"


def atomic_write_json(path: Path, payload: dict) -> None:
    """Escritura atómica (tmp + rename) segura ante ejecución paralela."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    tmp_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    os.replace(tmp_path, path)


class ExecutionRepository:
    """Persiste estado bajo artifacts/generated/<run_id>/."""

    def __init__(self, run_id: str, base_dir: Path | None = None) -> None:
        self._dir = (base_dir or GENERATED_DIR) / run_id

    def save_state(self, name: str, payload: dict) -> Path:
        path = self._dir / f"{name}.json"
        atomic_write_json(path, payload)
        return path
