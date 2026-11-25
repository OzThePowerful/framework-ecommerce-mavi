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

    def is_navigation_accessible(self) -> bool:
        """La navegación principal (menú de departamentos y links) está
        visible — es la vía para comenzar una compra."""
        return self.page.locator(HeaderLocators.NAV).count() > 0

    def wait_until_ready(self) -> None:
        """Estado utilizable del header: barra visible y buscador disponible."""
        self.page.locator(HeaderLocators.VISIBLE_ROOT).first.wait_for(
            state="visible"
        )
        self.search_box().wait_for(state="visible")
