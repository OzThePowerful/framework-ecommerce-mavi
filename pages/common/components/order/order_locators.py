"""Locators de la página de confirmación de orden del OSC.

Verificados en vivo (EC-SP01-017, orden 2000058324 en MA stage):
URL `…/checkout/onepage/success/`, contenedor `.checkout-success` con
"¡Gracias por tu compra! Hemos recibido tu pedido. Tu N° de pedido es:
# NNNNNNNNNN". El folio NO tiene selector dedicado: se extrae del
texto del contenedor (regex). La página no expone items ni totales.
"""


class OrderLocators:
    # Éxito inequívoco
    SUCCESS_CONTAINER = ".checkout-success"
    SUCCESS_URL = "**/success/**"
    SUCCESS_TITLE = ".page-title"

    # Folio: texto dentro del contenedor de éxito ("# 2000058324")
    ORDER_NUMBER = ".checkout-success"

    # Errores tras confirmar (declinación) — en el propio checkout
    DECLINE_MESSAGE = ".message-error:visible, .message.error:visible"

    # → [ecommerce] de los eventos `purchase` del dataLayer: fuente
    # autoritativa de la orden final (GA4 ecommerce; `transaction_id` =
    # folio, importes numéricos). Verificado en MA (EC-SP01-017+).
    PURCHASE_EVENTS_EXPR = """() => (window.dataLayer || [])
        .filter(e => e && e.event === 'purchase' && e.ecommerce)
        .map(e => JSON.parse(JSON.stringify(e.ecommerce)))"""
