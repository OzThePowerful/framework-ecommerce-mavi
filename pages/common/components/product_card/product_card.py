"""Product Card: abstracción del tile de producto en grids de resultados.

La equivalencia entre MA y VIU está verificada (EC-SP01-008/010): ambos
renderizan `div.product-tile` con nombre, link `.html`, precio de contado
y botón de agregar al carrito.
"""

import re
from decimal import Decimal, InvalidOperation

from playwright.sync_api import Locator

from pages.common.components.product_card.product_card_locators import (
    ProductCardLocators,
)


class ProductCard:
    """Envuelve el Locator del tile; los tests/workflows leen propiedades."""

    def __init__(self, tile: Locator) -> None:
        self._tile = tile

    def is_visible(self) -> bool:
        return self._tile.is_visible()

    def name(self) -> str:
        return (self._tile.locator(ProductCardLocators.NAME).inner_text() or "").strip()

    def identifier(self) -> str:
        """Identificador navegable: href de la PDP (contiene el slug/SKU)."""
        return self._tile.locator(ProductCardLocators.LINK).get_attribute("href") or ""

    def price(self) -> Decimal:
        """Precio de contado del tile; Decimal('0') si no es parseable."""
        text = self._tile.locator(ProductCardLocators.PRICE).inner_text() or ""
        match = re.search(r"([\d,]+(?:\.\d+)?)", text)
        if not match:
            return Decimal("0")
        try:
            return Decimal(match.group(1).replace(",", ""))
        except InvalidOperation:
            return Decimal("0")

    def is_purchasable(self) -> bool:
        """El tile muestra acción de compra (botón agregar al carrito).

        Nota: el botón NO refleja stock — en VIU/MA aparece deshabilitado
        en todas las cards (la compra se decide en la PDP).
        """
        return (
            self._tile.locator(ProductCardLocators.ADD_TO_CART).count() > 0
        )

    def open(self) -> None:
        """Abre la PDP del producto y espera la navegación del SPA."""
        self._tile.locator(ProductCardLocators.LINK).click()
        self._tile.page.wait_for_url("**/*.html**", timeout=15000)
