"""Ventana de promociones que aparece al agregar algunos artículos al carrito."""

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from pages.muebles_america.components.promotions_window.promotions_window_locators import (
    PromotionsWindowLocators,
)


class PromotionsWindowComponent:
    def __init__(self, page: Page) -> None:
        self.page = page

    def close_if_present(self, appear_timeout: int = 3000) -> None:
        """Solo aparece con algunos artículos: espera un margen corto; si no
        aparece continúa, si aparece la cierra y espera a que se retire el
        backdrop (que intercepta los clics)."""
        window = self.page.locator(PromotionsWindowLocators.ROOT).first
        try:
            window.wait_for(state="visible", timeout=appear_timeout)
        except PlaywrightTimeoutError:
            return  # Artículo sin promociones: no hay ventana que cerrar.

        window.locator(PromotionsWindowLocators.CLOSE_BUTTON).first.click()
        window.wait_for(state="hidden")
        self.page.locator(PromotionsWindowLocators.BACKDROP).first.wait_for(
            state="hidden"
        )
