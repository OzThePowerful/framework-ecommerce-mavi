"""Componente Header: los pages lo componen; sin herencia profunda."""

from playwright.sync_api import Locator, Page

from pages.common.components.header.header_locators import HeaderLocators


class HeaderComponent:
    def __init__(self, page: Page) -> None:
        self.page = page

    def is_visible(self) -> bool:
        return self.page.locator(HeaderLocators.VISIBLE_ROOT).count() > 0

    def search_box(self) -> Locator:
        """Input de búsqueda del header (instancia visible del viewport)."""
        return self.page.locator(HeaderLocators.SEARCH_INPUT)

    def open_cart(self) -> None:
        """Abre el minicart desde el botón del header."""
        self.page.locator(HeaderLocators.CART_BUTTON).first.click()

    def is_cart_accessible(self) -> bool:
        return self.page.locator(HeaderLocators.CART_BUTTON).count() > 0

    def is_account_accessible(self) -> bool:
        return self.page.locator(HeaderLocators.ACCOUNT_LINK).count() > 0

    def is_search_submittable(self) -> bool:
        return self.page.locator(HeaderLocators.SEARCH_SUBMIT).count() > 0

    def is_search_usable(self) -> bool:
        """Buscador visible y habilitado para capturar un término."""
        box = self.search_box().first
        return box.is_visible() and box.is_enabled()

    def is_cart_available(self) -> bool:
        """Acceso al carrito visible y habilitado."""
        cart = self.page.locator(HeaderLocators.CART_BUTTON).first
        return cart.is_visible() and cart.is_enabled()

    def is_logo_visible(self) -> bool:
        """Logo de la marca (link a inicio) visible en el header."""
        return self.page.locator(HeaderLocators.HOME_LOGO).first.is_visible()

    def main_nav_items(self) -> list[str]:
        """Textos de los elementos habilitados de la navegación principal."""
        items = self.page.locator(HeaderLocators.MAIN_NAV_ITEMS)
        return [
            items.nth(i).inner_text().strip()
            for i in range(items.count())
            if items.nth(i).is_enabled()
        ]

    def wait_until_ready(self) -> None:
        """Estado utilizable del header: barra visible y buscador disponible."""
        self.page.locator(HeaderLocators.VISIBLE_ROOT).first.wait_for(
            state="visible"
        )
        self.search_box().wait_for(state="visible")
