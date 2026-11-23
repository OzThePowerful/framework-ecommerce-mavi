"""Componente Blockers: detecta y descarta bloqueos transversales.

Cubre el banner de cookies (idéntico en MA y VIU) y overlays/backdrops
genéricos. Los bloqueos específicos de marca (p.ej. ventana promocional de
MA) viven en los componentes de cada sitio.
"""

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from pages.common.components.blockers.blocker_locators import BlockerLocators


class BlockerComponent:
    def __init__(self, page: Page) -> None:
        self.page = page

    def dismiss_cookies(self) -> bool:
        """Cierra el banner de cookies si está visible."""
        button = self.page.locator(BlockerLocators.COOKIE_CLOSE_BUTTON).first
        try:
            button.click(timeout=3000)
        except PlaywrightTimeoutError:
            return False
        return True

    def has_overlay(self) -> bool:
        """Detecta backdrops/overlays que interceptan la interacción."""
        return self.page.locator(BlockerLocators.OVERLAY).count() > 0
