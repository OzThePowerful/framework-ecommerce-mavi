# Levantamiento funcional y técnico de Checkout — MA + VIU

**Contrato**: EC-SP01-013 · **Fecha**: 2026-11-23 · **Ambiente**: stage
(`mueblesstage.mavi.mx` / `viustage.mavi.mx`)
**Método**: recorrido real con navegador en ambos sitios, hasta el último
paso revisable. La acción que crea la orden **no se ejecutó**.

## 1. Secuencia del flujo (idéntica en ambas marcas)

```text
PDP → add_to_cart → (toast + promo MA) → minicart (drawer)
  → "Ir al carrito de compras" → /checkout/cart
  → botón "Pagar" → gate identificación (guest / login)
  → "Continuar como invitado" → mcstage.<marca>.mx/onestepcheckout/
  → acordeón "Entrega" (abierto) → acordeón "Forma de pago" (bloqueado
    hasta dirección válida) → "Resumen de compra" + "Finalizar compra"
```

El checkout vive en un **subdominio distinto** por marca:

| Marca | URL del checkout |
|---|---|
| MA | `https://mcstage.mueblesamerica.mx/onestepcheckout/` |
| VIU | `https://mcstage.viu.mx/onestepcheckout/` |

## 2. Estructura Knockout del OneStepCheckout

- Acordeón con botones `#omniButtonShipping` ("Entrega"),
  `#paymentExpansionButton` ("Forma de pago") y `#omniButtonSummary`
  ("Resumen de compra").
- `#paymentExpansionButton` arranca `disabled` y se habilita cuando la
  dirección de envío es válida.
- `#_btnCheckout` ("Finalizar compra") permanece `disabled` hasta que hay
  método de pago seleccionado con datos válidos.
- Los campos se renderizan **lazy** (KO): hay que esperar `:visible` antes
  de interactuar.
- Los `name` se repiten entre secciones (envío, facturación
  `Payment Information`, retiro en sucursal): los locators deben filtrar
  `:visible` o acotar al scope de la sección. Los `id` son dinámicos
  (`Q0U6U6H`-style) — usar `name`/`placeholder`, salvo ids estables
  documentados abajo.

## 3. Campos (idénticos por `name` en ambas)

### Identificación / datos personales

| Campo | `name` | Notas |
|---|---|---|
| Correo | `username` | `id="customer-email"` estable |
| Nombres | `firstname` | Duplicado en sección pickup (oculta) |
| Ap. paterno | `lastname` | |
| Ap. materno | `custom_attributes[address_mothers_name]` | Opcional |
| Teléfono | `telephone` | |
| Crear cuenta | `create-account-checkbox` | "Crear tu cuenta con estos datos." |

### Dirección

| Campo | `name` | Notas |
|---|---|---|
| Calle | `street[0]` | |
| Número | `custom_attributes[address_number]` | |
| CP | `postcode` | `maxlength=5`; **dispara autocompletado** |
| Colonia | `custom_attributes[colonia]` | Input oculto autollenado |
| Colonia (select) | `colonia_select_shipping` | Select de colonias válidas para el CP |
| Ciudad | `city` | Readonly tras CP |
| Estado | `region_id` (select) | Autoseleccionado (44100 → `2334`/Jalisco); 33 opciones |
| País | `country_id` (select) | |
| Referencia | `custom_attributes[address_reference]` | Opcional |

**Autocompletado verificado**: CP `44100` → colonia `AMERICANA`,
ciudad `GUADALAJARA`, estado `Jalisco`, en ambas marcas.

### Entrega

| Elemento | Selector | MA | VIU |
|---|---|---|---|
| Toggle domicilio | `#domicilio` | "A tu domicilio" (default, clase `StorePickupSelected`) | Igual |
| Toggle sucursal | `#sucursal` | "Retiro en sucursal" | **"Click & Pick Up"** |
| Cobertura | — | Label "Verifica la cobertura" observado; la validación ocurre al capturar CP (sin botón propio en lo sondeado) | Igual |
| Estimado | resumen | "Entrega entre el 24 y el 26 de Noviembre." | Igual |
| Costo envío | resumen | `Gratis` | `Gratis` |
| Tras `#sucursal` | — | Resumen muestra "Recoge en tienda"; aparece `button.action` "Seleccionar tienda" | Igual |
| Store picker | `.store-selector-popup` | Modal con tabs `.mavi-tab-button` ("Buscar por estado" / "Buscar por código postal"), `select[name='store-selector-state']`, lista `.location` (`.location-name`/`.location-address`) y `button.action-select-shipping-item` "Entregar aquí"; vacío `.store-selector-popup-empty-query`; cierre `.action-close` | Igual (mapeado en EC-SP01-015) |
| Contacto pickup | — | Tras elegir sucursal: `firstname`, `father-name`, `mother-name`, `phone` | Igual |
| Costo de envío | `.omni-summary-totals` | `Envío`/`Costo de envío` → calcula asíncrono tras el CP ("Aún no calculado" → `Gratis`/importe) | Igual |

