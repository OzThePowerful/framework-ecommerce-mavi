# CAMBIOS CP_EC_MA_CHECKOUT_003 — Registrar domicilio y seleccionar método de entrega

## Alcance

Alinear `CP_EC_MA_CHECKOUT_003` con los 9 pasos del contrato
`Context_Contratos/MA/CP_EC_MA_CHECKOUT_003.md`, **solo para Muebles
América** (mecanismo de [MA-AISLAMIENTO-001](CAMBIOS_MA-AISLAMIENTO-001.md)).
El escenario va **intercalado** y el domicilio se captura **en el orden del
contrato**: CP → colonia → calle y número → adicionales.

| # | Paso del contrato | Antes (escenario común) | Ahora (escenario MA) |
|---|---|---|---|
| — | Precondición: datos del comprador aceptados | Un step llenaba comprador y domicilio de golpe | Steps de CHECKOUT_002 de MA: nombre, apellidos, correo y teléfono, cada uno sin error |
| 1 | Obtener domicilio → datos disponibles | Sin verificación | Calle, número, CP, colonia, ciudad y estado no vacíos; referencias opcionales (documentadas) |
| 2 | Capturar CP → aceptado | El CP iba al final del llenado, sin verificar | Captura + Tab + espera del autocompletado; valor conservado y sin error |
| 3 | Seleccionar colonia → aceptada | No se revisaba | La colonia del dataset está entre las que ofrece el CP y queda seleccionada (sin distinguir mayúsculas) |
| 4 | Calle y número → válidos | Sin verificación por campo | Valor conservado y sin error en cada uno |
| 5 | Información adicional → sin validaciones pendientes | Sin verificación | Referencias (si las trae el dataset) sin error; ciudad y estado autocompletados = dataset; sin errores ni campos inválidos; "Forma de pago" habilitada |
| 6 | Consultar métodos → al menos uno válido | No se consultaba | `#domicilio` / `#sucursal` visibles (≥ 1) y el del dataset entre ellos |
| 7 | Seleccionar método → seleccionado | Modo activo = dataset | Igual, con step propio |
| 8 | Costo de envío → importe o envío gratuito | `cost >= 0` | La etiqueta del resumen es "Gratis" (importe 0, regla de envío gratuito) o un importe > 0; nunca "Aún no calculado". Se adjunta el estimado |
| 9 | Continuar → siguiente etapa | **No continuaba** | Abre "Forma de pago": etapa `forma_de_pago`, sin errores, domicilio y método de entrega iguales a los registrados |
| Tags | `@muebles_america @checkout @shipping` | Solo `@CHECKOUT_003` | `@muebles_america` (Feature) + `@CHECKOUT_003 @checkout @shipping` |

**`CP_EC_VIU_CHECKOUT_003` no cambia:** sigue corriendo el escenario
común, que `origin/viu` reescribe en su rama (`7f53aa7`).

## Cambios

| Pieza | Detalle |
|---|---|
| `test_cases/muebles_america/checkout/checkout.feature` | Agrega `@CHECKOUT_003 @checkout @shipping` (41 steps) |
| `tests/bdd/steps/muebles_america/checkout_steps.py` | 17 steps (pasos 1–9) + helper `_field_ok`. Adjuntos "Domicilio del dataset", "Colonia", "Domicilio capturado", "Métodos de entrega" y "Costo de envío" |
| `pages/muebles_america/checkout/checkout_page.py` | `capture_postcode` (CP + espera del autocompletado), `colonia_options`, `select_colonia` (por etiqueta, sin distinguir mayúsculas; `None` si no existe), `selected_colonia`, `delivery_options` y `shipping_cost_label` (`"Gratis"`, `"$X"` o `None`) |
| `pages/muebles_america/checkout/checkout_locators.py` | `COLONIA_SELECT`, `DELIVERY_OPTIONS` (`a_domicilio` → `#domicilio`, `sucursal` → `#sucursal`) y `SHIPPING_SUMMARY` |
| `pytest.ini` | Marker `shipping` |
| `scripts/build_plane_catalog.py` → `test_cases/plane_catalog.yaml` | Bloque `muebles_america` en CHECKOUT_003 con el contrato. Solo cambia la entrada `CP_EC_MA_CHECKOUT_003` |

Se reutilizan:
- de CHECKOUT_002 de MA: `capture_field`, `field_value`, `field_error`, `invalid_fields` y `continue_to_payment`;
- de la página común: `read_address`, `shipping_cost` y `delivery_estimate`;
- el step común `selecciona el método de entrega del dataset`, que `origin/viu` no modifica.

**No se tocan:** lo común de Checkout/Shipping ni nada de VIU. Los textos
nuevos evitan los de `origin/viu` (`se presenta al menos un método de
entrega`, `abre la etapa de forma de pago`, `se accede a la etapa de forma
de pago`).

Observables verificados en stage MA (desktop 1366×768; sondeo con datos ficticios y corridas en vivo):

