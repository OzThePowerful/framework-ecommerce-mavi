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
    CART_ROUTE = "/checkout/cart"
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

    # CTA "Comprar ahora" del minicart — las clases de plataforma son las
    # mismas en MA y VIU; `:visible` discrimina la copia móvil oculta.
    BUY_NOW_BUTTON = "button.buy-now:visible"

    # Ítems del estado del SPA (`cart.cartItems`): la confirmación real del
    # add es el registro sincronizado (`server_item_id`), no el toast —
    # verificado en MA (CP_EC_MA_CART_001) y VIU (probe: server_item_id
    # 313783 para MIDE00067 en stage VIU).
    CART_ITEMS_EXPR = (
        "window.__INITIAL_STATE__ && window.__INITIAL_STATE__.cart"
        " ? (window.__INITIAL_STATE__.cart.cartItems || []).map(i => ({"
        "sku: i.sku, qty: i.qty, name: i.name,"
        " server_item_id: i.server_item_id || null}))"
        " : []"
    )
