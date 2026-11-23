"""Locators del checkout OSC — verificados idénticos en MA y VIU.

Los `name` se repiten entre secciones KO (envío, facturación, pickup);
los selectores de formulario deben filtrar `:visible`. Los `id` de los
campos son dinámicos → se usa `name`; los `id` de estructura documentados
abajo sí son estables.
"""


class CheckoutGateLocators:
    GUEST_CONTINUE = "role=button[name='Continuar como invitado']"


class CheckoutLocators:
    LOADER = "#checkout-loader"

    # Acordeón (estructura estable del OSC)
    SHIPPING_STEP = "#omniButtonShipping"
    PAYMENT_STEP = "#paymentExpansionButton"
    SUMMARY_STEP = "#omniButtonSummary"
    PLACE_ORDER = "#_btnCheckout"  # crea la orden — fuera de alcance aquí

    # Datos del comprador (por name + :visible; ids KO dinámicos)
    EMAIL = "input[name='username']:visible"
    FIRSTNAME = "input[name='firstname']:visible"
    LASTNAME = "input[name='lastname']:visible"
    MOTHERS_NAME = "input[name='custom_attributes[address_mothers_name]']:visible"
    PHONE = "input[name='telephone']:visible"

    # Dirección
    STREET = "input[name='street[0]']:visible"
    EXTERIOR_NUMBER = "input[name='custom_attributes[address_number]']:visible"
    POSTCODE = "input[name='postcode']:visible"
    # El input de colonia es oculto (el visible es el select por CP).
    COLONIA = "input[name='custom_attributes[colonia]']"
    COLONIA_SELECT = "select[name='colonia_select_shipping']:visible"
    CITY = "input[name='city']:visible"
    STATE = "select[name='region_id']:visible"
    REFERENCE = "input[name='custom_attributes[address_reference]']:visible"

    REQUIRED_INPUTS = "input[required]:visible"
    FIELD_ERRORS = ".field-error:visible, .mage-error:visible, .message.error:visible"
