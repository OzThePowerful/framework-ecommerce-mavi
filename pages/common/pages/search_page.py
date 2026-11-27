"""Búsqueda y resultados: fachada base compartida por las marcas."""

from playwright.sync_api import Page

from core.execution.execution_context import ExecutionContext
from pages.base_page import BasePage
from pages.common.components.product_card.product_card import ProductCard
from pages.common.components.search.search_component import SearchComponent
from pages.common.components.search.search_locators import SearchLocators


class CommonSearchPage(BasePage):
    def __init__(self, page: Page, context: ExecutionContext) -> None:
        super().__init__(page, context)
        self.search_component = SearchComponent(page)

    def search(self, term: str) -> None:
        self.search_component.search(term)

    def type_term(self, term: str) -> None:
        self.search_component.type_term(term)

    def typed_term(self) -> str:
        return self.search_component.typed_term()

    def submit_search(self) -> None:
        self.search_component.submit_search()

    def is_results_view_ready(self) -> bool:
        return self.search_component.is_results_view_ready()

    def results_query(self) -> str | None:
        return self.search_component.results_query()

    def visible_card_count(self) -> int:
        return self.search_component.visible_card_count()

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

    def eligible_cards(self, max_cards: int = 4) -> list[ProductCard]:
        return self.search_component.eligible_cards(max_cards)

    def open_product(self, product_name: str) -> None:
        """Abre la PDP del tile cuyo texto contiene `product_name`."""
        tile = self.page.locator(SearchLocators.GRID).filter(
            has_text=product_name
        )
        tile.first.click()
        self.page.wait_for_url("**/*.html**", timeout=15000)

    def back_to_results(self) -> None:
        """Regresa a la PLP tras abrir una PDP; el SPA re-renderiza el grid."""
        self.page.go_back()
        self.page.locator(SearchLocators.GRID).first.wait_for(
            state="visible", timeout=15000
        )
