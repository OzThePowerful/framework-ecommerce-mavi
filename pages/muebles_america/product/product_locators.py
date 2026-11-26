"""Locators de la PDP de Muebles América.

Los de la ventana de promociones viven en components/promotions_window/.

Etiqueta de disponibilidad (regla de negocio, verificada en stage —
CP_EC_MA_PDP_001): `Disponible`, `Agotado` o `Solo queda N` (N bajo un
umbral configurable en backend). Se localiza por texto, no por clase de
color. Es la fuente de verdad para el cliente: el estado del SPA puede
decir `is_in_stock` en un artículo que la PDP marca Agotado. Vive en MA
porque PDP_001 aplica solo a MA (MA-AISLAMIENTO-001).
"""


class ProductLocators:
    AVAILABILITY_LABEL = (
        "span:text-matches('^(Disponible|Agotado|Solo queda [0-9]+)$', 'i')"
        ":visible"
    )
    ADD_TO_CART_BUTTON = (
        "button.add-to-cart.border.relative.buy.button-viu.contained.lg.primary"
        ".btn-ripple:visible"
    )
    NOTIFICATION = "div.notifications.fixed span"
    NOTIFICATION_CLOSE = "button[aria-label='Cerrar']:visible"
    CART_NOTIFICATION_BUTTON = "button.fw-600.fs-15.cl-white:visible"
