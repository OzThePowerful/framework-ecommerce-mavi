"""Gestión de evidencias de ejecución (screenshots, texto, JSON)."""

import json
from pathlib import Path

from core.evidence.artifact_paths import run_artifacts_dir


class EvidenceManager:
    """Persiste evidencias bajo artifacts/runs/<run_id>/."""

    def __init__(self, run_id: str) -> None:
        self._base = run_artifacts_dir(run_id)

    def save_screenshot(self, page, name: str) -> Path:
        path = self._base / "screenshots" / f"{name}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(path), full_page=True)
        return path

    def save_text(self, name: str, content: str) -> Path:
        path = self._base / f"{name}.txt"
        path.write_text(content, encoding="utf-8")
        return path

    def save_json(self, name: str, payload: dict) -> Path:
        path = self._base / f"{name}.json"
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return path
