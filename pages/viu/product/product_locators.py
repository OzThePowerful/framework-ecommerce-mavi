"""Locators de la PDP de VIU.

El CTA `button.add-to-cart` y la lectura de estado son idénticos a MA:
viven en pages/common/components/pdp/pdp_locators.py.
"""


class ProductLocators:
    ADD_TO_CART_BUTTON = "button.add-to-cart:visible"
    NOTIFICATION = "div.notifications.fixed span"
    NOTIFICATION_CLOSE = "button[aria-label='Cerrar']:visible"
    # Toast post-add (div.notification) — a diferencia de MA no enlaza al
    # carrito: solo ofrece "Aceptar"; el minicart se abre desde el header.
    NOTIFICATION_TOAST = "div.notification:visible"
    NOTIFICATION_ACCEPT = ".notification-action:visible"
    MODAL_BACKDROP = "div.modal-backdrop:visible"
    MINICART_BUTTON = "header:visible button[aria-label='Abrir minicart']"
