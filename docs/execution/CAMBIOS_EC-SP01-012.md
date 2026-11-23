# CAMBIOS EC-SP01-012 — Cart MA + VIU

**Tipo**: implementación del vertical Cart con integridad comercial
`Product → Cart` en ambas marcas y transición al gate de checkout.

## Qué se implementó

Flujo completo: PDP → `add_to_cart` → minicart → página de carrito
(`/checkout/cart`) → lectura de ítems como `CartItem`/`Cart` de dominio →
comparación contra el `Product` leído en PDP → CTA `Pagar` → gate
`Continuar como invitado`.

### DOM verificado (idéntico en ambas marcas)

- Carrito real: `/checkout/cart` en **ambos** sitios. Se corrige la matriz:
  el `/carrito` de MA documentado en EC-SP01-008 era un hallazgo de probe
  defectuoso; esa ruta no existe.
- Ítems: `.shopping-cart-products .shopping-tile` (reemplaza
  `.product-item-details`, que no existe en el DOM Vue real).
- Fila: `.sku` (texto `SKU#: XXX`), `.name`,
  `.product-quantity.counter` (contador textual, no input),
  `span.price.cl-accent` (vigente) / `span.price.line-through` (anterior),
  `button.trash` (Eliminar).
- Resumen: `div.expansion-panel` con `Subtotal:`/`Descuento:` en su texto,
  `.total-price-value`, `.total-products` ("Total de productos N").
- CTA: `role=button[name='Pagar']` → gate `Continuar como invitado`.

### Ajustes encontrados en implementación

- Nombre/precio del ítem duplicados en el DOM (layout móvil + desktop) →
  `.first` en todos los campos de fila.
- `span.sum` es el botón "+" del stepper, no el valor → cantidad desde
  `.product-quantity.counter`.
- Los ítems se acotan a `.shopping-cart-products`: `shopping-tile` puede
  aparecer fuera del contenedor principal.

### Componente common (nuevo)

`pages/common/components/cart/`: `open_cart()` (header → minicart → CTA
"Ir al carrito de compras" → `/checkout/cart`), `items()` → `CartItem`,
`read_cart()` → `Cart`, `page_subtotal()`/`page_discount()`/`page_total()`
→ `Money`, `total_products()`, `continue_to_checkout()`.

`pages/common/components/checkout/`: gate de invitado
(`wait_for_guest_gate()`, `is_guest_gate_visible()`) — base del próximo
vertical de checkout.

### Pages por marca

- `pages/muebles_america/cart/`: fachada sobre el componente common;
  conserva `buy_now()` (regresión del workflow intacta).
- `pages/viu/cart/`: nueva fachada equivalente.
- `pages/viu/checkout/`: nuevo — gate de invitado.
- `CheckoutPage` MA: compone el gate common.
- `ProductPage` MA/VIU: `dismiss_post_add_overlays()` — MA cierra la
  ventana de promociones + toast; VIU solo el toast.

### Casos implementados (BDD)

`test_cases/common/cart.feature` — se materializa por marca vía `--site`:

| Caso | Escenario |
|---|---|
| `CP_EC_MA_CART_001` / `CP_EC_VIU_CART_001` | Agregar producto → integridad comercial: SKU, nombre, cantidad y precio efectivo del `Product` vs `CartItem`; subtotal/descuento/total página vs modelo |
| `CP_EC_MA_CART_002` / `CP_EC_VIU_CART_002` | Continuar al checkout → gate `Continuar como invitado` |

Steps delgados en `tests/bdd/steps/cart_steps.py`; evidencia Allure con
SKU, cantidad, precio unitario, subtotal de ítem y subtotal/descuento/total
del carrito. Los importes usan `Money`/`Decimal` exclusivamente.

## Fuera de alcance respetado

Sin confirmación de orden, sin pago final, sin flujos de compra completos
más allá del gate de invitado.

## Archivos

| Estado | Rutas |
|---|---|
| Nuevos | `pages/common/components/cart/` (3), `pages/common/components/checkout/` (3), `pages/viu/cart/` (3), `pages/viu/checkout/` (3), `test_cases/common/cart.feature`, `tests/bdd/steps/cart_steps.py` |
| Modificados | `pages/muebles_america/cart/cart_page.py`, `pages/muebles_america/product/` (page + locators), `pages/viu/product/` (page + locators), `pages/muebles_america/checkout/checkout_page.py`, `tests/bdd/test_features.py`, `docs/architecture/matriz_locators.md` |

## Validación

| Prueba | Resultado |
|---|---|
| `CP_EC_MA_CART_001` + `CP_EC_MA_CART_002` | ✅ 2 passed |
| `CP_EC_VIU_CART_001` + `CP_EC_VIU_CART_002` | ✅ 2 passed |
| Quality gate | ✅ compileall · ruff · architecture · 77 collected |
| `pytest tests/unit` | ✅ 49 passed |
| Regresión BDD + smoke MA | ✅ 8 passed |

## Definition of Done

La transición PDP → Cart se valida comercialmente en ambas marcas: el
`CartItem` reconstruido del DOM se compara campo a campo contra el
`Product` de dominio leído en PDP, y los importes del resumen se validan
contra `Cart.subtotal/discount/total` del modelo — sin acoplar las
comparaciones al HTML.
