# CAMBIOS CP_EC_MA_PAY_001 — Seleccionar forma de pago correspondiente a venta de contado

## Alcance

Alinear `CP_EC_MA_PAY_001` con los 6 pasos del contrato
`Context_Contratos/MA/CP_EC_MA_PAY_001.md`, **solo para Muebles América**
(mecanismo de [MA-AISLAMIENTO-001](CAMBIOS_MA-AISLAMIENTO-001.md)). El
escenario va **intercalado**: cada acción del contrato lleva su
verificación. La forma de pago de contado es **`openpay_cards`, "Tarjeta
Crédito / Débito" (OpenPay)**, decidido al autorizar: es el método que ya
usan `checkout`/`guest.payment_method` y E2E_001. Nunca se pulsa
"Finalizar compra".

| # | Paso del contrato | Antes (escenario común) | Ahora (escenario MA) |
|---|---|---|---|
| — | Precondición: checkout completo, dirección válida, entrega seleccionada | Steps comunes de búsqueda → checkout | Steps de PDP/Cart/Checkout de MA + comunes `registra los datos del comprador del dataset` / `selecciona el método de entrega del dataset`. Se verifica el método de entrega (step de CHECKOUT_003 de MA) |
| 1 | Llegar a la etapa de pago → disponible | Abría el acordeón, sin verificar | `continue_to_payment` de MA; etapa activa `forma_de_pago`, métodos presentes y sin errores. El estado del botón solo se adjunta (ver Notas) |
| 2 | Consultar métodos → opciones habilitadas | No se verificaba | Lectura **estabilizada** de `{value, label, enabled}`: ≥ 1 habilitado, todos con nombre visible, ninguno preseleccionado y botón **deshabilitado** sin método |
| 3 | Identificar contado → encontrado | Solo se usaba el `value` | El `value` del dataset está entre las opciones, habilitado, y su nombre visible = `payment.card.label` |
| 4 | Seleccionar → método activo | `:checked` = dataset (al final) | `:checked` = contado, contenedor `.payment-method._active` = contado y botón "Pagar con Tarjeta Crédito / Débito" |
| 5 | Completar datos → información aceptada | Llenaba la tarjeta sin revisar | Número, mes, año y CVV conservados = dataset; sin errores; facturación = dirección de entrega |
| 6 | Revisar resumen → compra lista para finalizar | Botón habilitado | Subtotal = precio efectivo de la PDP (cantidad 1); total = subtotal + envío, > 0; método intacto; sin errores; botón habilitado; sigue en el checkout (no hay orden) |
| Tags | `@muebles_america @payment @cash_sale` | Solo `@PAY_001` | `@muebles_america` (Feature) + `@PAY_001 @payment @cash_sale` |

**`CP_EC_VIU_PAY_001` no cambia:** sigue corriendo el escenario común, que
`origin/viu` reescribe en su rama (`2efab82`).

## Cambios

| Pieza | Detalle |
|---|---|
| `test_cases/muebles_america/payment/payment.feature` (nuevo) | `@muebles_america` + `@PAY_001 @payment @cash_sale` (24 steps) |
| `tests/bdd/steps/muebles_america/payment_steps.py` (nuevo) | 12 steps (pasos 1–6) + fixture `cash_method`, que exige que `payment.card.method` = `checkout.guest.payment_method`. Adjuntos "Etapa de pago", "Métodos de pago", "Forma de pago de contado", "Método activo", "Datos de pago" (tarjeta enmascarada) y "Resumen antes de confirmar" |
| `tests/bdd/test_features.py` | Importa los steps de Payment de MA |
| `pages/muebles_america/payment/payment_page.py` | `payment_options()`: espera a que radios y botón no cambien durante 1.5 s (máx. 15 s). También `active_method()`, `place_order_label()` (solo lectura) y `card_values()` |
| `pages/muebles_america/payment/payment_locators.py` | `ACTIVE_METHOD_RADIO` y `OPTIONS_EXPR` |
| `data/muebles_america/payment.yaml` | `card` gana `label: "Tarjeta Crédito / Débito"` y `provider: "OpenPay"`, y se documentan sus restricciones. Eran los datos "pendientes" del contrato |
| `pytest.ini` | Markers `payment` y `cash_sale` |
| `scripts/build_plane_catalog.py` → `test_cases/plane_catalog.yaml` | Bloque `muebles_america` en PAY_001 con el contrato. Solo cambia el contenido de `CP_EC_MA_PAY_001`; el resto es renumeración de alias YAML |

Se reutilizan:
- de la `PaymentPage` común: `select_method`, `fill_card`, `selected_method`, `validation_errors`, `is_billing_same_as_shipping`, `wait_place_order_enabled` y `is_place_order_enabled`;
- de la página de checkout de MA: `continue_to_payment`, `is_on_checkout` y `summary_totals`.

La clave `expected_payment_method` se sigue llenando para los steps
comunes de ORDER/E2E.

**No se tocan:**
- `test_cases/common/payment/payment.feature`, `tests/bdd/steps/payment_steps.py`, ni `PaymentComponent` y sus locators comunes;
- los `@pending` PAY_002/003;
- nada de VIU.

Los textos nuevos evitan los de `origin/viu` (`se accede a la etapa de forma
de pago`, `se muestran métodos de pago habilitados`, `el método de contado
del dataset está disponible`).

Observables verificados en stage MA (desktop 1366×768; sondeo de solo lectura con datos ficticios y corridas en vivo):

