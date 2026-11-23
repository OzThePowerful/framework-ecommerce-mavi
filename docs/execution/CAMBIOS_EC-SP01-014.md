# CAMBIOS EC-SP01-014 — Checkout y Customer MA + VIU

**Tipo**: implementación del vertical Checkout/Customer con la arquitectura
del levantamiento EC-SP01-013: desde carrito válido hasta registrar los
datos del comprador como invitado. Sin pago ni confirmación (fuera de
alcance).

## Qué se implementó

### Componentes common (`pages/common/components/checkout/`)

- **`CheckoutComponent`**: gate de invitado (`wait_for_guest_gate`,
  `is_guest_gate_visible`, `continue_as_guest` con navegación por
  `checkout_url_pattern`), `wait_until_ready()` (loader OSC + render lazy
  KO), `current_stage()` (acordeón: `entrega`/`forma_de_pago`/`resumen`),
  `is_payment_stage_enabled()` + `wait_payment_stage_enabled()` (la
  validación KO de la dirección habilita el paso asíncronamente),
  `required_fields()`.
- **`CustomerFormComponent`** (nombre exigido por el contrato):
  `fill(customer, address)` — campos por `name` con `:visible` (los
  `name` se repiten entre secciones KO; los `id` son dinámicos);
  `wait_postcode_autocomplete()` (el lookup del CP corre en blur — se
  envía `Tab` tras el fill); `read_customer()` → `Customer`,
  `read_address()` → `Address` (colonia desde el input oculto
  autollenado, primera instancia no vacía); `validation_errors()`.

### Pages por marca

- `CheckoutPage` MA: compone ambos componentes; conserva
  `continue_as_guest`/`get_displayed_price` (regresión intacta).
- `CheckoutPage` VIU: misma composición + `continue_as_guest` del
  componente (navegación por patrón del contexto).

### Dominio

- `Customer.mothers_name: str | None` — apellidos completos del
  formulario OSC (backward-compatible).

### BDD (`test_cases/common/checkout.feature` + `checkout_steps.py`)

| Caso | Escenario |
|---|---|
| `CP_EC_MA_CHECKOUT_001` / `CP_EC_VIU_CHECKOUT_001` | Carrito válido → invitado → etapa `entrega` activa + campos obligatorios presentes |
| `CP_EC_MA_CHECKOUT_002` / `CP_EC_VIU_CHECKOUT_002` | Datos del dataset → sin errores de validación → `Customer`/`Address` leídos coherentes → etapa de pago habilitada |

Datos desde `data/<marca>/checkout.yaml` (referencia `customers:guest` +
`addresses:guadalajara`). Evidencia Allure con etapa, campos requeridos y
comprador registrado.

## Ajustes encontrados en implementación

- El autocompletado del CP corre en `change`/blur → `Tab` después del
  fill del postcode.
- `#paymentExpansionButton` se habilita de forma asíncrona tras la
  validación KO → `wait_payment_stage_enabled()`.
- `custom_attributes[colonia]` es input oculto → lectura por primera
  instancia con valor.
- `input[name='city']` existe duplicado (envío/facturación) → el wait
  evalúa todas las instancias.

## Archivos

| Estado | Rutas |
|---|---|
| Nuevos | `pages/common/components/checkout/customer_form_component.py`, `test_cases/common/checkout.feature`, `tests/bdd/steps/checkout_steps.py` |
| Modificados | `pages/common/components/checkout/{checkout_locators,checkout_component}.py`, `pages/muebles_america/checkout/checkout_page.py`, `pages/viu/checkout/checkout_page.py`, `domain/models/customer.py`, `tests/bdd/test_features.py` |

## Validación

| Prueba | Resultado |
|---|---|
| `CP_EC_MA_CHECKOUT_001` + `002` | ✅ passed |
| `CP_EC_VIU_CHECKOUT_001` + `002` | ✅ 2 passed |
| Quality gate | ✅ 79 collected |
| `pytest tests/unit` | ✅ 49 passed |
| Regresión BDD + smoke MA | ✅ 10 passed |

## Fuera de alcance respetado

Sin selección de método de pago ni `#_btnCheckout` — el límite es la
etapa "Forma de pago" habilitada.
