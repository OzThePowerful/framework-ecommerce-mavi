# Contrato funcional ejecutable (BDD) — exclusivo de Muebles América.
# Reemplaza a @ORDER_001 común en --site muebles_america → CP_EC_MA_ORDER_001;
# en otras marcas se descarta (MA-AISLAMIENTO-001).
# Steps en tests/bdd/steps/muebles_america/order_steps.py (+ PDP/Cart/
# Checkout/Payment de MA y los comunes de búsqueda, carrito, invitado y entrega).
# PRECAUCIÓN: el escenario pulsa "Finalizar compra" y crea una orden REAL en
# el ambiente (autorizado solo en stage). Excluir de regresiones con
# -k "not ORDER and not E2E".
@muebles_america
Feature: Orden de venta de contado de Muebles América
  Con el checkout completo y la forma de pago de contado seleccionada, el
  usuario confirma la compra y obtiene una orden con folio verificable.

  # Intercalado 1:1 con los pasos de Context_Contratos/MA/CP_EC_MA_ORDER_001.md.
  # Precondiciones (carrito válido, checkout completo, contado seleccionado):
  # steps de PDP/Cart/Checkout/Payment de MA y los comunes de captura del
  # comprador y de entrega. Contado = `payment`/`card` (Tarjeta Crédito /
  # Débito, OpenPay, tarjeta sandbox).
  @ORDER_001 @order @cash_sale
  Scenario: Generar una orden mediante venta de contado
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    And selecciona una card elegible y abre su PDP
    Then se abre la PDP del producto seleccionado
    When agrega el producto disponible al carrito
    And espera la confirmación de la adición
    And abre el carrito de compras
    And continúa al checkout desde el carrito
    And continúa como invitado
    And registra los datos del comprador del dataset
    And selecciona el método de entrega del dataset
    Then el método de entrega del dataset queda seleccionado
    When llega a la etapa de pago del checkout
    And consulta los métodos de pago disponibles
    And identifica la forma de pago de contado del dataset
    And selecciona la forma de pago de contado
    And completa los datos permitidos del método de contado
    And revisa el resumen final de la compra
    Then la información de la compra está visible en el resumen
    When valida el total antes de confirmar la compra
    Then el total a pagar está disponible
    When ejecuta la confirmación de la compra
    Then la solicitud de compra queda procesada
    When espera la respuesta de la confirmación
    Then la confirmación no produce errores inesperados
    When revisa la página final de la compra
    Then se presenta la confirmación de la compra
    When obtiene el número de orden de la compra
    Then el número de orden es un identificador válido
