"""Locators de la ventana de promociones ("Añadido al carrito") de la PDP."""


class PromotionsWindowLocators:
    ROOT = "div.modal-container:has(h5:text-is('Añadido al carrito'))"
    # Desktop: botón X (aria-label="Cerrar"); mobile: "Seguir comprando".
    CLOSE_BUTTON = (
        "button[aria-label='Cerrar']:visible, "
        "button:has(span:text-is('Seguir comprando')):visible"
    )
    BACKDROP = "#product div.modal-backdrop:visible"
