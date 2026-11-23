"""Locators de la etapa Forma de pago del OSC — verificados en MA y VIU.

Los métodos son radios `input[name='payment[method]']` cuyo `id` coincide
con el `value`. OpenPay es nativo (campos en el DOM, sin iframes; la
tokenización va por el JS del proveedor). Nunca versionar datos de
tarjeta: llegan por variables de entorno.
"""


class PaymentLocators:
    # Acordeón / confirmación (frontera: habilitado, nunca clickeado aquí)
    PAYMENT_STEP = "#paymentExpansionButton"
    PLACE_ORDER = "#_btnCheckout"

    # Métodos de pago
    METHOD_RADIOS = "input[name='payment[method]']"
    METHOD_CHECKED = "input[name='payment[method]']:checked"
    METHOD_BY_VALUE = "input[name='payment[method]'][value='{value}']"
    METHOD_LABEL = "label[for='{value}']"

    # OpenPay tarjeta (contado)
    CARD_NUMBER = "#openpay_cards_cc_number"
    CARD_EXP_MONTH = "#openpay_cards_expiration"
    CARD_EXP_YEAR = "#openpay_cards_expiration_yr"
    CARD_CVV = "#openpay_cards_cc_cid"

    # Facturación
    BILLING_SAME_AS_SHIPPING = "#billing-address-same-as-shipping"

    FIELD_ERRORS = ".field-error:visible, .mage-error:visible, .message.error:visible"


# Métodos que implican salir del dominio (popup/redirect del proveedor).
EXTERNAL_PROVIDER_METHODS = {"paypal_express"}
