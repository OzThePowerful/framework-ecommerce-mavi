"""Locators de la página de éxito de Muebles América (solo definiciones).

Información final de la orden (CP_EC_MA_ORDER_002, verificado en stage MA,
orden 2000059182): la página de éxito no expone ítems ni importes en el
DOM, pero publica en `window.dataLayer` dos eventos `purchase` generados
desde la orden:
- GA4 (weltpixel): `ecommerce.{transaction_id, value, tax, shipping,
  coupon, currency, items[{item_id, item_name, price, quantity}]}`;
- MAVI: los mismos campos + `tipo_pago` ("contado") e
  `items[].price_sin_descuento` / `price_descuento` ("0%").
`transaction_id` es el folio. Importes numéricos (6119 = $6,119.00).
"""


class OrderLocators:
    # → [ecommerce] de los eventos `purchase` presentes en el dataLayer.
    PURCHASE_EVENTS_EXPR = """() => (window.dataLayer || [])
        .filter(e => e && e.event === 'purchase' && e.ecommerce)
        .map(e => JSON.parse(JSON.stringify(e.ecommerce)))"""
