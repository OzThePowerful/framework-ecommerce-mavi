# CAMBIOS CP_EC_MA_ORDER_001 — Generar orden mediante venta de contado

## Alcance

Alinear `CP_EC_MA_ORDER_001` con los 6 pasos del contrato
`Context_Contratos/MA/CP_EC_MA_ORDER_001.md`, **solo para Muebles América**
(mecanismo de [MA-AISLAMIENTO-001](CAMBIOS_MA-AISLAMIENTO-001.md)). El
escenario va **intercalado**: cada acción del contrato lleva su
verificación. La venta de contado es **`openpay_cards`, "Tarjeta Crédito /
Débito" (OpenPay)** con tarjeta sandbox, la misma de
[CP_EC_MA_PAY_001](CAMBIOS_CP_EC_MA_PAY_001.md).

> ⚠️ **El caso crea una orden REAL en stage MA** cada vez que se ejecuta
> (ejecución autorizada en stage). Ver [Comandos](#comandos) para excluirlo.

| # | Paso del contrato | Antes (escenario común) | Ahora (escenario MA) |
|---|---|---|---|
| — | Precondiciones: carrito válido, checkout completo, contado seleccionado | Steps comunes de búsqueda → pago | Steps de PDP/Cart/Checkout/Payment de MA (los *When* de PAY_001) + comunes `registra los datos del comprador del dataset` / `selecciona el método de entrega del dataset`. Se verifica la PDP y el método de entrega |
| 1 | Revisar resumen final → información visible | No se revisaba | "Detalle de la compra": 1 producto con SKU, nombre y precio = PDP, cantidad 1 y fecha de entrega; método seleccionado = contado y botón "Pagar con <label del dataset>" |
| 2 | Validar total antes de confirmar → total disponible | No se validaba | Botón habilitado; total > 0; subtotal = precio × cantidad; total = subtotal + envío |
| 3 | Ejecutar confirmación → solicitud procesada | Click sin verificación | Click con registro de peticiones; `POST …/payment-information` responde 2xx con el id interno de la orden |
| 4 | Esperar respuesta → sin error inesperado | Solo `wait_success()` | Se llega a la página de éxito; ninguna petición de la confirmación responde ≥ 400; sin mensaje de rechazo; fuera del checkout |
| 5 | Revisar página final → confirmación de compra | Buscaba "pedido" o "compra" en el texto | Éxito inequívoco (URL + contenedor + folio); encabezado "Hemos recibido tu pedido" y mensaje con "N° de pedido" |
| 6 | Obtener número de orden → identificador válido | Folio numérico | Folio numérico **y** presente como `# <folio>` en la confirmación |
| Tags | `@muebles_america @order @cash_sale` | Solo `@ORDER_001` | `@muebles_america` (Feature) + `@ORDER_001 @order @cash_sale` |

**`CP_EC_VIU_ORDER_001` no cambia:** sigue corriendo el escenario común, que
`origin/viu` reescribe en su rama (`cdf85d2`). `CP_EC_MA_ORDER_002` y
`CP_EC_MA_E2E_001` siguen con el escenario común.

## Cambios

| Pieza | Detalle |
|---|---|
| `test_cases/muebles_america/order/order.feature` (nuevo) | `@muebles_america` + `@ORDER_001 @order @cash_sale` (29 steps) con advertencia de orden real |
| `tests/bdd/steps/muebles_america/order_steps.py` (nuevo) | 12 steps (pasos 1–6). Adjuntos "Resumen final", "Total antes de confirmar", "Solicitud de compra", "Respuesta de la confirmación", "Página final" y "Order" (folio, SKU, total, método) |
| `tests/bdd/test_features.py` | Importa los steps de Order de MA |
| `pages/muebles_america/checkout/checkout_page.py` + `checkout_locators.py` | `summary_items()` → `[{sku, name, price, qty, delivery}]` leídos del texto de `li.omni-product-item:visible` (solo lectura) |
| `pages/muebles_america/payment/payment_page.py` + `payment_locators.py` | `confirm_order_tracked()` (**irreversible**): registra los POST de la confirmación (`/rest/`, `openpay`), llama al `confirm_order()` común y espera la respuesta de `/payment-information`. `confirmation_responses()` devuelve lo registrado y quita el listener |
| `pages/muebles_america/order/order_page.py` | `success_heading()`: encabezado `.page-title` visible de la página de éxito |
| `pytest.ini` | Marker `order`; la descripción de `cash_sale` advierte que incluye una orden real |
| `scripts/build_plane_catalog.py` → `test_cases/plane_catalog.yaml` | Bloque `muebles_america` en ORDER_001 con el contrato. Solo cambia `CP_EC_MA_ORDER_001`; el resto es renumeración de alias YAML |

Se reutilizan: `confirm_order`, `wait_place_order_enabled`,
`is_place_order_enabled`, `selected_method` de la `PaymentPage` común;
`wait_success`, `is_success`, `confirmation_message`, `decline_message` y
`read_order` de la `OrderPage` común; `summary_totals` e `is_on_checkout`
del checkout de MA; y los steps de PAY_001 de MA para preparar el pago.

**No se tocan:**
- `test_cases/common/order/order.feature`, `tests/bdd/steps/order_steps.py`, `OrderComponent` y sus locators;
- ORDER_002, E2E_001 ni nada de VIU;
- ningún dataset.

Los 12 textos nuevos no existen en esta rama ni en `origin/viu` (VIU usa
`captura el resumen comercial previo a confirmar`, `el total del resumen
está disponible`, `confirma la compra`).

Observables verificados en stage MA (desktop 1366×768; sondeo de solo lectura sobre PAY_001, línea base con registro de peticiones y corridas en vivo):

| Paso | Observable |
|---|---|
| 1 | `li.omni-product-item`: "SKU#: MABE00902 / Parrilla De Gas Mabe PM75KR0 76 Cm / A: $6,119.00 / Entrega entre el 28 y el 30 de Noviembre. / Cantidad: 1"; botón "Pagar con Tarjeta Crédito / Débito" |
| 2 | `{"subtotal": "6119.00", "shipping": "0.00", "total": "6119.00", "boton_habilitado": true}` |
| 3 | Tras el click: `POST …/V1/guest-carts/<id>/checkout-information` 200 → `sandbox-api.openpay.mx/…/tokens` 201 → `POST …/guest-carts/<id>/payment-information` **200, cuerpo `"65770"`** (id interno de la orden, distinto del folio) → `…/mavi-placeorderhistory/guest/<id>/saveResponseResult` 200. El resto de POST son analítica (Adobe, New Relic, GA4) y no se evalúan |
| 4 | Redirección a `/checkout/onepage/success/`; sin `.message-error` |
| 5 | Encabezado `.page-title` "¡Gracias por tu compra! Hemos recibido tu pedido."; `.checkout-success` "Tu N° de pedido es: # 2000059134 … A continuación recibirás un correo de confirmación…" |
| 6 | Folio de 10 dígitos (`2000059134`) |

## Comandos

```bash
# Crea una orden REAL en stage (requiere MAVI_GUEST_MA_* en .env)
pytest tests/bdd/test_features.py --case-id CP_EC_MA_ORDER_001
pytest -m order --site muebles_america

# -m cash_sale ahora incluye PAY_001 (sin orden) y ORDER_001 (con orden)
pytest -m cash_sale --site muebles_america
pytest -m "cash_sale and not order" --site muebles_america   # solo sin orden

# Regresión de MA sin órdenes
pytest tests/bdd/test_features.py --site muebles_america -k "not ORDER and not E2E"
```

## Requisitos del contrato

| Requisito | Cómo se cumple |
|---|---|
| Precondición: carrito válido | Steps de PDP/Cart de MA (PDP verificada, adición confirmada) |
| Precondición: checkout completo | Comprador del dataset + entrega verificada |
| Precondición: contado seleccionado | Steps de PAY_001 de MA; el paso 1 verifica método y botón |
| Precondición: ambiente autorizado para pedidos de prueba | Stage MA; ejecución autorizada; advertencia en feature, marker y catálogo |
| Resultado final: orden con identificador verificable | Pasos 3 (id de orden en la respuesta), 5 (página de éxito) y 6 (folio en la confirmación y adjunto en Allure) |
| Postcondición: orden de prueba en el ambiente | Folio adjunto en "Order"; ver tabla de órdenes |
| Tags `@muebles_america @order @cash_sale` | Feature + escenario; markers registrados |
| Asserts fuera de Page Objects | Solo en `tests/bdd/steps/muebles_america/order_steps.py` |

## Validación

Quality Gate:

| Control | Resultado |
|---|---|
| `python -m compileall -q .` | ✅ |
| `ruff check .` | ✅ All checks passed |
| `pytest tests/unit tests/architecture -q` | ✅ 120 passed (5.6s) |
| `--collect-only` MA / VIU | ✅ 21 / 21 (32 recolectados, 11 descartados por marca) |
| `-m "order or cash_sale"` (MA) | ✅ 2 (`CP_EC_MA_PAY_001`, `CP_EC_MA_ORDER_001`) |

En vivo (stage, con `.env` local):

| Ejecución | Resultado | Duración |
|---|---|---|
| Línea base `CP_EC_MA_PAY_001` + sondeo del resumen (sin orden) | ✅ | 41.5s |
| Línea base `CP_EC_MA_ORDER_001` (escenario común) + registro de peticiones | ✅ orden 2000059131 | 71.7s |
| `CP_EC_MA_ORDER_001`, run 1 (sin el assert del encabezado) | ✅ orden 2000059134 | 57.6s |
| `CP_EC_MA_ORDER_001`, versión final, run 2 / 3 / 4 | ✅ órdenes 2000059137 / 2000059140 / 2000059146 | 74.0s / 71.9s / 72.4s |
| `CP_EC_MA_PAY_001` (comparte `PaymentPage` de MA) | ✅ | 39.6s |
| `CP_EC_MA_CHECKOUT_001` / `_002` / `_003` (comparten `CheckoutPage` de MA) | ✅ | 26.5s / 27.1s / 30.2s |
| Smoke MA (`-m smoke --site muebles_america`) | ✅ 5 passed (sin cambio de tamaño) | 94.6s |
| Smoke VIU (`-m smoke --site viu`) | ✅ 4 passed | 136.0s |

Órdenes de prueba creadas en stage MA (todas `MABE00902`, $6,119.00, `openpay_cards`):
`2000059131`, `2000059134`, `2000059137`, `2000059140`, `2000059146`.

Prueba negativa (en vivo, paso 1, **sin crear orden**):
- con `label: "Método Inexistente QA"` en `data/muebles_america/payment.yaml`, el caso **falla en el paso 1, antes de confirmar** (`El botón 'Pagar con Tarjeta Crédito / Débito' no muestra el método de contado 'Método Inexistente QA'`, 39.2s);
- el dataset se restauró en `try/finally`: hash idéntico y `git diff` vacío en `data/`.

Simulación de merge (`git merge-tree` del working tree contra `origin/viu`
`b5ab5d2`):
- 0 conflictos de código; solo `plane_catalog.yaml`, que es generado;
- 0 steps duplicados: los 12 textos nuevos no existen en esta rama ni en `origin/viu`.

## Notas

- **`-m cash_sale` ahora crea una orden** en MA (decisión al autorizar:
  aplicar el tag que pide el contrato). Para la suite sin órdenes usar
  `-m "cash_sale and not order"`.
- La página de éxito cambió respecto a EC-SP01-017: "¡Gracias por tu
  compra! Hemos recibido tu pedido." ya no está dentro de
  `.checkout-success`, sino en el encabezado `.page-title`. El escenario
  común (`"pedido" in message`) sigue pasando.
- El cuerpo de `payment-information` es el id interno de la orden
  (`65767`, `65770`, …), no el folio. Si el navegador ya no conserva el
  cuerpo, el paso 3 verifica solo el estado HTTP.
- Las verificaciones del paso 2 asumen que no hay fila de descuento (el
  producto MA en stage no tiene promoción) y solo se han visto con envío
  "Gratis".
- La regla de que `guia_operacion.md` excluye órdenes con `-k "not E2E"`
  no cubre ORDER (pendiente previo a este cambio); el comando correcto se
  documenta arriba.
