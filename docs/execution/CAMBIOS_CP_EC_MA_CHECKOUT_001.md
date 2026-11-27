# CAMBIOS CP_EC_MA_CHECKOUT_001 — Iniciar Checkout desde un carrito válido

## Alcance

Alinear `CP_EC_MA_CHECKOUT_001` con los 5 pasos del contrato
`Context_Contratos/MA/CP_EC_MA_CHECKOUT_001.md`, **solo para Muebles
América** (mecanismo de [MA-AISLAMIENTO-001](CAMBIOS_MA-AISLAMIENTO-001.md)).
El escenario va **intercalado** (acción → verificación).

| # | Paso del contrato | Antes (escenario común) | Ahora (escenario MA) |
|---|---|---|---|
| — | Precondición: producto disponible en un carrito válido | Steps compartidos sin verificar (el add se tragaba el timeout) | `la disponibilidad permite comprar el producto` (PDP_001) + `el ecommerce procesa la adición del producto` (CART_001) |
| 1 | Carrito disponible | Solo espera | Ruta `/checkout/cart` + contenedor visible (CART_001) |
| 2 | Producto válido | No se revisaba | El sku registrado en la PDP está en el carrito, con 1 ítem, mismo nombre y cantidad 1 (CART_001) |
| 3 | El ecommerce inicia Checkout | El gate solo se esperaba dentro de `continúa como invitado` | Tras "Pagar", el gate "Continuar como invitado" es visible (step de CART_002 MA) |
| 4 | Primera etapa cargada | Espera de loader y email | La URL coincide con `checkout_url_pattern` de la marca, la etapa abierta es `entrega` y "Forma de pago" sigue deshabilitada |
| 5 | Campos necesarios disponibles | Los 7 `name` fijos en el step debían estar en `required` | Los campos de `checkout`/`entry.required_fields` (dataset) están marcados como obligatorios **y** son capturables: visibles, habilitados y no de solo lectura |
| Tags | `@muebles_america @checkout` | Solo `@CHECKOUT_001` | `@muebles_america` (Feature) + `@CHECKOUT_001 @checkout` |

**`CP_EC_VIU_CHECKOUT_001` no cambia:** sigue corriendo el escenario común.
`origin/viu` tiene su propia versión (`4307eab CP_EC_VIU_CHECKOUT_001`).
`@CHECKOUT_002` y `@CHECKOUT_003` siguen comunes en ambas marcas.

## Cambios

| Pieza | Detalle |
|---|---|
| `test_cases/muebles_america/checkout/checkout.feature` | Nuevo. `@muebles_america`; `@CHECKOUT_001 @checkout` intercalado (17 steps). Reemplaza al común solo en MA |
| `tests/bdd/steps/muebles_america/checkout_steps.py` | Nuevo. Fixture `checkout_entry` + 2 steps (pasos 4 y 5) con adjuntos "Checkout inicial" y "Campos requeridos" |
| `tests/bdd/test_features.py` | Importa los steps de Checkout de MA |
| `pages/muebles_america/checkout/checkout_page.py` | `is_on_checkout()` (URL contra el patrón glob del `ExecutionContext`) y `unavailable_fields(names)` (los no visibles o no editables) |
| `pages/muebles_america/checkout/checkout_locators.py` | `FIELD_BY_NAME = "input[name='{name}']:visible"` |
| `data/muebles_america/checkout.yaml` | Clave nueva `entry.required_fields` (7 `name`); `guest` no cambia |
| `pytest.ini` | Marker `checkout` |
| `scripts/build_plane_catalog.py` → `test_cases/plane_catalog.yaml` | Bloque `muebles_america` en CHECKOUT_001 con el contrato. Solo cambia la entrada `CP_EC_MA_CHECKOUT_001` |

**No se tocan:** `test_cases/common/checkout/checkout.feature`,
`tests/bdd/steps/checkout_steps.py`, `CheckoutComponent`,
`CommonCheckoutPage`, `ShippingComponent` (los modifica `origin/viu`) ni
nada de VIU. Los textos nuevos no repiten los de `origin/viu` (`el acceso
como invitado está disponible`, `se presenta al menos un método de
entrega`, `se accede a la etapa de forma de pago`).

Observables verificados en stage MA (`parrilla` → `MABE00902`, desktop 1366×768):

| Paso | Observable | Valor |
|---|---|---|
| 1 | Carrito | `https://mueblesstage.mavi.mx/checkout/cart`, sin mensajes de error visibles |
| 3 | Tras "Pagar" | El gate "Continuar como invitado" se abre **sobre el mismo `/checkout/cart`** (la URL no cambia) |
| 4 | Tras "Continuar como invitado" | `https://mcstage.mueblesamerica.mx/onestepcheckout/` (otro host; coincide con `checkout_url_pattern` de `sites.yaml`), título "One Step Checkout" |
| 4 | Acordeón | `#omniButtonShipping` `opened`; `#paymentExpansionButton` `disabled` |
| 5 | Requeridos en pantalla | `username`, `firstname`, `lastname`, `custom_attributes[address_mothers_name]`, `telephone`, `street[0]`, `custom_attributes[address_number]`, `postcode`, `custom_attributes[colonia]`, `city` (**solo lectura**: la llena el CP), `custom_attributes[address_reference]` |

