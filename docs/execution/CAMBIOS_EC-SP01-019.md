# CAMBIOS EC-SP01-019 — Cobertura BDD/Gherkin de los Test Cases

## Alcance

Todo caso `Automated` del catálogo tiene representación Gherkin
equivalente y ejecutable por su Case ID (`CP_EC_<MA|VIU>_<MODULO>_<NNN>`).
Cierra la brecha detectada tras EC-SP01-018: `HOME_001` y `SMOKE_001`
sin Gherkin, y `CUSTOMER`/`ADDRESS`/`SHIPPING_001` solo cubiertos
implícitamente dentro de escenarios CHECKOUT.

## Estructura

| Pieza | Detalle |
|---|---|
| `test_cases/common/<modulo>/*.feature` | 12 features compartidos, materializados por marca con `--site` (21 escenarios ×2) |
| Case ID como tag | `@<MODULO>_<NNN>` por escenario + hook de colección en `fixtures/execution_fixtures.py` que renombra el item a `CP_EC_<CODE>_<TAG>` → `-k CP_EC_VIU_CART_001` funciona |
| `@pending` | Auto-skip en colección (`pytest_collection_modifyitems`): PAY_002/PAY_003 se coleccionan como `skipped` trazables, nunca PASS falsificado |
| `tests/unit/test_case_id_materialization.py` | Gate de la convención |

## Features nuevos

| Feature | Casos | Implementación |
|---|---|---|
| `home/home.feature` | HOME_001 | Header marca + buscador accesible |
| `smoke/sale_cash.feature` | SMOKE_001 ×2 | `GuestCheckoutWorkflow` (movido a `workflows/common/`) |
| `e2e/e2e.feature` | E2E_001 ×2 | `SaleCashWorkflow` con `confirm_order=True` — crea orden real |
| `customer/customer.feature` | CUSTOMER_001 | Captura de comprador persiste en checkout |
| `address/address.feature` | ADDRESS_001 | CP autocompleta colonia/ciudad/estado |
| `shipping/shipping.feature` | SHIPPING_001 + SHIPPING_002 | Costo de envío + store picker (pickup) |
| `payment/payment.feature` (+2 @pending) | PAY_002/PAY_003 | Reglas de negocio sin dataset — skipped |

## Paridad de fachada VIU (nueva superficie)

| Pieza | Detalle |
|---|---|
| `pages/viu/components/mega_menu/` | Componente nuevo: `Departamentos` → `.categories-modal` (2 copias en DOM: `:visible` + `.categories-list-desktop`); swap `button→a` en item activo; carrera de hidratación Vue resuelta con espera corta + fallback `click`; click del link con fallback `dispatch_event` |
| `data/viu/guest_checkout.yaml` | Línea blanca > Estufas, estufa Whirlpool WFR7050S |
| `ProductPage` VIU | `open_cart_from_notification()`: el toast `div.notification` solo ofrece "Aceptar" (sin link al carrito) → aceptar + clic en `.modal-backdrop` residual + minicart desde header |
| `CartPage` VIU | `buy_now()` — mismo `button.buy-now` del minicart que MA |
| `CheckoutPage` VIU | `get_displayed_price()` → `delivery.summary_total()` |

## Fixes de robustez (componentes compartidos)

| Problema | Fix |
|---|---|
| `dismiss_post_add_overlays` no esperaba la confirmación del add → carrito vacío intermitente | Espera del toast post-add (10s tolerante) antes de despejar — el toast es la confirmación del POST async |
| `select_picker_state` devolvía la lista del estado previo | Espera a que `stores()` se estabilice tras `select_option` |
| `summary_totals()` fallaba con "Envío: Aún no calculado" | `summary_total()` nuevo: solo la fila Total |
| `SaleCashWorkflow` verificaba `is_method_selectable` antes de la habilitación KO | Delega a `select_method` (que espera el radio); `PaymentError` → `PreconditionError` |
| ADDRESS_001: sitio normaliza a mayúsculas | Comparación `casefold()` |

## Validación en vivo

| Caso | MA | VIU |
|---|---|---|
| HOME_001 | ✅ | ✅ |
| SMOKE_001 | ✅ | ✅ |
| CUSTOMER_001 | ✅ | ✅ |
| ADDRESS_001 | ✅ | ✅ |
| SHIPPING_001 | ✅ | ✅ |
| SHIPPING_002 | ✅ | ✅ |
| E2E_001 | ✅ **folio 2000058492** | ✅ **folio 12000050171** |

## Catálogo actualizado

38 Automated · 4 Not Automated (PAY_002/PAY_003 ×2 — reglas de negocio
sin dataset: límite >$30k de `openpay_stores` y wiring MSI).

## Nota operativa

`E2E_001` y `ORDER_001/002` crean órdenes reales en stage — excluir de
regresiones habituales: `-k "not E2E and not ORDER"`.
