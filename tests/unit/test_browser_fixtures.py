"""Pruebas del Browser Lifecycle: Playwright → Browser → Context → Page.

Sin conexión externa: Chromium local en headless y navegación a
about:blank. Seleccionables con ``pytest tests/unit -k fixture``.
"""

from dataclasses import replace

import pytest

from core.browser.browser_context import create_browser_context
from core.browser.browser_factory import launch_browser
from core.execution.execution_errors import ConfigError
from pages.muebles_america.home.home_page import HomePage

pytestmark = pytest.mark.unit


def test_fixture_browser_conectado(browser):
    """El perfil default lanza Chromium headless local."""
    assert browser.is_connected()


def test_fixture_context_aislado(context, browser):
    assert context in browser.contexts


def test_fixture_page_funcional(page):
    """La Page recibida opera sin salir a la red."""
    page.goto("about:blank")
    assert page.url == "about:blank"


def test_fixture_pages_factory_construye_page_objects(pages):
    """Los Page Objects reciben Page vía factory, sin elegir sitio."""
    assert isinstance(pages.home(), HomePage)


def test_fixture_navegador_no_soportado_falla_explicito(
    playwright_instance, execution_context
):
    """Selección futura de navegador: valor inválido → ConfigError."""
    bad_context = replace(execution_context, browser="navegador_inexistente")
    with pytest.raises(ConfigError):
        launch_browser(playwright_instance, bad_context)


def test_fixture_lifecycle_cierra_recursos_ante_fallo(
    playwright_instance, execution_context
):
    """El cleanup post-yield corre aunque el cuerpo del test falle."""
    browser = launch_browser(playwright_instance, execution_context)
    context = create_browser_context(browser, execution_context)
    page = context.new_page()
    try:
        with pytest.raises(AssertionError):
            raise AssertionError("fallo simulado del test")
    finally:
        page.close()
        context.close()
        browser.close()
    assert not browser.is_connected()
