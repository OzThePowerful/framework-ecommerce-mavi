"""Locators del checkout (OneStepCheckout) de Muebles América.

`FIELD_BY_NAME` (CP_EC_MA_CHECKOUT_001): plantilla para un campo del
formulario del comprador por `name` (los `id` KO son dinámicos). Se usa
`:visible` porque los `name` se repiten entre secciones (envío, login).
"""


class CheckoutLocators:
    GUEST_CONTINUE_BUTTON = "role=button[name='Continuar como invitado']"
    CHECKOUT_LOADER = "#checkout-loader"
    TOTAL_PRICE = "strong span.price"
    FIELD_BY_NAME = "input[name='{name}']:visible"
