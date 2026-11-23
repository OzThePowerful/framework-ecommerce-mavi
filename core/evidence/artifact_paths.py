"""Rutas de artefactos ancladas al proyecto (nunca al equipo de alguien)."""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"

CASE_SUBDIRS = ("screenshots", "logs", "traces", "videos")

_UNSAFE_CHARS = re.compile(r"[^A-Za-z0-9_.\-]+")


def _safe_name(name: str) -> str:
    """Nombre de directorio válido en Windows/Linux para un Case ID."""
    return _UNSAFE_CHARS.sub("_", name)


def run_artifacts_dir(run_id: str) -> Path:
    """Directorio de artefactos de una ejecución; lo crea si no existe."""
    path = ARTIFACTS_DIR / "runs" / run_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def case_artifacts_dir(run_id: str, case_id: str) -> Path:
    """artifacts/runs/<run_id>/<case_id>/ con subdirs de evidencia.

    Las subcarpetas de artefactos pesados (traces, videos) quedan
    preparadas aunque su captura no esté activa todavía.
    """
    path = run_artifacts_dir(run_id) / _safe_name(case_id)
    for subdir in CASE_SUBDIRS:
        (path / subdir).mkdir(parents=True, exist_ok=True)
    return path


def allure_results_dir() -> Path:
    path = ARTIFACTS_DIR / "allure-results"
    path.mkdir(parents=True, exist_ok=True)
    return path
