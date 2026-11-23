# CAMBIOS EC-SP01-013 — Levantamiento funcional y técnico de Checkout MA + VIU

**Tipo**: investigación documentada. Sin código nuevo ni abstracciones
comunes (explícitamente fuera de alcance del contrato).

## Entregable

`docs/architecture/levantamiento_checkout.md` — recorrido real del
checkout de ambas marcas hasta el último paso revisable:

- Secuencia completa: carrito → Pagar → gate guest → OSC en subdominio
  propio por marca (`mcstage.mueblesamerica.mx` / `mcstage.viu.mx`).
- Acordeón KO: `Entrega` → `Forma de pago` (bloqueada hasta dirección
  válida) → `Resumen` + `Finalizar compra` (disabled hasta pago válido).
- Inventario de campos por `name` (IDs dinámicos), autocompletado de CP
  (`44100` → Americana/Guadalajara/Jalisco), select
  `colonia_select_shipping`.
- Entrega: `#domicilio` vs `#sucursal` (etiquetas distintas por marca),
  envío "Gratis", estimado de entrega en el resumen.
- Los 5 métodos de pago con `value` y label, por marca.
- Venta de contado: `openpay_cards` (campos nativos, sin iframes;
  tokenización por JS de OpenPay).
- Fronteras externas (OpenPay, PayPal, SPEI, Omnipro) y efecto
  irreversible identificado: `#_btnCheckout` "Finalizar compra" — nunca
  ejecutado durante el levantamiento.
- Riesgos registrados: render lazy KO, `name` duplicados por sección,
  3DS/cargo, selector de tienda pickup pendiente de detalle, login con
  cuenta real.

## Datos actualizados

- `data/<marca>/checkout.yaml`: `shipping_method: "a_domicilio"`,
  `payment_method: "openpay_cards"` (eran `pending`).
- `data/<marca>/payment.yaml`: llaves reales verificadas —
  `openpay_cards` (card), `openpay_stores` (cash), `banktransfer`
  (transfer), `paypal_express`, `omnipro_pago_credito` (crédito de
  marca, no contado); `status: "verified"`.

## Matriz de locators

Sección Checkout enriquecida: botones del acordeón, toggles de entrega,
`#_btnCheckout` marcado irreversible, campos OpenPay, billing
same-as-shipping, promotor, colonia select.

## Diferencias MA vs VIU documentadas

Solo cosméticas: subdominio OSC, etiquetas del crédito de marca y del
pickup. La estructura completa es idéntica.

## Definition of Done

El equipo conoce de forma verificable cómo se ejecuta una venta de
contado en MA y VIU (`openpay_cards` + `Finalizar compra`) y los casos
`CHECKOUT_001/002/003`, `PAY_001`, `ORDER_001/002`, `E2E_001` pueden
implementarse sin inventar reglas de negocio.
