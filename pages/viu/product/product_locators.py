"""Locators de la PDP de VIU.

El CTA `button.add-to-cart` y la lectura de estado son idénticos a MA:
viven en pages/common/components/pdp/pdp_locators.py.
"""


class ProductLocators:
    ADD_TO_CART_BUTTON = "button.add-to-cart:visible"
    # Toast post-add (div.notification) — a diferencia de MA no enlaza al
    # carrito: solo ofrece "Aceptar"; el minicart se abre desde el header.
    # Llega en dos variantes: .success (agregado) y .error (sin stock).
    NOTIFICATION_TOAST = "div.notification:visible"
    NOTIFICATION_SUCCESS = "div.notification.success:visible"
    NOTIFICATION_ERROR = "div.notification.error:visible"
    NOTIFICATION_ACCEPT = ".notification-action:visible"
    # Modal rico post-add en productos con promo: subtotal, banner e
    # "Ir al carrito"; convive con el toast y deja un backdrop residual.
    CART_MODAL = "div.modal-container:visible"
    CART_MODAL_CLOSE = "div.modal-container button[aria-label='Cerrar']:visible"
    MODAL_GO_TO_CART = "div.modal-container button:has-text('Ir al carrito'):visible"
    MODAL_BACKDROP = "div.modal-backdrop:visible"
    MINICART_BUTTON = "header:visible button[aria-label='Abrir minicart']"
