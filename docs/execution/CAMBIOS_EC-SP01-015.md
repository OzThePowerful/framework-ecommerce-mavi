# CAMBIOS EC-SP01-015 — Address y Shipping MA + VIU

**Tipo**: implementación de la captura de domicilio y selección de método
de entrega, con separación de responsabilidades justificada por el DOM
(identidad del comprador vs dirección vs modo de entrega).

## Qué se implementó

### `AddressComponent` (common, nuevo)

Bloque de dirección extraído de `CustomerFormComponent`: calle, número
exterior, CP (fill + `Tab` → autocompletado de colonia/ciudad/estado),
referencias; `fill(address)` y `read()` → `Address` del dominio (ya
existente). `CustomerFormComponent` lo compone y delega — el contrato
público `fill_customer_form`/`read_address` no cambió.

### `ShippingComponent` (common, nuevo)

- `select_delivery_method("a_domicilio"|"sucursal")` → `#domicilio` /
  `#sucursal`; `current_delivery_mode()` detecta el toggle con
  `StorePickupSelected`.
- **Store picker** (mapeado por sondeo adicional, pedido del usuario):
  `open_store_picker()` → modal `.store-selector-popup`,
  `select_picker_state()` → `select[name='store-selector-state']`,
  `stores()` → filas `.location` (`.location-name`/`.location-address`),
  `select_store(name)` → `button.action-select-shipping-item` "Entregar
  aquí", `close_store_picker()` → `.action-close`; estado vacío
  `.store-selector-popup-empty-query`.
- `fill_pickup_contact()` → campos propios del pickup (`father-name`,
  `mother-name`, `phone`, `firstname`).
- `shipping()` → `Shipping` (método + `cost` `Money`); `shipping_cost()`
  espera el cálculo asíncrono (`Envío\tAún no calculado` → `Gratis`/
  importe, en `.omni-summary-totals`); `delivery_estimate()`.

### Pages

`CheckoutPage` MA/VIU componen `delivery` y exponen
`select_delivery_method`, `current_delivery_mode`, `shipping`,
`shipping_cost`, `delivery_estimate`.

### BDD — `CP_EC_*_CHECKOUT_003`

Nuevo escenario en `checkout.feature`: tras registrar el comprador,
selecciona el método del dataset (`shipping_method: "a_domicilio"`),
valida modo activo + `Shipping` con costo `Money >= 0` + etapa de pago
habilitada; adjunta Shipping a Allure.

## Ajustes encontrados en implementación

- El resumen del checkout es `.omni-summary-totals` (no
  `.expansion-panel` — eso era el cart) y está siempre renderizado.
- El costo de envío se calcula asíncrono tras el CP: el renglón aparece
  como `Envío\tAún no calculado` → espera de valor real.
- La etiqueta puede leerse como `Envío` o `Costo de envío` → regex
  tolerante.
- El store picker es un modal KO con tabs estado/CP, no un dropdown
  inline — quedó mapeado con lista, vacío y cierre.

## Archivos

| Estado | Rutas |
|---|---|
| Nuevos | `pages/common/components/checkout/{address_component,shipping_component,field_utils}.py` |
| Modificados | `pages/common/components/checkout/{checkout_locators,customer_form_component}.py`, `pages/*/checkout/checkout_page.py`, `test_cases/common/checkout.feature`, `tests/bdd/steps/checkout_steps.py`, `docs/architecture/{levantamiento_checkout,matriz_locators}.md` |

## Validación

| Prueba | Resultado |
|---|---|
| `CP_EC_MA_CHECKOUT_003` | ✅ passed |
| `CP_EC_VIU_CHECKOUT_003` | ✅ passed |
| Quality gate | ✅ 80 collected |
| `pytest tests/unit` | ✅ 49 passed |
| Regresión BDD + smoke MA | ✅ 11 passed |

## Fuera de alcance respetado

Sin confirmar pago ni `#_btnCheckout`; el límite es la etapa de pago
habilitada con costo de envío disponible para validaciones posteriores.
