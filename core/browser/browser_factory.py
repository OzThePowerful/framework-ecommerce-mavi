"""Creación del navegador a partir del ExecutionContext."""

from playwright.sync_api import Browser, Playwright

from core.execution.execution_context import ExecutionContext
from core.execution.execution_errors import ConfigError


def launch_browser(playwright: Playwright, context: ExecutionContext) -> Browser:
    """Lanza el navegador declarado en el contexto de ejecución."""
    browser_type = getattr(playwright, context.browser, None)
    if browser_type is None:
        raise ConfigError(
            f"Navegador '{context.browser}' no soportado. "
            "Válidos: chromium, firefox, webkit."
        )
    return browser_type.launch(headless=context.headless)
