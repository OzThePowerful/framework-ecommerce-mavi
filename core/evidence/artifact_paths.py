"""Rutas de artefactos ancladas al proyecto (nunca al equipo de alguien)."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"


def run_artifacts_dir(run_id: str) -> Path:
    """Directorio de artefactos de una ejecución; lo crea si no existe."""
    path = ARTIFACTS_DIR / "runs" / run_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def allure_results_dir() -> Path:
    path = ARTIFACTS_DIR / "allure-results"
    path.mkdir(parents=True, exist_ok=True)
    return path
