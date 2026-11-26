# CAMBIOS CP_EC_MA_CART_001 — Agregar producto disponible al carrito

## Alcance

Alinear `CP_EC_MA_CART_001` con los 7 pasos del contrato
`Context_Contratos/MA/CP_EC_MA_CART_001.md`, **solo para Muebles América**
(mecanismo de [MA-AISLAMIENTO-001](CAMBIOS_MA-AISLAMIENTO-001.md)). El
escenario va **intercalado** (acción → verificación), como en SEARCH y PDP.

El caso común existía y pasaba, pero dos pasos se cumplían siempre:

| # | Paso del contrato | Antes (escenario común) | Ahora (escenario MA) |
|---|---|---|---|
| 1 | PDP disponible | Clic en la card sin verificar nada | `se abre la PDP del producto seleccionado`: URL con el slug de la card y mismo nombre (reutilizado de PDP_001 MA) |
| 2 | Registrar nombre, identificador y precio | `read_product()` sin assert ni adjunto | Nombre no vacío, sku presente y precio efectivo > 0; adjunto "Producto registrado" |
| 3 | Cantidad 1 | Guardaba la cantidad de la PDP como "esperada": **una qty 2 en PDP y carrito también pasaba** | Cantidad visible (`div.product-quantity`) **y** cantidad del SPA iguales a 1 |
| 4 | Acción procesada | Clic en el CTA | El estado del SPA (`cart.cartItems`) registra el sku con `qty 1` y `server_item_id` (aceptado por Magento) |
| 5 | Confirmación observable | `dismiss_post_add_overlays()` se tragaba el timeout: **sin toast, pasaba igual** | El toast dice "agregado a tu carrito" y menciona el producto, y el minicart muestra 1. Después se despejan los overlays |
| 6 | Carrito disponible | Solo espera | Ruta `/checkout/cart` + contenedor visible |
| 7 | Producto visible con cantidad 1 | 1 ítem con datos de la PDP; qty == la de la PDP | El sku registrado aparece, hay exactamente 1 ítem, el nombre coincide y la cantidad es **1** |
| Tags | `@muebles_america @cart` | Solo `@CART_001` | `@muebles_america` (Feature) + `@CART_001 @cart` |

Cobertura adicional que se conserva (EC-SP01-012, no la pide el
contrato): `el carrito contiene el producto con datos coherentes con la
PDP` y `los importes del carrito son consistentes con el subtotal y el
total` (steps comunes).

**`CP_EC_VIU_CART_001` no cambia:** sigue corriendo el escenario común,
que el equipo VIU trabaja en `origin/viu`.

## Cambios

| Pieza | Detalle |
|---|---|
| `test_cases/muebles_america/cart/cart.feature` | Nuevo. `@muebles_america`; `@CART_001 @cart` intercalado 1:1 (15 steps). Reemplaza al `@CART_001` común solo en MA |
| `tests/bdd/steps/muebles_america/cart_steps.py` | Nuevo. 8 steps (pasos 2–7) con adjuntos "Producto registrado", "Adición procesada", "Confirmación" y "Carrito" |
| `tests/bdd/test_features.py` | Importa los steps de Cart de MA |
| `pages/muebles_america/cart/cart_locators.py` | Nuevo. `CART_ROUTE` y `CART_ITEMS_EXPR` (lee `__INITIAL_STATE__.cart.cartItems`); hereda los comunes |
| `pages/muebles_america/cart/cart_page.py` | `state_item(sku)` (espera la sincronización; devuelve el último ítem visto o `None`), `minicart_count()`, `wait_for_minicart_count(n)` (devuelve el último valor) e `is_open()`. Devuelven estado, sin asserts |
| `pages/muebles_america/product/product_locators.py` | `QUANTITY = "div.product-quantity:visible"` |
| `pages/muebles_america/product/product_page.py` | `displayed_quantity()` y `add_confirmation_message()` (texto del toast `NOTIFICATION` o `None`) |
| `pytest.ini` | Marker `cart` |
| `scripts/build_plane_catalog.py` → `test_cases/plane_catalog.yaml` | Bloque `muebles_america` en CART_001 con los textos del contrato. Solo cambia la entrada `CP_EC_MA_CART_001`; la de VIU queda igual |

**No se tocan:** `test_cases/common/cart/cart.feature`, `tests/bdd/steps/cart_steps.py`,
`CartComponent`, `CommonCartPage`, `pages/viu/` ni `@CART_002`. Tampoco
se usan ni se modifican los steps compartidos `agrega el producto al
carrito` y `abre la PDP de una card elegible`, que `origin/viu`
reescribió. Los textos nuevos no repiten los de `origin/viu` (`el
producto agregado es visible en el carrito con cantidad 1`, `el subtotal
del ítem coincide…`).

Observables verificados en stage MA (`parrilla` → `MABE00902`, desktop 1366×768):