| Paso | Observable |
|---|---|
| Inicial | "A tu domicilio" **ya preseleccionado** (`#domicilio` con `StorePickupSelected`); resumen "Envío: Aún no calculado" |
| 2–3 | CP 44100 → colonias `AMERICANA`, `GUADALAJARA CENTRO`; autoselecciona `AMERICANA`; ciudad `GUADALAJARA` (solo lectura), estado Jalisco |
| 4–5 | Con calle, número y referencias, "Forma de pago" se habilita; sin errores |
| 6 | `["a_domicilio", "sucursal"]` |
| 8 | Resumen "Costo de envío: **Gratis**" → `{"etiqueta": "Gratis", "importe": "0.00", "regla": "envío gratuito"}`; sin estimado de entrega en el resumen |
| 9 | "Forma de pago" `opened`; domicilio y método intactos |

## Comandos

```bash
pytest tests/bdd/test_features.py --case-id CP_EC_MA_CHECKOUT_003   # requiere MAVI_GUEST_MA_* en .env
pytest -m shipping --site muebles_america
pytest -m checkout --site muebles_america                         # CHECKOUT_001/002/003
```

## Requisitos del contrato

| Requisito | Cómo se cumple |
|---|---|
| Datos: calle, número, CP, colonia, municipio/ciudad, estado, referencias | Dataset `addresses`/`guadalajara` (vía `checkout`/`guest.address`); paso 1 exige los 6 primeros; referencias opcionales |
| Datos del comprador aceptados | Precondición con los steps de CHECKOUT_002 de MA |
| Importe observable o regla de envío gratuito | "Gratis" → 0; importe → > 0 (paso 8) |
| Resultado final: dirección y método registrados | Paso 9 compara el domicilio leído y el modo activo después de continuar |
| Tags `@muebles_america @checkout @shipping` | Feature + escenario |
| Asserts fuera de Page Objects | Solo en `tests/bdd/steps/muebles_america/checkout_steps.py` |

## Validación

Quality Gate:

| Control | Resultado |
|---|---|
| `python -m compileall -q .` | ✅ |
| `ruff check .` | ✅ All checks passed |
| `pytest tests/unit tests/architecture -q` | ✅ 120 passed |
| `--collect-only` MA / VIU | ✅ 21 / 21 (30 recolectados, 9 descartados por marca) |
| `-m checkout` / `-m shipping` (MA) | ✅ 3 / 1 |

En vivo (stage, con `.env` local):

| Ejecución | Resultado | Duración |
|---|---|---|
| Línea base previa `CP_EC_MA_CHECKOUT_003` (escenario común) | ✅ | 28.9s |
| `CP_EC_MA_CHECKOUT_003` run 1 / 2 / 3 | ✅ | 28.4s / 26.8s / 27.2s |
| `CP_EC_MA_CHECKOUT_001` (comparte página y steps) | ✅ | 24.0s |
| `CP_EC_MA_CHECKOUT_002` (comparte página y steps) | ✅ | 26.3s |
| Smoke MA (`-m smoke --site muebles_america`) | ✅ 5 passed (sin cambio de tamaño) | 95.6s |

Pruebas negativas:

- **En vivo, paso 3:** con `neighborhood: "Colonia Inexistente QA"` en
  `data/muebles_america/addresses.yaml`, el caso **falla** (`La colonia
  'Colonia Inexistente QA' no está entre las que ofrece el CP:
  ['AMERICANA', 'GUADALAJARA CENTRO']`). El dataset se restauró en
  `try/finally`: hash idéntico y `git diff` vacío.
- **Objetos falsos (fuera del repo), 29 de 29 según lo esperado:**
  - **Fallan:**
    - dataset sin colonia o sin estado;
    - error en CP, número o referencias;
    - colonia no ofrecida o distinta;
    - ciudad distinta, campo inválido o "Forma de pago" deshabilitada;
    - ningún método o método no ofrecido, o método activo distinto;
    - envío no calculado, "Gratis" con importe o importe en 0;
    - no avanza, o domicilio o método cambian al continuar.
  - **Pasan:** los casos válidos y el **envío con importe** (`$199.00`), la rama que en stage no se ve con `parrilla`.

Simulación de merge (`git merge-tree` del working tree contra `origin/viu`
`25a6743`, que ya incluye ORDER_002 y SMOKE_001 de VIU):

- 0 conflictos de código (solo `plane_catalog.yaml`, que es generado).
- 0 steps duplicados.
- 0 steps faltantes nuevos. Los 3 `@pending` de `payment.feature` ya existían, y sigue el falso positivo conocido del paso 3 de CART_002 (literales concatenados).

## Notas

- **Limitación:** con `parrilla` el envío a Guadalajara sale "Gratis". La
  rama "importe > 0" solo está probada con objetos falsos. Para verla en
  vivo haría falta un producto o CP con costo de envío.
- El método `sucursal` se detecta como opción, pero el escenario no lo
  selecciona: el contrato pide un método y el dataset usa `a_domicilio`.
  El retiro en sucursal es SHIPPING_002.
- El número interior queda fuera porque el dataset lo trae vacío y el
  sitio no lo exige.
