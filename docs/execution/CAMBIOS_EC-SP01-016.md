# CAMBIOS EC-SP01-016 — Payment de contado MA + VIU

## Alcance

Selección y preparación del método de contado (`openpay_cards`) en ambas
marcas, hasta la última frontera permitida: `#_btnCheckout`
**habilitado**. La acción que crea la orden nunca se ejecuta.

## Implementación

| Pieza | Detalle |
|---|---|
| `pages/common/components/payment/` | `PaymentComponent` + `PaymentLocators`: `open_payment_stage()`, `payment_methods()`, `is_method_selectable()`, `select_method()` (raise `PaymentError` si no seleccionable), `selected_method()`, `expects_external_provider()`, `fill_card()`, `set_billing_same_as_shipping()` / `is_billing_same_as_shipping()`, `is_place_order_enabled()` / `wait_place_order_enabled()` (la frontera), `validation_errors()` |
| `pages/muebles_america/payment/` + `pages/viu/payment/` | Fachadas `PaymentPage` (convención `pages.<site>.payment.payment_page` → `pages.payment()`) |
| `fixtures/data_fixtures.py` | Fixture `payment_card`: lee el registro `payment`/`card` del DataProvider — las tarjetas sandbox son ficticias (públicas) y van versionadas por decisión del equipo; las credenciales reales (login/API) viven en `.env` |
| `test_cases/common/payment.feature` | Escenario `PAY_001` (→ `CP_EC_MA_PAY_001` / `CP_EC_VIU_PAY_001`) |
| `tests/bdd/steps/payment_steps.py` | Steps delgados: abre etapa de pago, selecciona contado del dataset + tarjeta de env, valida método seleccionado, sin errores y `Finalizar compra` habilitado. Allure adjunta método/estado/métodos disponibles — nunca datos de tarjeta |

## Encapsulado (contrato)

| Requisito | Implementación |
|---|---|
| iframe | No aplica — OpenPay nativo (verificado 013): campos en DOM, tokenización JS del proveedor |
| redirección/proveedor externo | `expects_external_provider()` — `paypal_express` abre popup del proveedor |
| validaciones | `is_method_selectable()` detecta radios `disabled` (encapsula el límite `openpay_stores` > $30,000); `validation_errors()` lee `.field-error`/`mage-error` |
| tokenización | JS de OpenPay al confirmar — fuera del alcance del framework |
| estado de autorización | `is_place_order_enabled()` / `wait_place_order_enabled()` — única señal de "lista para confirmar" sin crear la orden |
| excepción | `PaymentError` (ya existía en la taxonomía `core/execution`) |

## Reglas de negocio incorporadas

- `openpay_cards` = contado. MSI (`4242…4242`) también es contado: el
  banco difiere los meses.
- `openpay_stores`: límite $30,000 MXN → sobre el monto el método no es
  seleccionable (radio `disabled`).
- `paypal_express`: el pago ocurre en ventana del proveedor (popup).
- `omnipro_pago_credito` = crédito de la marca, NO contado.

## Validación

| Prueba | Resultado |
|---|---|
| `CP_EC_MA_PAY_001` (stage, tarjeta sandbox 4111) | ✅ passed |
| `CP_EC_VIU_PAY_001` (stage, tarjeta sandbox 4111) | ✅ passed |
| Quality gate (compileall + ruff + architecture + collect) | ✅ 81 collected |
| Unitarios | ✅ 49 passed |
| Regresión BDD + smoke MA | ✅ 12 passed |

## Seguridad

- Tarjetas ficticias de sandbox OpenPay (públicas) en
  `data/<sitio>/payment.yaml`; ningún PAN/CVV real en repo ni en
  evidencia Allure.
- Credenciales privadas (login `MAVI_LOGIN_*`, API `MAVI_API_*`) solo
  en `.env` — gitignored — o secrets de CI.
- `#_btnCheckout` solo se valida habilitado; el click no existe en el
  framework.

## Pendiente

- `ORDER_001/002` y `E2E_001`: requieren estrategia para el click
  irreversible (órdenes de prueba cancelables en stage).
- Escenario de validación del límite de `openpay_stores` requiere un
  carrito > $30,000 (no cubierto por `PAY_001`).
