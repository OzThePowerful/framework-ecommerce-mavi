# CAMBIOS EC-SP01-011 — Product Detail Page y modelo `Product` MA + VIU

**Tipo**: implementación del vertical PDP con conversión DOM → modelo de
dominio `Product`, incluyendo productos configurables.

## Qué se implementó

Lectura de la PDP y conversión al contrato `Product` (name, sku, product_id,
unit_price, promotional_price, availability, quantity, estado del CTA) para
ambas marcas, con soporte de productos configurables (padre + variantes).

### Fuente de datos verificada

`window.__INITIAL_STATE__.product.current` — el estado del SPA expone todo lo
necesario en ambos sitios, estructura idéntica:

- `sku`, `name`, `price`/`final_price`, `regular_price`/`original_price`,
  `status`, `visibility`, `qty`, `type_id`, `parentSku`, `stock`
  (`is_in_stock`, `stock_status`, `qty`, `product_id`).
- El JSON-LD `Product` quedó **descartado como fuente de disponibilidad**:
  declara `OutOfStock` aunque el artículo tenga stock real (metadata SEO
  desfasada, verificado en ambos productos).

### Regla de venta implementada

`availability = stock.is_in_stock && stock.qty > 0 && status == 1 && visibility == 4`

Para hijos de configurables la regla exime `visibility` (siempre `1` por
diseño: no se exhiben individualmente).

### Componente common (nuevo)

`pages/common/components/pdp/`: `read_product()` → `Product`,
`stock_quantity()`, `quantity()`, `is_available()`,
`is_add_to_cart_enabled()`, `is_configurable()`, `parent_sku()`,
`variants()` → `list[Product]` (cada hijo con precio propio y disponibilidad
por su stock).

### Pages por marca

- `pages/muebles_america/product/`: fachada extendida; conserva
  `add_to_cart`/`open_cart_from_notification` (regresión intacta).
- `pages/viu/product/` (**nuevo**): misma fachada.
- `open_product()` en ambas SearchPage ahora espera `**/*.html` tras el clic
  (el SPA necesita la navegación antes de leer `product.current`).

### Configurables

Verificado con Colchón America Winer: padre `1COLC08920` (MA) /
`2COLC08920` (VIU) — **el prefijo del sku padre difiere por marca**; los sku
hijos (`AMER00733`–`AMER00736`) sí son compartidos. Precios por tamaño
6389–11489. `products.yaml` lleva `configurable_colchon` por sitio con
`expected_parent_sku` propio.

### BDD

`test_cases/common/pdp.feature` (2 escenarios agnósticos de marca) +
`tests/bdd/steps/pdp_steps.py` con evidencia Allure (`attach_text` del
`Product` y de las variantes). Wiring en `test_features.py`.

## Validación obligatoria — ambos PDP_001 + configurable

| Sitio | Comando | Resultado |
|---|---|---|
| CP_EC_MA_PDP_001 | `pytest tests/bdd --site muebles_america` | ✅ 4 passed |
| CP_EC_VIU_PDP_001 | `pytest tests/bdd --site viu` | ✅ 4 passed |

(4 = 2 search + 1 PDP simple + 1 configurable por sitio.)

## Validación del framework

| Comando | Resultado |
|---|---|
| `python scripts/quality_gate.py` | ✅ compileall · ruff · 20 architecture · 75 collected |
| Regresión `tests/smoke` MA stage | ✅ 2 passed |

## Criterios de aceptación

- ✅ MA y VIU producen el mismo contrato `Product` (incluidos configurables).
- ✅ Order/Checkout fuera de alcance (no se validaron).
- ✅ La información comercial viaja en `Product`, independiente del DOM.
