"""Locators/identificadores del PDP — verificados idénticos en MA y VIU.

La fuente de datos comerciales es el estado del SPA
(`window.__INITIAL_STATE__.product.current`), no el markup: el SPA no
renderiza `h1` ni `span.price` con selectores semánticos (EC-SP01-008) y el
JSON-LD declara `OutOfStock` aunque el artículo sí tenga stock (desfasado).

Etiqueta de disponibilidad (regla de negocio, verificada en stage MA y
VIU — CP_EC_MA_PDP_001): `Disponible`, `Agotado` o `Solo queda N`
(N bajo un umbral configurable en backend). Se localiza por texto, no
por clase de color. Es la fuente de verdad para el cliente: el estado del
SPA puede decir `is_in_stock` en un artículo que la PDP marca Agotado.
"""


class PdpLocators:
    ADD_TO_CART = "button.add-to-cart:visible"
    AVAILABILITY_LABEL = (
        "span:text-matches('^(Disponible|Agotado|Solo queda [0-9]+)$', 'i')"
        ":visible"
    )
    CURRENT_PRODUCT_EXPR = (
        "window.__INITIAL_STATE__ && window.__INITIAL_STATE__.product"
        " ? window.__INITIAL_STATE__.product.current : null"
    )
