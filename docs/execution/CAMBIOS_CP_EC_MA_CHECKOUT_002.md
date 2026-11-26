# CAMBIOS CP_EC_MA_CHECKOUT_002 — Registrar datos válidos del comprador

## Alcance

Alinear `CP_EC_MA_CHECKOUT_002` con los 7 pasos del contrato
`Context_Contratos/MA/CP_EC_MA_CHECKOUT_002.md`, **solo para Muebles
América** (mecanismo de [MA-AISLAMIENTO-001](CAMBIOS_MA-AISLAMIENTO-001.md)).
El escenario va **intercalado** y captura **campo por campo**.

| # | Paso del contrato | Antes (escenario común) | Ahora (escenario MA) |
|---|---|---|---|
| — | Precondición: checkout iniciado | Steps compartidos sin verificar | Flujo de MA hasta `la primera etapa del checkout queda cargada` (CHECKOUT_001) |
| 1 | Obtener datos → dataset disponible | El fixture fallaba si faltaban variables; sin paso propio | Nombre, apellido, correo, teléfono, calle y CP no vacíos (`.env` vía `guest_customer` + `addresses`/`guadalajara`) |
| 2 | Nombre → campo válido | Un solo step llenaba todo; luego comparaba el nombre | Captura + Tab: el campo conserva el valor y no tiene error |
| 3 | Apellidos → campo válido | Solo comparaba el paterno; el materno no se revisaba | Paterno + materno (si el dataset lo trae; si no, `"ausente"` documentado), cada uno sin error |
| 4 | Correo → aceptado | Comparaba el valor al final | Sin `aria-invalid` ni `#customer-email-error` |
| 5 | Teléfono → aceptado | **No se verificaba** | Sin contenedor `.field._error` (p.ej. "La longitud requerida es mayor o igual a 10 caracteres.") |
| 6 | Otros obligatorios → aceptados | Solo comparaba el CP | Calle, número y CP conservan su valor y no tienen error; el CP autocompleta colonia y ciudad (= dataset) y el estado = dataset |
| 7 | Continuar → sin validaciones pendientes | Sin errores + "Forma de pago" habilitada, **pero no continuaba** | Abre "Forma de pago": etapa `forma_de_pago`, sin errores ni campos inválidos, y los datos del comprador siguen intactos |
| Tags | `@muebles_america @checkout @customer` | Solo `@CHECKOUT_002` | `@muebles_america` (Feature) + `@CHECKOUT_002 @checkout @customer` |

"Continuar" en el OSC es abrir el acordeón **"Forma de pago"**: en la etapa
Entrega no existe un botón "Continuar". **Nunca se pulsa "Finalizar
compra"**, porque crea la orden.

**`CP_EC_VIU_CHECKOUT_002` no cambia.** CHECKOUT_003, Customer, Address,
Shipping, Payment y Order siguen usando el step común `registra los datos
del comprador del dataset`.

## Hallazgo: el apellido materno está marcado como requerido, pero no se exige

`custom_attributes[address_mothers_name]` lleva `required` en el HTML del
OSC de MA. Aun así, con el campo vacío "Forma de pago" se habilita y no
aparece ningún error. El escenario lo trata como **opcional**: lo captura
y verifica si el dataset lo trae (`MAVI_GUEST_MA_MOTHERS_NAME`) y, si no,
lo documenta como `"ausente"`. En la validación de este cambio el dataset
sí lo trae, así que se verificó en vivo. Si negocio lo considera
obligatorio, basta con hacer que falle cuando falta.

## Cambios

| Pieza | Detalle |
|---|---|
| `test_cases/muebles_america/checkout/checkout.feature` | Agrega `@CHECKOUT_002 @checkout @customer` (24 steps) |
| `tests/bdd/steps/muebles_america/checkout_steps.py` | 14 steps (pasos 1–7) + helper `_capture_and_check`. Adjuntos "Datos del comprador", "Apellidos", "Dirección capturada" y "Comprador aceptado", con **correo y teléfono enmascarados** (`a***@e***`, `******5678`) |
| `pages/muebles_america/checkout/checkout_page.py` | `capture_field(name, value)` (fill + Tab), `field_value`, `field_error` (texto del error o `None`), `invalid_fields`, `fill_address` (delega en el `AddressComponent` común) y `continue_to_payment` (espera la habilitación, abre "Forma de pago" y espera a que sea la etapa activa) |
| `pages/muebles_america/checkout/checkout_locators.py` | `PAYMENT_STEP`, `FIELD_ERROR_EXPR` (error por `aria-invalid`, `.field._error` o `#<id>-error`) e `INVALID_FIELDS_EXPR` |
| `pytest.ini` | Marker `customer` |
| `scripts/build_plane_catalog.py` → `test_cases/plane_catalog.yaml` | Bloque `muebles_america` en CHECKOUT_002 con el contrato. Solo cambia la entrada `CP_EC_MA_CHECKOUT_002` |

**No se tocan:** `checkout.feature` y `checkout_steps.py` comunes,
`CustomerFormComponent`, `AddressComponent`, `CommonCheckoutPage` ni nada
de VIU.

Observables verificados en stage MA (desktop 1366×768; sondeo con datos ficticios):

