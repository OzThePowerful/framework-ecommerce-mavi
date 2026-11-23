"""Locators de la PDP de Muebles América.

Los de la ventana de promociones viven en components/promotions_window/.
"""


class ProductLocators:
    ADD_TO_CART_BUTTON = (
        "button.add-to-cart.border.relative.buy.button-viu.contained.lg.primary"
        ".btn-ripple:visible"
    )
    NOTIFICATION = "div.notifications.fixed span"
    NOTIFICATION_CLOSE = "button[aria-label='Cerrar']:visible"
    CART_NOTIFICATION_BUTTON = "button.fw-600.fs-15.cl-white:visible"