### Forma de pago (`input[name='payment[method]']`, 5 métodos en ambas)

| `value` | Label MA | Label VIU | Proveedor | Tipo |
|---|---|---|---|---|
| `omnipro_pago_credito` | Crédito Muebles América | **Mi crédito VIU** | Omnipro (motor de crédito propio) | **Crédito, NO contado** |
| `openpay_cards` | Tarjeta Crédito / Débito | Tarjeta Crédito / Débito | **OpenPay** | **Contado** |
| `paypal_express` | PayPal | PayPal | PayPal (redirección externa) | Contado |
| `banktransfer` | Transferencia bancaria / Pago en tienda | Transferencia bancaria / Pago en tienda | SPEI/transferencia | Contado diferido |
| `openpay_stores` | Efectivo | Efectivo | **OpenPay** (tiendas de conveniencia) | Contado diferido |

### Campos de `openpay_cards` (nativos, **sin iframes**)

| Campo | `name` / `id` |
|---|---|
| Número | `payment[cc_number]` / `#openpay_cards_cc_number` |
| Mes | `payment[cc_exp_month]` / `#openpay_cards_expiration` (select) |
| Año | `payment[cc_exp_year]` / `#openpay_cards_expiration_yr` (select, 2026–2036) |
| CVV | `payment[cc_cid]` / `#openpay_cards_cc_cid` ("What is this?" tooltip) |

- Fieldset: `#payment_form_openpay_cards`, form `#openpay_cards-form`.
- La tokenización va por el JS de OpenPay en página, **no por iframe**
  (iframes funcionales: 0 en ambos; VIU mostró 1 iframe vacío/invisible,
  sin src — placeholder sin efecto).
- Checkbox `billing-address-same-as-shipping` — dirección de facturación
  independiente (duplica los `name` de dirección).
- `input#mavi-promoter-enabled` + label "Num. Empleado:" — promotor/número
  de empleado asociado (sección visible en ambos).
- Cupón: `input#discount-code` (`name=discount_code`) + `#btnAplicarCupon`
  "Aplicar".

### Resumen de compra

Ítem con SKU/cantidad/precio "A:", "Quitar", estimado de entrega,
`Subtotal`, `Costo de envío` (Gratis), `Total (IVA incl.)`, cupón.

## 4. Venta de contado

| Marca | Método contado principal | Identificación | Datos requeridos | Proveedor | Acción que crea la orden |
|---|---|---|---|---|---|
| MA | `openpay_cards` | radio + label "Tarjeta Crédito / Débito" | cc_number, exp_mes/año, cvv + dirección de facturación (o checkbox same-as-shipping) | OpenPay | `#_btnCheckout` "Finalizar compra" |
| VIU | `openpay_cards` | idéntico | idéntico | OpenPay | `#_btnCheckout` "Finalizar compra" |

`openpay_stores`, `banktransfer` y `paypal_express` también son contado
(pago completo, no crédito) pero con confirmación diferida o redirección.
`omnipro_pago_credito` **no** es contado: es el crédito de la marca.

**Limitaciones stage**: se asume que el checkout apunta al sandbox de
OpenPay (sin cargo real), pero no se verificaron las llaves. Con tarjeta
real o datos inválidos el comportamiento puede incluir 3DS o rechazo —
**riesgo a validar al implementar `PAY_001`**.

## 5. Fronteras externas

| Frontera | Dónde | Efecto |
|---|---|---|
| OpenPay JS (tokenización + cargo) | `openpay_cards` / `openpay_stores` | La tarjeta se envía a OpenPay al confirmar; posible 3DS |
| PayPal | `paypal_express` | Redirección fuera del dominio al confirmar |
| SPEI/transferencia | `banktransfer` | Orden con referencia; confirmación fuera de línea |
| Crédito Omnipro | `omnipro_pago_credito` | Evaluación de crédito del cliente |

