"""Componente Search: ejecutar búsqueda y leer el grid de resultados.

Compartido por MA y VIU (mismo SPA): el input/submit vive en el header
común y los resultados son `div.product-tile` + contador textual.
"""

import re

from playwright.sync_api import Page

from pages.common.components.header.header_locators import HeaderLocators
from pages.common.components.product_card.product_card import ProductCard
from pages.common.components.search.search_locators import SearchLocators


class SearchComponent:
    def __init__(self, page: Page) -> None:
        self.page = page

    def search(self, term: str) -> None:
        """Captura el término y ejecuta la búsqueda desde el header."""
        box = self.page.locator(HeaderLocators.SEARCH_INPUT)
        box.fill(term)
        self.page.locator(HeaderLocators.SEARCH_SUBMIT).first.click()
        self.wait_for_results()

    def wait_for_results(self) -> None:
        """Espera observable: el contador 'N resultados de búsqueda' aparece
        tanto con resultados como con cero."""
        self.page.locator(SearchLocators.RESULT_COUNT).first.wait_for(
            state="visible"
        )

    def result_count(self) -> int:
        """Total declarado por el sitio (puede diferir de tiles por paginación)."""
        text = (
            self.page.locator(SearchLocators.RESULT_COUNT).first.inner_text() or ""
        )
        match = re.search(r"(\d+)", text)
        return int(match.group(1)) if match else -1

    def cards(self) -> list[ProductCard]:
        """Product Cards renderizadas en el grid."""
        tiles = self.page.locator(SearchLocators.GRID)
        return [ProductCard(tiles.nth(i)) for i in range(tiles.count())]

    def load_all_cards(self, max_rounds: int = 15, pause_ms: int = 800) -> int:
        """Paginación por scroll infinito: baja hasta el último tile visible
        para disparar la carga, hasta que el grid deje de crecer o alcance
        el total declarado por el contador. Devuelve cuántas cards cargó."""
        tiles = self.page.locator(SearchLocators.GRID)
        target = self.result_count()
        loaded = tiles.count()
        for _ in range(max_rounds):
            if target >= 0 and loaded >= target:
                break
            if loaded:
                tiles.nth(loaded - 1).scroll_into_view_if_needed()
            else:
                self.page.mouse.wheel(0, 4000)
            self.page.wait_for_timeout(pause_ms)
            current = tiles.count()
            if current == loaded:
                # Reintento con wheel por si el último tile no disparó el lazy load.
                self.page.mouse.wheel(0, 2000)
                self.page.wait_for_timeout(pause_ms)
                current = tiles.count()
                if current == loaded:
                    break
            loaded = current
        return loaded

    def eligible_card(self) -> ProductCard | None:
        """Primera card elegible por criterios observables (no posicional):
        visible, navegable (href), precio válido y comprable."""
        for card in self.cards():
            if (
                card.is_visible()
                and card.identifier()
                and card.price() > 0
                and card.is_purchasable()
            ):
                return card
        return None
