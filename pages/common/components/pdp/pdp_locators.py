"""Locators/identificadores del PDP — verificados idénticos en MA y VIU.

La fuente de datos comerciales es el estado del SPA
(`window.__INITIAL_STATE__.product.current`), no el markup: el SPA no
renderiza `h1` ni `span.price` con selectores semánticos (EC-SP01-008) y el
JSON-LD declara `OutOfStock` aunque el artículo sí tenga stock (desfasado).
"""


class PdpLocators:
    ADD_TO_CART = "button.add-to-cart:visible"
    # Etiqueta verde de stock: verdad observable — el JSON del SPA llega
    # desfasado (p.ej. declara in-stock un agotado). Cubre todas las
    # variantes positivas: "Disponible", "Solo queda 1", "Solo quedan N".
    AVAILABILITY_BADGE = "span.fw-700.cl-green-label:visible"
    # Marcador negativo: el agotado se etiqueta en cl-accent, no en verde.
    OUT_OF_STOCK_BADGE = (
        "span.fw-700.cl-accent:has-text('Agotado'):visible"
    )
    CURRENT_PRODUCT_EXPR = (
        "window.__INITIAL_STATE__ && window.__INITIAL_STATE__.product"
        " ? window.__INITIAL_STATE__.product.current : null"
    )
