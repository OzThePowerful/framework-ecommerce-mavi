# CAMBIOS CP_EC_MA_ORDER_002 — Validar integridad comercial de la orden generada

## Alcance

Alinear `CP_EC_MA_ORDER_002` con los 9 pasos del contrato
`Context_Contratos/MA/CP_EC_MA_ORDER_002.md`, **solo para Muebles América**
(mecanismo de [MA-AISLAMIENTO-001](CAMBIOS_MA-AISLAMIENTO-001.md)). El
escenario va **intercalado**: cada acción del contrato lleva su
verificación. Reutiliza la cadena de [CP_EC_MA_ORDER_001](CAMBIOS_CP_EC_MA_ORDER_001.md)
hasta la orden generada.

> ⚠️ **El caso crea una orden REAL en stage MA** cada vez que se ejecuta
> (ejecución autorizada en stage). Ver [Comandos](#comandos) para excluirlo.

**Fuente de la "información final de la orden":** los eventos `purchase`
que la página de éxito publica en `window.dataLayer`. Se generan en el
servidor a partir de la orden creada, y su `transaction_id` es el folio. Es
la única fuente posterior a la orden que se puede observar desde la UI de MA:

| Fuente evaluada | Resultado en stage MA |
|---|---|
| Página de éxito (DOM) | Solo el folio; sin ítems ni importes |
| Consulta de pedido de invitado `/sales/guest/form` | 404 (redirige al front headless) |
| "Mis pedidos" `/my-account/orders` | Requiere login; la orden se crea como invitado |
| API `MAVI_API_*` | Marcada "uso futuro"; sin cliente en el framework |
| **`dataLayer` de la página de éxito** | ✅ 2 eventos `purchase` con folio, importes, ítems y `tipo_pago` |

| # | Paso del contrato | Antes (escenario común) | Ahora (escenario MA) |
|---|---|---|---|
| — | Precondiciones: orden generada; Product, Cart y Checkout disponibles | Cadena común + resumen previo | PDP verificada, carrito leído y verificado (1 producto, cantidad 1), resumen final y total capturados antes de confirmar, confirmación de ORDER_001 (página de éxito verificada) |
| 1 | Obtener información final → datos disponibles | **No existía**: solo comparaba contra el resumen previo a confirmar | Eventos `purchase` del folio presentes, con ítems, subtotal, envío y total; los eventos coinciden entre sí (total, envío y SKU/cantidad/precio por ítem) |
| 2 | Comparar producto → coincide | SKU carrito = PDP (sin la orden) | 1 producto; SKU orden = PDP = carrito = checkout; nombre orden = PDP |
| 3 | Comparar cantidad → coincide | No se comparaba | Cantidad orden = PDP = carrito = checkout |
| 4 | Comparar subtotal → coincide | Resumen = carrito (sin la orden) | Precio unitario orden = PDP = carrito; subtotal orden (Σ precio × cantidad) = carrito = checkout |
| 5 | Comparar descuento → coincide cuando aplique | Solo en la fórmula del total | Cupón en la orden ⇔ descuento en el carrito; descuento de producto de la orden (`price_sin_descuento − price`) = PDP (`unit_price − effective_price`) |
| 6 | Comparar shipping → coincide | Resumen = Shipping (sin la orden) | Envío orden = checkout |
| 7 | Comparar total → coincide | Resumen = fórmula (sin la orden) | Total orden (`value`) = checkout = subtotal − descuento + envío |
| 8 | Revisar forma de pago → contado | `order.payment_method` = esperado, **pero ese valor lo ponía el propio test** (siempre pasaba) | `tipo_pago` de la orden = `payment.card.sale_type` (`"contado"`) y método seleccionado = `openpay_cards` |
| 9 | Revisar folio → identificador válido | Folio numérico | Folio de la página numérico = `transaction_id` de la orden |
| Tags | `@muebles_america @order @commercial_validation` | Solo `@ORDER_002` | `@muebles_america` (Feature) + `@ORDER_002 @order @commercial_validation` |

**`CP_EC_VIU_ORDER_002` no cambia:** sigue corriendo el escenario común, que
`origin/viu` reescribe en su rama (`9c157b0`). `CP_EC_MA_E2E_001` sigue con
el escenario común.

## Cambios

| Pieza | Detalle |
|---|---|
| `test_cases/muebles_america/order/order.feature` | Nuevo escenario `@ORDER_002 @order @commercial_validation` (47 steps); el encabezado del Feature ya cubre ORDER_001 y ORDER_002 |
| `tests/bdd/steps/muebles_america/order_steps.py` | 18 steps (pasos 1–9). Adjuntos "Orden final" (cada evento normalizado), "Producto", "Cantidad", "Subtotal", "Descuento", "Envío", "Total", "Forma de pago" y "Folio" |
| `pages/muebles_america/order/order_locators.py` (nuevo) | `PURCHASE_EVENTS_EXPR`: los `ecommerce` de los eventos `purchase` del `dataLayer` |
| `pages/muebles_america/order/order_page.py` | `final_order(folio)` (solo lectura). Espera hasta 10 s el evento del folio y devuelve `{folio, items[{sku, name, qty, price, list_price}], subtotal, shipping, total, coupon, sale_type, events}`, con importes en `Money`. Los campos que faltan en un evento se completan con el otro, y `events` conserva cada evento por separado |
| `data/muebles_america/payment.yaml` | `card.sale_type: "contado"`: tipo de venta que debe informar la orden |
| `pytest.ini` | La descripción de `commercial_validation` advierte que incluye una orden real |
| `scripts/build_plane_catalog.py` → `test_cases/plane_catalog.yaml` | Bloque `muebles_america` en ORDER_002 con el contrato. Solo cambia `CP_EC_MA_ORDER_002`; el resto es renumeración de alias YAML |

Se reutilizan:
- los steps de ORDER_001 de MA, para el resumen final, el total, la confirmación, la respuesta, la página final y el número de orden;
- los de PDP/Cart/Checkout/Payment de MA;
- `order_number()` de la `OrderPage` común.

**No se tocan:**
- `test_cases/common/order/order.feature`, `tests/bdd/steps/order_steps.py`, ni `OrderComponent` y sus locators;
- los steps de ORDER_001 de MA (solo se reusan);
- E2E_001 ni nada de VIU.

Los 18 textos nuevos no existen en esta rama ni en `origin/viu`.

Observables verificados en stage MA (línea base con lectura del `dataLayer` y corridas en vivo):

| Evento | Contenido (orden 2000059182) |
|---|---|
| GA4 (weltpixel), `pageType: "purchase"` | `transaction_id: "2000059182"`, `value: 6119`, `tax: 0`, `shipping: 0`, `coupon: ""`, `items[{item_id: "MABE00902", item_name: "Parrilla De Gas Mabe PM75KR0 76 Cm", price: 6119, quantity: 1}]` |
| MAVI | Lo mismo, más `tipo_pago: "contado"` e `items[].price_sin_descuento: 6119`, `price_descuento: "0%"`; `coupon: " "` (espacio) |

Resultado de una corrida (orden 2000059185): SKU `MABE00902` y cantidad 1 en las 4 etapas; precio unitario y subtotal 6119.00 en orden, PDP, carrito y checkout; sin cupón ni descuento; envío 0.00; total 6119.00 en la orden, el checkout y la fórmula; `tipo_pago` "contado" con `openpay_cards`; folio de la página = `transaction_id`.

## Comandos

```bash
# Crea una orden REAL en stage (requiere MAVI_GUEST_MA_* en .env)
pytest tests/bdd/test_features.py --case-id CP_EC_MA_ORDER_002
pytest -m order --site muebles_america                      # ORDER_001 + ORDER_002

# -m commercial_validation ahora incluye CART_002 (sin orden) y ORDER_002 (con orden)
pytest -m commercial_validation --site muebles_america
pytest -m "commercial_validation and not order" --site muebles_america   # solo sin orden

# Regresión de MA sin órdenes
pytest tests/bdd/test_features.py --site muebles_america -k "not ORDER and not E2E"
```

## Requisitos del contrato

| Requisito | Cómo se cumple |
|---|---|
| Precondición: orden generada | Steps de ORDER_001 de MA hasta "se presenta la confirmación de la compra" |
| Precondición: información de Product, Cart y Checkout | PDP (`pdp_ctx`), carrito leído (`cart_ctx`), resumen final y totales (`checkout_ctx`) |
| Validaciones: producto, SKU/product ID, cantidad, precio unitario, subtotal, descuentos, shipping, total, forma de pago, folio | Pasos 2–9. Product ID: la orden solo expone el SKU (`item_id`), que es el identificador que se compara |
| Resultado final: la orden representa la operación comercial | Los 9 pasos contra la orden final del `dataLayer` |
| Tags `@muebles_america @order @commercial_validation` | Feature + escenario; markers registrados |
| Asserts fuera de Page Objects | Solo en `tests/bdd/steps/muebles_america/order_steps.py` |

## Validación

Quality Gate:

| Control | Resultado |
|---|---|
| `python -m compileall -q .` | ✅ |
| `ruff check .` | ✅ All checks passed |
| `pytest tests/unit tests/architecture -q` | ✅ 120 passed (11.4s) |
| `--collect-only` MA / VIU | ✅ 21 / 21 (33 recolectados, 12 descartados por marca) |
| `-m "order or commercial_validation"` (MA) | ✅ 3 (`CART_002`, `ORDER_001`, `ORDER_002`) |

En vivo (stage, con `.env` local):

| Ejecución | Resultado | Duración |
|---|---|---|
| Línea base `CP_EC_MA_ORDER_002` (escenario común) + lectura del `dataLayer` | ✅ orden 2000059182 | 77.3s |
| `CP_EC_MA_ORDER_002`, run 1 / 2 / 3 | ✅ órdenes 2000059185 / 2000059188 / 2000059191 | 78.5s / 75.5s / 78.9s |
| `CP_EC_MA_ORDER_001` (comparte feature, `OrderPage` y steps) | ✅ orden 2000059197 | 75.1s |
| `CP_EC_MA_PAY_001` (comparte el registro `payment`/`card`) | ✅ | 39.6s |
| `CP_EC_MA_CART_002` (suite `commercial_validation`) | ✅ | 15.2s |
| Smoke MA (`-m smoke --site muebles_america`) | ✅ 5 passed (sin cambio de tamaño) | 96.4s |
| Smoke VIU (`-m smoke --site viu`) | ✅ 4 passed | 145.1s |

Órdenes de prueba creadas en stage MA (todas `MABE00902`, $6,119.00, `openpay_cards`):
`2000059182`, `2000059185`, `2000059188`, `2000059191`, `2000059194` (prueba negativa), `2000059197`.

Prueba negativa (en vivo, paso 8; **crea 1 orden**, porque el paso es posterior a la confirmación):
- con `sale_type: "credito"` en `data/muebles_america/payment.yaml`, el caso **falla en el paso 8** (`La orden informa tipo de pago 'contado'; esperado 'credito'`, 73.5s, orden 2000059194);
- el dataset se restauró en `try/finally`: hash idéntico y el `git diff` muestra solo el cambio autorizado (`sale_type: "contado"`).

Simulación de merge (`git merge-tree` del working tree contra `origin/viu`
`b5ab5d2`):
- 0 conflictos de código; solo `plane_catalog.yaml`, que es generado;
- 0 steps duplicados.

## Notas

- **Dependencia de analítica:** el caso depende de los tags de GA4
  (weltpixel) y del de MAVI en la página de éxito. Si se desactivan o
  cambian, el paso 1 falla con `La página final no publica la orden …`.
  Cuando exista un cliente de la API (`MAVI_API_*`), conviene leer la orden
  desde ahí.
- **`value` como total:** con envío 0 no se puede distinguir si `value` es
  el total o el subtotal. El paso 7 lo exige igual al total del checkout, y
  un carrito con envío > 0 lo confirmaría.
- **Descuentos:** el producto MA en stage no tiene promoción ni se usa
  cupón, así que el paso 5 solo se ha visto con descuento 0. El evento GA4
  no trae `price_sin_descuento`; se toma del evento de MAVI. Si ninguno lo
  trae, solo se verifica el cupón.
- **`-m commercial_validation` ahora crea una orden** en MA (decisión al
  autorizar: aplicar el tag que pide el contrato). Para la suite sin
  órdenes usar `-m "commercial_validation and not order"`.
- El cupón del evento de MAVI viene como `" "` (espacio): se normaliza con
  `strip()`.
