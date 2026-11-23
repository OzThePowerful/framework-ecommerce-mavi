"""Locators de minicart y página de carrito — verificados idénticos en MA y VIU.

La página real del carrito es /checkout/cart en ambas marcas; el minicart
(drawer) la alcanza vía el CTA "Ir al carrito de compras".
"""


class CartLocators:
    # Minicart (drawer del header)
    OPEN_MINICART = "header:visible button[aria-label='Abrir minicart']"
    MINICART_ITEM = ".product-minicart"
    GO_TO_CART = "a[href*='checkout/cart']:has-text('carrito')"

    # Página de carrito (/checkout/cart)
    CART_ROOT = ".shopping-cart-products"
    ITEM_ROW = ".shopping-tile"
    ITEM_SKU = ".sku"  # texto "SKU#: XXXX"
    ITEM_NAME = ".name"
    ITEM_QTY = ".product-quantity.counter"
    ITEM_PRICE_CURRENT = "span.price.cl-accent"
    ITEM_PRICE_CROSSED = "span.price.line-through"
    ITEM_REMOVE = "button.trash"

    # Resumen
    SUMMARY = "div.expansion-panel:has-text('Resumen de compra')"
    TOTAL_PRODUCTS = ".total-products"  # "Total de productos N"
    TOTAL_VALUE = ".total-price-value"
    CONTINUE = "role=button[name='Pagar']"
