"""Adjuntos Allure. No-op seguro si el plugin no está instalado."""

from pathlib import Path

try:
    import allure
except ImportError:  # allure-pytest es opcional fuera de la ejecución de pruebas
    allure = None


def attach_text(name: str, content: str) -> None:
    if allure is not None:
        allure.attach(content, name=name, attachment_type=allure.attachment_type.TEXT)


def attach_file(path: Path, name: str | None = None) -> None:
    if allure is not None and path.is_file():
        allure.attach.file(str(path), name=name or path.name)


def label(name: str, value: str) -> None:
    """Etiqueta de contexto para el reporte Allure del test actual."""
    if allure is not None:
        allure.dynamic.label(name, value)


def attach_failure_artifacts(artifacts: dict) -> None:
    """Adjunta a Allure la evidencia capturada ante un fallo."""
    screenshot = artifacts.get("screenshot")
    if screenshot:
        attach_file(screenshot, name="failure-screenshot")
    if artifacts.get("url_log"):
        attach_text("current_url", artifacts["url_log"].read_text(encoding="utf-8"))
    if artifacts.get("exception_log"):
        attach_text(
            "exception", artifacts["exception_log"].read_text(encoding="utf-8")
        )
