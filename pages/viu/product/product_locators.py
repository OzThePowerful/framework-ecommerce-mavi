"""Locators de la PDP de VIU.

El CTA `button.add-to-cart` y la lectura de estado son idénticos a MA:
viven en pages/common/components/pdp/pdp_locators.py.
"""


class ProductLocators:
    ADD_TO_CART_BUTTON = "button.add-to-cart:visible"
    NOTIFICATION = "div.notifications.fixed span"
    NOTIFICATION_CLOSE = "button[aria-label='Cerrar']:visible"
