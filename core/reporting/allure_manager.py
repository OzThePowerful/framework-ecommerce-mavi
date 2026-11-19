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
