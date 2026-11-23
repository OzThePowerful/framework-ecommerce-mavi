"""Locators internos de un Product Card (tile) — verificados en ambos sitios.

Se aplican con scope al tile (`tile.locator(...)`); no son selectores de
página completa.
"""


class ProductCardLocators:
    NAME = ".product-tile__name"
    LINK = "a.product-link[href*='.html']"
    PRICE = "[class*='default-price'] .price"
    ADD_TO_CART = "button.add-to-cart"
