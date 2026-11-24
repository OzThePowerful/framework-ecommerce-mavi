# CAMBIOS EC-SP01-018-1 — SaleCashWorkflow multi-ecommerce

## Alcance

Capa de coordinación del flujo de venta de contado
(`CP_EC_MA_E2E_001` / `CP_EC_VIU_E2E_001`):

`Test/BDD → SaleCashWorkflow → Search → Product → Cart → Checkout → Payment → Order`

## Piezas

| Pieza | Detalle |
|---|---|
| `workflows/common/sale_cash_workflow.py` | `SaleCashWorkflow`, `SaleRequest`, `SaleResult`, `PaymentCard` |
| `workflows/muebles_america/sale_cash_workflow.py` | Stub de EC-SP01-001 → alias del common |
| `pages/viu/home/home_page.py` | `close_promo_if_present()` no-op — paridad de fachada con MA |
| `tests/unit/test_sale_cash_workflow.py` | 11 pruebas contractuales con fakes |

## Diseño

- **`SaleRequest`**: `search_term`, `customer`, `address`,
  `shipping_method`, `payment_method`, `card` (`PaymentCard`) y
  `confirm_order=False` — la confirmación real es opt-in explícito
  (crea orden en stage).
- **`SaleResult`**: modelos de dominio por etapa — `product`, `cart`,
  `customer`/`address` leídos del checkout, `shipping`, `summary`
  (totales previos a confirmar), `payment_method`, `order` (None si no
  se confirmó).
- **Reglas del contrato**: sin locators, sin Playwright, sin asserts,
  sin YAML, sin secretos — verificado por `test_workflow_policy.py`.
- **Diferencias MA/VIU por composición**: el `PageFactory` materializa
  la fachada de la marca; el workflow no contiene `if site`. La única
  brecha de fachada (`close_promo_if_present` solo en MA) se resolvió
  con un no-op documentado en `HomePage` VIU.
- **Errores de precondición sin ocultarlos**: cada etapa se envuelve en
  `_stage()` que registra inicio/fin, anota el nombre de la etapa en la
  excepción (`add_note`) y la relanza. Precondiciones de negocio se
  elevan como `PreconditionError` explícitas: sin card elegible, PDP
  no disponible, carrito vacío, gate ausente, errores de formulario,
  método de pago no seleccionable.

## Validación

| Prueba | Resultado |
|---|---|
| `tests/unit/test_sale_cash_workflow.py` | ✅ 11 passed — orden de etapas, modelos, confirmación opt-in, precondiciones, propagación de errores, paridad MA/VIU |
| Quality gate | ✅ compileall + ruff + architecture + 103 collected |
| Unitarios + architecture | ✅ 89 passed |

## Fuera de alcance

El wiring BDD del escenario E2E (`sale_cash.feature` @pending) queda
para EC-SP01-019. Workflows de crédito/wishlist/cancelación: fuera.
