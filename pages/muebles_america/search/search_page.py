"""Listado de productos (grid de categoría/búsqueda) de Muebles América."""

from pages.base_page import BasePage
from pages.muebles_america.search.search_locators import SearchLocators


class SearchPage(BasePage):
    def open_product(self, product_name: str) -> None:
        """Abre la PDP del tile cuyo texto contiene `product_name`."""
        tile = self.page.locator(SearchLocators.PRODUCT_TILE).filter(
            has_text=product_name
        )
        tile.first.click()
