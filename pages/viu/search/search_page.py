"""Búsqueda y resultados de VIU: fachada sobre componentes common."""

from playwright.sync_api import Page

from core.execution.execution_context import ExecutionContext
from pages.base_page import BasePage
from pages.common.components.product_card.product_card import ProductCard
from pages.common.components.search.search_component import SearchComponent
from pages.viu.search.search_locators import SearchLocators


class SearchPage(BasePage):
    def __init__(self, page: Page, context: ExecutionContext) -> None:
        super().__init__(page, context)
        self.search_component = SearchComponent(page)

    def search(self, term: str) -> None:
        self.search_component.search(term)

    def result_count(self) -> int:
        return self.search_component.result_count()

    def cards(self) -> list[ProductCard]:
        return self.search_component.cards()

    def load_all_cards(self) -> int:
        """Scroll infinito hasta que el grid deje de crecer o alcance el
        total del contador; devuelve cuántas cards cargó."""
        return self.search_component.load_all_cards()

    def eligible_card(self) -> ProductCard | None:
        return self.search_component.eligible_card()

    def open_product(self, product_name: str) -> None:
        """Abre la PDP del tile cuyo texto contiene `product_name`."""
        tile = self.page.locator(SearchLocators.PRODUCT_TILE).filter(
            has_text=product_name
        )
        tile.first.click()