| Paso | Observable |
|---|---|
| 1 | "Forma de pago" `opened`, etapa `forma_de_pago`; 5 métodos: `omnipro_pago_credito` "Crédito Muebles América", `openpay_cards` "Tarjeta Crédito / Débito", `paypal_express` "PayPal", `banktransfer` "Transferencia bancaria / Pago en tienda", `openpay_stores` "Efectivo" |
| 2 | **La habilitación oscila** al abrir la etapa: los 5 habilitados a 0 s → solo "Efectivo" a ~0.8–1.1 s → los 5 a ~2.3–2.6 s. Ninguno preseleccionado; botón "Finalizar compra" deshabilitado |
| 4 | Contenedor `payment-method _active`; botón **"Pagar con Tarjeta Crédito / Débito"**, aún deshabilitado; aparecen los campos de tarjeta y "Utilizar dirección de Entrega" (marcado) |
| 5 | Con número, vencimiento y CVV, el botón se habilita; sin errores. No hay checkbox de términos |
| 6 | p.ej. `{"subtotal": "6119.00", "shipping": "0.00", "total": "6119.00", "precio_pdp": "6119.00", "boton": "Pagar con Tarjeta Crédito / Débito", "boton_habilitado": true, "en_checkout": true}` |

## Comandos

```bash
pytest tests/bdd/test_features.py --case-id CP_EC_MA_PAY_001   # requiere MAVI_GUEST_MA_* en .env
pytest -m payment --site muebles_america
pytest -m cash_sale --site muebles_america
```

## Requisitos del contrato

| Requisito | Cómo se cumple |
|---|---|
| Datos: nombre del método, proveedor, datos de prueba, restricciones | `payment`/`card`: `method`, `label`, `provider`, tarjeta sandbox y restricciones en comentario |
| Precondiciones: checkout completo, dirección válida, entrega seleccionada | Steps de MA y comunes; método de entrega verificado; "Forma de pago" solo se habilita con dirección válida (paso 1) |
| Método de contado documentado y habilitado en Stage | Paso 3: presente, habilitado y con el nombre del dataset |
| Resultado final: forma de pago de contado seleccionada | Pasos 4 y 6 (seleccionado, activo y sin cambios antes de confirmar) |
| Tags `@muebles_america @payment @cash_sale` | Feature + escenario; markers registrados |
| Asserts fuera de Page Objects | Solo en `tests/bdd/steps/muebles_america/payment_steps.py` |

## Validación

Quality Gate:

| Control | Resultado |
|---|---|
| `python -m compileall -q .` | ✅ |
| `ruff check .` | ✅ All checks passed |
| `pytest tests/unit tests/architecture -q` | ✅ 120 passed |
| `--collect-only` MA / VIU | ✅ 21 / 21 (31 recolectados, 10 descartados por marca) |
| `-m "payment or cash_sale"` (MA) | ✅ 1 (`CP_EC_MA_PAY_001`) |

En vivo (stage, con `.env` local):

| Ejecución | Resultado | Duración |
|---|---|---|
| Línea base previa `CP_EC_MA_PAY_001` (escenario común) | ✅ | 53.9s |
| `CP_EC_MA_PAY_001`, primera versión, run 1 / 2 / 3 | ✅ | 52.3s / 49.2s / 47.5s |
| `CP_EC_MA_PAY_001`, primera versión, 1.ª prueba negativa | ❌ antes del paso alterado: botón habilitado en el paso 1 (ver Notas) | 41.2s |
| `CP_EC_MA_PAY_001`, versión final, run 1 / 2 / 3 / 4 / 5 | ✅ | 39.4s / 40.2s / 39.4s / 37.7s / 39.1s |
| `CP_EC_MA_CHECKOUT_001` / `_002` / `_003` (comparten steps de checkout) | ✅ | 33.4s / 36.4s / 37.6s |
| `CP_EC_VIU_PAY_001` (escenario común, sin cambios) | ✅ | 47.5s |
| Smoke MA (`-m smoke --site muebles_america`) | ✅ 5 passed (sin cambio de tamaño) | 137.3s |

CHECKOUT, VIU y smoke se ejecutaron antes del ajuste final. Ese ajuste
solo toca `payment_options()` y los steps nuevos de MA, que esos casos no
usan.

Prueba negativa (en vivo, paso 3):
- con `label: "Método Inexistente QA"` en `data/muebles_america/payment.yaml`, el caso **falla** (`El método 'openpay_cards' se muestra como 'Tarjeta Crédito / Débito'; dataset 'Método Inexistente QA'`, 30.5s);
- el dataset se restauró en `try/finally`: hash idéntico y el `git diff` muestra solo el cambio autorizado.

Simulación de merge (`git merge-tree` del working tree contra `origin/viu`
`b5ab5d2`, que ya incluye E2E_001 de VIU):
- 0 conflictos de código; solo `plane_catalog.yaml`, que es generado;
- 0 steps duplicados: los 12 textos nuevos no existen en esta rama ni en `origin/viu`.

## Notas

- **Inestabilidad encontrada y corregida:** en 1 de 9 corridas, el botón
  estaba **habilitado** ("Finalizar compra", sin método elegido) justo al
  abrir la etapa. No se reprodujo en dos sondeos que leían cada 250 ms. Es
  un estado transitorio de KO, igual que la oscilación de los radios. Por
  eso la verificación "sin método, el botón está deshabilitado" se movió al
  paso 2, después de que `payment_options()` estabiliza radios y botón. El
  paso 1 solo adjunta el estado del botón.
- El paso 5 aplica porque el contado elegido exige tarjeta. Otros métodos
  de contado ("Efectivo", `openpay_stores`) no piden datos y tienen límite
  de $30,000; eso es PAY_002 (`@pending`).
- Con `parrilla` el envío sale "Gratis". La regla total = subtotal + envío
  solo se ha visto en vivo con envío 0.
- Si el resumen mostrara una fila de descuento, la verificación subtotal =
  precio de la PDP seguiría valiendo, pero total = subtotal + envío fallaría.
  El producto MA en stage no tiene promoción.
