"""Locators de pago de MA — los de la etapa son common (verificados
idénticos a VIU); aquí solo los de CP_EC_MA_PAY_001.

Forma de pago (CP_EC_MA_PAY_001, verificado en stage MA):
- 5 métodos `input[name='payment[method]']` con `label[for=<value>]`;
- la habilitación de los radios oscila al abrir la etapa (todos → solo
  'Efectivo' → todos, en ~2.3 s): leer tras estabilizarse;
- el método elegido marca su contenedor `.payment-method._active` y el
  botón `#_btnCheckout` pasa de 'Finalizar compra' a 'Pagar con <método>'.

Confirmación (CP_EC_MA_ORDER_001, verificado en stage MA, orden
2000059131): el click dispara POST `…/V1/guest-carts/<id>/checkout-information`,
el token de OpenPay (`sandbox-api.openpay.mx/…/tokens`, 201), POST
`…/guest-carts/<id>/payment-information` (200, cuerpo = id interno de la
orden, p.ej. "65767") y `…/mavi-placeorderhistory/…/saveResponseResult`;
luego redirige a la página de éxito. El resto de POST son analítica.
"""


class PaymentLocators:
    ACTIVE_METHOD_RADIO = ".payment-method._active input[name='payment[method]']"
    # Fragmentos de URL de las peticiones de la confirmación (no analítica).
    CONFIRMATION_REQUESTS = ("/rest/", "openpay")
    PLACE_ORDER_REQUEST = "/payment-information"
    # → [{value, label, enabled}] de los métodos de pago presentes.
    OPTIONS_EXPR = """() => [...document.querySelectorAll("input[name='payment[method]']")]
        .map(r => {
            const label = document.querySelector(`label[for='${r.id}']`);
            return {
                value: r.value,
                label: label ? label.innerText.trim().replace(/\\s+/g, ' ') : '',
                enabled: !r.hasAttribute('disabled'),
            };
        })"""