| Situación | Observable |
|---|---|
| Correo inválido + Tab | input `aria-invalid=true` + `div.mage-error#customer-email-error` "Por favor usa una dirección de correo valida." |
| Teléfono de 2 dígitos + Tab | `div.field ... _error` + `div.field-error` "La longitud requerida es mayor o igual a 10 caracteres." (`maxlength` 10) |
| Nombre vacío + Tab | Sin error inmediato |
| Valores corregidos | Desaparecen todos los errores |
| CP 44100 | Colonia `AMERICANA`, ciudad `GUADALAJARA` (solo lectura), estado Jalisco |
| Datos válidos completos | `#paymentExpansionButton` deja de estar `disabled` |
| Clic en "Forma de pago" | Entrega se cierra, Forma de pago `opened`, sin errores |
| Botones de la etapa | Entrega, A tu domicilio, Retiro en sucursal, Forma de pago, Resumen de compra, Aplicar, **Finalizar compra** (no se usa) |

## Comandos

```bash
pytest tests/bdd/test_features.py --case-id CP_EC_MA_CHECKOUT_002   # requiere MAVI_GUEST_MA_* en .env
pytest -m customer --site muebles_america
pytest -m checkout --site muebles_america                         # CHECKOUT_001 + CHECKOUT_002
```

## Requisitos del contrato

| Requisito | Cómo se cumple |
|---|---|
| Datos desde DataProvider (nombre, apellidos, correo, teléfono) | `guest_customer` (`MAVI_GUEST_MA_*`) + `checkout`/`guest` → `addresses` |
| "Más los campos que determine el levantamiento real" | Calle, número y CP (`checkout`/`entry.required_fields`, CHECKOUT_001) + colonia/ciudad autocompletadas; el apellido materno es opcional (ver Hallazgo) |
| Resultado final: datos aceptados y el checkout puede continuar | Paso 7: etapa `forma_de_pago` sin validaciones pendientes |
| Tags `@muebles_america @checkout @customer` | Feature + escenario |
| Asserts fuera de Page Objects | Solo en `tests/bdd/steps/muebles_america/checkout_steps.py` |
| Datos privados | Solo en `.env` (gitignored); en Allure, correo y teléfono enmascarados |

## Validación

Quality Gate:

| Control | Resultado |
|---|---|
| `python -m compileall -q .` | ✅ |
| `ruff check .` | ✅ All checks passed |
| `pytest tests/unit tests/architecture -q` | ✅ 120 passed |
| `--collect-only` MA / VIU | ✅ 21 / 21 (29 recolectados, 8 descartados por marca) |
| `-m checkout` / `-m customer` (MA) | ✅ 2 / 1 |

En vivo (stage, con `.env` local):

| Ejecución | Resultado | Duración |
|---|---|---|
| Línea base previa `CP_EC_MA_CHECKOUT_002` (escenario común) | ✅ | 33.2s |
| `CP_EC_MA_CHECKOUT_002` run 1 / 2 / 3 | ✅ | 36.3s / 30.0s / 29.2s |
| `CP_EC_MA_CHECKOUT_001` (comparte página y steps) | ✅ | 29.1s |
| `CP_EC_MA_CHECKOUT_003` (común; comparte `continúa como invitado`) | ✅ | 28.9s |
| Smoke MA (`-m smoke --site muebles_america`) | ✅ 5 passed (sin cambio de tamaño) | 94.0s |

Adjunto "Comprador aceptado" (run en vivo):
`{"etapa": "forma_de_pago", "errores": [], "campos_invalidos": [], "correo": "v***@g***", "telefono": "******5678"}`.

Pruebas negativas:

- **En vivo, paso 5:** con `MAVI_GUEST_MA_PHONE` de 9 dígitos **solo en el
  proceso de la corrida** (el `.env` no se tocó: hash igual antes y
  después), el caso **falla** con `El campo 'telephone' muestra un error:
  'La longitud requerida es mayor o igual a 10 caracteres.'`. La variable
  temporal se eliminó al terminar.
- **Objetos falsos (fuera del repo), 22 de 22 según lo esperado:**
  - **Fallan:**
    - dataset sin teléfono o sin correo;
    - valor distinto o error en nombre, apellido materno, correo o teléfono;
    - CP sin colonia, ciudad distinta o calle con error;
    - checkout que sigue en `entrega`, error visible, campo inválido o dato que cambió al continuar.
  - **Pasan:** los casos válidos y el apellido materno ausente en el dataset (queda documentado).

Simulación de merge (`git merge-tree` del working tree contra `origin/viu`
`cdf85d2`):

- 0 conflictos de código (solo `plane_catalog.yaml`, que es generado).
- 0 steps duplicados.
- 0 steps faltantes nuevos. Los 3 `@pending` de `payment.feature` ya existían, y sigue el falso positivo conocido del paso 3 de CART_002 (literales concatenados).
- `.env` no forma parte del árbol.

## Notas

- **Entorno:** el caso requiere `MAVI_GUEST_MA_FIRST_NAME`, `_LAST_NAME`,
  `_EMAIL` y `_PHONE` en `.env` (`_MOTHERS_NAME` es opcional). Sin ellas
  falla con `ConfigError` antes de los steps.
- **Validación de correo:** el formulario solo valida el formato. La
  validación externa del correo ocurre al confirmar la orden y queda fuera
  de este caso.
- El nombre vacío no muestra error al salir del campo. El paso 2 verifica
  el valor capturado, no el caso vacío.