## Comandos

```bash
pytest tests/bdd/test_features.py --case-id CP_EC_MA_CHECKOUT_001
pytest -m checkout --site muebles_america        # escenarios de Checkout marcados (hoy: CHECKOUT_001)
```

## Requisitos del contrato

| Requisito | Cómo se cumple |
|---|---|
| Carrito con producto válido / producto disponible | Precondiciones verificadas con los steps de PDP_001 y CART_001 de MA |
| Sin errores pendientes en carrito | **Pendiente** (ver Notas) |
| Resultado final: ingresa al flujo de Checkout | Pasos 3–5 |
| Campos necesarios | Lista en el dataset de MA (`entry.required_fields`), no en el código |
| Tags `@muebles_america @checkout` | Feature + escenario |
| Asserts fuera de Page Objects | Solo en `tests/bdd/steps/muebles_america/checkout_steps.py` |

## Validación

Quality Gate:

| Control | Resultado |
|---|---|
| `python -m compileall -q .` | ✅ |
| `ruff check .` | ✅ All checks passed |
| `pytest tests/unit tests/architecture -q` | ✅ 120 passed |
| `--collect-only` MA / VIU | ✅ 21 / 21 (28 recolectados, 7 descartados por marca) |
| `-m checkout --site muebles_america --collect-only` | ✅ 1 (`CP_EC_MA_CHECKOUT_001`) |

En vivo (stage):

| Ejecución | Resultado | Duración |
|---|---|---|
| Línea base previa `CP_EC_MA_CHECKOUT_001` (escenario común) | ✅ | 26.7s |
| Línea base previa `CP_EC_VIU_CHECKOUT_001` | ✅ | 25.4s |
| `CP_EC_MA_CHECKOUT_001` run 1 / 2 / 3 | ✅ | 25.5s / 26.9s / 29.4s |
| `CP_EC_VIU_CHECKOUT_001` (sin cambios) | ✅ | 25.1s |
| `CP_EC_MA_CART_002` (comparte el step del gate) | ✅ | 14.5s |
| `CP_EC_MA_CHECKOUT_002` (comparte `continúa como invitado`) | ⚠️ No ejecutable en este workspace: `ConfigError` porque faltan `MAVI_GUEST_MA_*` (no existe `.env`). Ajeno a este cambio: falla al construir la identidad del comprador, antes de cualquier step tocado | — |
| Smoke MA (`-m smoke --site muebles_america`) | ✅ 5 passed (sin cambio de tamaño) | 108.0s |

Adjunto "Checkout inicial" (run en vivo):
`{"url": "https://mcstage.mueblesamerica.mx/onestepcheckout/", "on_checkout": true, "stage": "entrega", "payment_stage_enabled": false}`.

Pruebas negativas:

- **En vivo, paso 5:** con `campo_inexistente_qa` agregado temporalmente a
  `entry.required_fields`, el caso **falla** (`Campos no marcados como
  obligatorios: ['campo_inexistente_qa']`). Se restauró el dataset en
  `try/finally` y se confirmó con hash que el contenido quedó idéntico al
  de antes de la prueba.
- **Objetos falsos (fuera del repo), 8 de 8 según lo esperado:** fallan
  fuera de la URL del checkout, etapa `forma_de_pago` o sin etapa, "Forma
  de pago" ya habilitada, campo no obligatorio y campo de solo lectura o
  deshabilitado. Pasan los casos válidos.

Simulación de merge (`git merge-tree` del working tree contra `origin/viu`
`cdf85d2`, que ya incluye CHECKOUT_001/002/003, PAY_001 y ORDER_001 de
VIU):

- 0 conflictos de código (solo `plane_catalog.yaml`, que es generado).
- 0 steps duplicados.
- 0 steps faltantes nuevos. Los 3 `@pending` de `payment.feature` ya existían. El verificador vuelve a marcar el falso positivo conocido del paso 3 de CART_002: el step se define con dos literales concatenados y el regex no los une, pero pytest-bdd sí lo resuelve.

## Notas

- **Pendiente: "Sin errores pendientes en carrito".** En stage no apareció
  ningún mensaje de error en el carrito y no hay un caso real para
  verificar un locator. Se puede agregar cuando exista un ejemplo (por
  ejemplo, un producto que se agota con el carrito abierto).
- **Entorno:** este workspace no tiene `.env`, así que CHECKOUT_002/003,
  Customer, Address, Shipping, Payment y Order de MA no se pueden ejecutar
  aquí. Hace falta la identidad `MAVI_GUEST_MA_*` (ver `.env.example`).
- `origin/viu` sigue avanzando (`cdf85d2 CP_EC_VIU_ORDER_001`). La
  simulación de merge se repitió contra esa versión.