| Paso | Observable | Valor |
|---|---|---|
| 2 | Producto registrado | `Parrilla De Gas Mabe PM75KR0 76 Cm`, sku `MABE00902`, product_id `319265`, $6,119.00 |
| 3 | Cantidad visible / SPA | `1` / `1` (`div.product-quantity`; `counter-text` "1 de 1") |
| 4 | `cart.cartItems` | `{"sku": "MABE00902", "qty": 1, "server_item_id": 313168}` tras `POST /api/cart/update` → 200 |
| 5 | Toast | "Tu producto Parrilla De Gas Mabe PM75KR0 76 Cm ha sido agregado a tu carrito de compras. ACEPTAR" |
| 5 | Minicart del header | vacío → `Carrito 1` |
| 7 | Carrito | `[{"sku": "MABE00902", "quantity": 1}]`, subtotal del ítem $6,119.00 |

## Comandos

```bash
pytest tests/bdd/test_features.py --case-id CP_EC_MA_CART_001
pytest -m cart --site muebles_america          # escenarios de Cart marcados (hoy: CART_001)
```

## Requisitos del contrato

| Requisito | Cómo se cumple |
|---|---|
| Producto disponible / PDP operativo | Card elegible de `search`/`with_results` (MA: `parrilla`) vía `data_provider`; paso 1 verifica la PDP |
| Acción de agregar habilitada | `add_to_cart()` sobre el CTA visible; el paso 4 falla si el ecommerce no acepta el ítem |
| Resultado final: carrito con el producto y cantidad 1 | Paso 7 + integridad PDP→Cart adicional |
| Postcondición: existe un producto en el carrito | Paso 7 exige exactamente 1 ítem |
| Tags `@muebles_america @cart` | `@muebles_america` en la Feature y `@cart` en el escenario |
| Asserts fuera de Page Objects | Solo en `tests/bdd/steps/muebles_america/cart_steps.py` |
| Solo MA | El escenario vive en `test_cases/muebles_america/`; en VIU se descarta (`keep_for_site`) |

## Validación

Quality Gate:

| Control | Resultado |
|---|---|
| `python -m compileall -q .` | ✅ |
| `ruff check .` | ✅ All checks passed |
| `pytest tests/unit tests/architecture -q` | ✅ 120 passed |
| `--collect-only` MA / VIU | ✅ 21 / 21 (26 recolectados, 5 descartados por marca) |
| `-m cart --site muebles_america --collect-only` | ✅ 1 (`CP_EC_MA_CART_001`) |

En vivo (stage):

| Ejecución | Resultado | Duración |
|---|---|---|
| Línea base previa `CP_EC_MA_CART_001` (escenario común) | ✅ | 19.8s |
| Línea base previa `CP_EC_VIU_CART_001` | ✅ | 19.0s |
| `CP_EC_MA_CART_001` run 1 / 2 / 3 | ✅ | 14.4s / 14.8s / 14.2s |
| `CP_EC_VIU_CART_001` (sin cambios) | ✅ | 14.9s |
| `CP_EC_MA_CART_002` (comparte `abre el carrito de compras`) | ✅ | 14.3s |
| `CP_EC_MA_PDP_001` (comparte los steps de PDP de MA) | ✅ | 9.4s |
| Smoke MA (`-m smoke --site muebles_america`) | ✅ 5 passed (sin cambio de tamaño) | 98.7s |

Pruebas negativas con objetos falsos (fuera del repo), **21 de 21 según lo
esperado**. Fallan con mensaje claro:

- sin sku;
- precio 0;
- cantidad visible 2 o ausente;
- ítem ausente del estado del carrito, sin `server_item_id` o con qty 2;
- confirmación ausente, de error ("La cantidad solicitada no está
  disponible") o de otro producto;
- minicart en 0;
- carrito no abierto;
- producto ausente del carrito, 2 ítems o cantidad 2.

Los 6 casos válidos pasan.

Simulación de merge (`git merge-tree` del working tree contra `origin/viu`):
0 conflictos de código (solo `plane_catalog.yaml`, que es generado), 0 steps
duplicados y 0 steps faltantes nuevos. Los únicos 3 faltantes son de
escenarios `@pending` de `payment.feature` y ya existían antes.

## Notas

- **Al mezclar `origin/viu`:** su `cart.feature` común reemplaza el
  `@CART_002` actual por "El ítem del carrito conserva producto,
  cantidad, precio y subtotal de la PDP" y retira el step `se muestra la
  opción de continuar como invitado`. Como `@CART_002` es común,
  `CP_EC_MA_CART_002` pasará a correr esa versión. Si MA necesita su
  propio CART_002, debe hacerse con este mismo mecanismo.
- El paso 4 lee estado interno del SPA (`cart.cartItems`): es lo que
  distingue "procesado por el ecommerce" de "confirmado al cliente"
  (paso 5). Lo eligió el usuario.
- El paso 3 verifica la cantidad 1 por defecto, pero no la selecciona: la
  PDP no ofrece un selector que se tenga que operar para llegar a 1.