## 6. Efectos irreversibles

- **`#_btnCheckout` "Finalizar compra" crea la orden** (y dispara el cargo
  en `openpay_cards` / la redirección PayPal). Nunca automatizar su click
  real en stage/prod sin un mecanismo de cancelación o entorno garantizado.
- Todo lo anterior a ese click es revisable y repetible.

## 7. Diferencias MA vs VIU

| Aspecto | MA | VIU |
|---|---|---|
| Subdominio checkout | `mcstage.mueblesamerica.mx` | `mcstage.viu.mx` |
| Crédito de marca | "Crédito Muebles América" | "Mi crédito VIU" |
| Pickup | "Retiro en sucursal" | "Click & Pick Up" |
| Resto del flujo | idéntico | idéntico |

## 8. Riesgos registrados

| Riesgo | Mitigación propuesta |
|---|---|
| IDs dinámicos KO + `name` duplicados por sección | Locators por `name` + filtro `:visible` o scope de sección (`Payment Information`, shipping, pickup) |
| Render lazy de campos | `wait_for(state='visible')` antes de cada fill |
| `_btnCheckout` crea la orden | Los tests `PAY`/`ORDER`/`E2E` llegan hasta la validación previa; el click final solo con estrategia de stage confirmada |
| 3DS / cargo real con tarjeta | Usar tarjetas de prueba de OpenPay sandbox; documentar credenciales por secrets, no por repo |
| Selector de tienda en pickup | **Resuelto en EC-SP01-015**: modal `.store-selector-popup`, lista `.location`, "Entregar aquí" por sucursal |
| Gate guest/login: el login real requiere credenciales de cuenta | Los casos guest están desbloqueados; login requiere fixture de cuenta de prueba |

## 9. Casos desbloqueados

Con este levantamiento, `CHECKOUT_001/002/003`, `PAY_001`, `ORDER_001/002`
y `E2E_001` de ambas marcas pueden implementarse hasta la acción previa a
`Finalizar compra` sin suposiciones. La confirmación de orden
(`ORDER_001/002` con éxito real) depende de definir si stage permite
órdenes de prueba cancelables.

## 10. Verificado en `PAY_001` (EC-SP01-016)

- **Frontera final**: con `openpay_cards` + tarjeta válida, `#_btnCheckout`
  queda **habilitado** en ambas marcas — el framework lo valida, nunca lo
  ejecuta.
- **Tarjetas sandbox OpenPay** (ficticias, versionadas en
  `data/<sitio>/payment.yaml` por decisión del equipo):
  `4111111111111111` contado; `4242424242424242` MSI — MSI también es
  contado, el banco difiere los meses.
- **`openpay_stores`**: límite $30,000 MXN; sobre el monto el radio queda
  `disabled` → `is_method_selectable()` lo detecta (no se validó en vivo
  por costo de armar un carrito >30k; la regla está documentada).
- **`paypal_express`**: abre ventana del proveedor (popup externo; el pago
  ocurre fuera del dominio) → `expects_external_provider()`.
- `PaymentError` (taxonomía `core/execution`) para método no
  seleccionable.

## 11. Verificado en `ORDER_001/002` (EC-SP01-017)

- **El email se valida contra un servicio externo**: dominios ficticios
  (`@example.com`) son **rechazados silenciosamente** al confirmar — el
  click no produce error visible ni navegación. Los datasets usan un
  correo real del equipo.
- **Éxito**: redirect a `…/checkout/onepage/success/`, `.checkout-success`
  con "¡Gracias por tu compra! Hemos recibido tu pedido. Tu N° de pedido
  es: # NNNNNNNNNN". Folio solo como texto (sin selector dedicado).
  La página **no** expone items ni totales — la consistencia comercial
  se verifica contra `.omni-summary-totals` previo a confirmar.
- **Tokenización OpenPay**: ocurre en el submit (`openpay_token` oculto);
  `device_session_id` no es requerido en stage.
- KO valida campos de tarjeta **en blur**: `fill_card` presiona `Tab`
  tras cada campo.
- Órdenes de prueba creadas en stage (referencia): MA `2000058324`,
  `2000058327`, `2000058330`; VIU `12000050087`, `12000050090`.
