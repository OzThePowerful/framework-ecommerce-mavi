# CAMBIOS EC-SP01-017 — Order Confirmation MA + VIU

## Alcance

Confirmación real de la compra en stage (autorizada): ejecución de
`#_btnCheckout`, detección de éxito inequívoco, captura de folio y
verificación de consistencia comercial Order vs Product/Cart/Shipping/
total/pago.

## Implementación

| Pieza | Detalle |
|---|---|
| `domain/models/order.py` | `Order` extendido: `folio`, `confirmation_message` (además de items/subtotal/discount/shipping/total/payment_method existentes) |
| `pages/common/components/order/` | `OrderComponent` + `OrderLocators`: `wait_success()` (URL `**/success/**` + `.checkout-success`), `is_success()` (inequívoco: URL + contenedor + folio), `order_number()` (folio por regex sobre el texto del contenedor), `confirmation_message()`, `decline_message()` (→ `PaymentError` en rechazo), `read_order()` |
| `pages/<marca>/order/` | Fachadas `OrderPage` (convención `pages.<site>.order.order_page` → `pages.order()`) |
| `PaymentComponent.confirm_order()` | **Acción irreversible**: espera habilitación + click en `Finalizar compra` — separada y explícita, solo casos ORDER/E2E |
| `ShippingComponent.summary_totals()` | `dict[str, Money]` con Subtotal/Envío/Total de `.omni-summary-totals` (etiquetas tolerantes) |
| `fill_card` robusto | Espera de fieldset estable (KO re-renderiza al seleccionar método), fill+verificación de dígitos (máscara con espacios), **`Tab` tras cada campo** — KO valida en blur |
| `order.feature` + `order_steps.py` | `ORDER_001` (folio + confirmación) / `ORDER_002` (consistencia comercial) × 2 marcas |
| Fixture `payment_card` | Migrada a dataset `payment`/`card` (tarjetas ficticias versionadas por decisión del equipo) |
| `site_credentials` + `guest_customer` fixtures + `.env` | Datos privados del equipo en `.env` gitignored + `.env.example` + `load_dotenv()`: login `MAVI_LOGIN_<SITIO>_*`, API `MAVI_API_*`, **identidad del comprador `MAVI_GUEST_<SITIO>_*`** (correo real — el checkout lo valida externamente) |
| `data_providers/customer_provider.py` | `resolve_guest_customer(site)` → `Customer` desde env; `ConfigError` con variables faltantes |
| `customers.yaml` | **Eliminados** — la identidad ya no se versiona (decisión PM: datos de clientes solo del equipo) |

## Hallazgos críticos de implementación

- **Email validado externamente**: `@example.com` rechazado silenciosamente
  al confirmar → datasets migrados a correo real del equipo.
- **Folio sin selector**: `# NNNNNNNNNN` solo como texto en
  `.checkout-success` → extracción por regex.
- **La página de éxito no muestra items/totales**: la consistencia se
  verifica capturando `.omni-summary-totals` antes de confirmar.

## Órdenes de prueba creadas (stage)

| Caso | Marca | Folio | SKU | Total |
|---|---|---|---|---|
| Probe levantamiento | MA | 2000058324 | MABE00902 | $6,119.00 |
| `CP_EC_MA_ORDER_001` | MA | 2000058327 | — | — |
| `CP_EC_MA_ORDER_002` | MA | 2000058330 | MABE00902 | $6,119.00 |
| `CP_EC_VIU_ORDER_001` | VIU | 12000050087 | — | — |
| `CP_EC_VIU_ORDER_002` | VIU | 12000050090 | WHIR00686 | $18,999.00 |

## Validación

| Prueba | Resultado |
|---|---|
| `CP_EC_MA_ORDER_001` + `002` | ✅ passed (órdenes reales creadas) |
| `CP_EC_VIU_ORDER_001` + `002` | ✅ passed |
| Quality gate | ✅ 83 collected, ruff + architecture OK |
| Unitarios + architecture | ✅ 69 passed |
| Regresión BDD+smoke MA (sin ORDER) | ✅ 11 passed |

## Nota operativa

Los escenarios ORDER crean órdenes reales: las regresiones habituales
deben excluirlos (`-k "not confirmar and not consistente"`) salvo
ejecución deliberada.
