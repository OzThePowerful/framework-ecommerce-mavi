"""Locators/identificadores del PDP — verificados idénticos en MA y VIU.

La fuente de datos comerciales es el estado del SPA
(`window.__INITIAL_STATE__.product.current`), no el markup: el SPA no
renderiza `h1` ni `span.price` con selectores semánticos (EC-SP01-008) y el
JSON-LD declara `OutOfStock` aunque el artículo sí tenga stock (desfasado).
"""


class PdpLocators:
    ADD_TO_CART = "button.add-to-cart:visible"
    CURRENT_PRODUCT_EXPR = (
        "window.__INITIAL_STATE__ && window.__INITIAL_STATE__.product"
        " ? window.__INITIAL_STATE__.product.current : null"
    )
