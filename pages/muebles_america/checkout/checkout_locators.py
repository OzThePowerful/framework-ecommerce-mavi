"""Locators del checkout (OneStepCheckout) de Muebles América.

`FIELD_BY_NAME` (CP_EC_MA_CHECKOUT_001): plantilla para un campo del
formulario del comprador por `name` (los `id` KO son dinámicos). Se usa
`:visible` porque los `name` se repiten entre secciones (envío, login).

Validación por campo (CP_EC_MA_CHECKOUT_002, verificada en stage MA):
- correo inválido → input `aria-invalid=true` + `div.mage-error#customer-email-error`;
- teléfono corto → contenedor `div.field._error` + `div.field-error`;
- al corregir, ambos desaparecen.
"Continuar" en el OSC es abrir el acordeón "Forma de pago"
(`PAYMENT_STEP`); "Finalizar compra" crea la orden y no se usa aquí.

Domicilio y entrega (CP_EC_MA_CHECKOUT_003, verificado en stage MA):
- el CP llena `COLONIA_SELECT` (p.ej. 44100 → AMERICANA, GUADALAJARA
  CENTRO) y autoselecciona la primera; ciudad (solo lectura) y estado;
- `#domicilio` / `#sucursal` son los métodos; el activo lleva
  `StorePickupSelected` ("A tu domicilio" viene preseleccionado);
- el resumen muestra "Envío: Aún no calculado" hasta completar el
  domicilio y luego "Costo de envío: Gratis" o un importe.

Resumen final (CP_EC_MA_ORDER_001, verificado en stage MA): "Detalle de
la compra" lista un `li.omni-product-item` por producto con el texto
"SKU#: MABE00902 / <nombre> / A: $6,119.00 / Entrega entre el … /
Cantidad: 1" (sin selectores por campo: se lee el texto del ítem).
"""


class CheckoutLocators:
    GUEST_CONTINUE_BUTTON = "role=button[name='Continuar como invitado']"
    CHECKOUT_LOADER = "#checkout-loader"
    TOTAL_PRICE = "strong span.price"
    FIELD_BY_NAME = "input[name='{name}']:visible"
    PAYMENT_STEP = "#paymentExpansionButton"
    COLONIA_SELECT = "select[name='colonia_select_shipping']:visible"
    DELIVERY_OPTIONS = {"a_domicilio": "#domicilio", "sucursal": "#sucursal"}
    SHIPPING_SUMMARY = ".omni-summary-totals"
    SUMMARY_ITEM = "li.omni-product-item:visible"
    # (name) → texto del error del input visible con ese name, o null.
    FIELD_ERROR_EXPR = """(name) => {
        const input = [...document.querySelectorAll(`input[name="${name}"]`)]
            .find(i => i.offsetParent !== null);
        if (!input) return null;
        const field = input.closest('.field');
        const texts = [];
        if (field && field.classList.contains('_error')) {
            const e = field.querySelector('.field-error, .mage-error');
            texts.push(e && e.innerText.trim() ? e.innerText.trim() : 'campo con error');
        }
        if (input.getAttribute('aria-invalid') === 'true') {
            const ref = input.getAttribute('aria-describedby');
            const e = (ref && document.getElementById(ref))
                || (input.id && document.getElementById(input.id + '-error'))
                || (field && field.querySelector('.mage-error'));
            texts.push(e && e.innerText.trim() ? e.innerText.trim() : 'aria-invalid');
        }
        return texts.length ? [...new Set(texts)].join(' | ') : null;
    }"""
    # → names de los inputs visibles marcados como inválidos.
    INVALID_FIELDS_EXPR = """() => [...document.querySelectorAll('input, select')]
        .filter(i => i.offsetParent !== null && i.name
            && (i.getAttribute('aria-invalid') === 'true'
                || (i.closest('.field') && i.closest('.field').classList.contains('_error'))))
        .map(i => i.name)"""
