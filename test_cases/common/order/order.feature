Feature: Confirmación de orden en checkout
  Contrato común de Order: ejecutar la confirmación final y verificar
  que la compra produjo una orden con datos consistentes. Se
  materializa por marca vía --site:
    muebles_america → CP_EC_MA_ORDER_001 / _002
    viu             → CP_EC_VIU_ORDER_001 / _002
  PRECAUCIÓN: cada escenario ejecuta 'Finalizar compra' y crea una
  orden REAL en el ambiente (acción autorizada solo en stage).
  Fuera de alcance: cancelación, devolución o historial de pedidos.

  @ORDER_001
  Scenario: Confirmar la compra genera una orden con folio verificable
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    And abre la PDP de una card elegible
    And agrega el producto al carrito
    And abre el carrito de compras
    And continúa al checkout desde el carrito
    And continúa como invitado
    And registra los datos del comprador del dataset
    And selecciona el método de entrega del dataset
    And abre la etapa de forma de pago
    And selecciona el método de contado del dataset y completa la tarjeta de prueba
    And captura el resumen comercial previo a confirmar
    Then el total del resumen está disponible
    When confirma la compra
    Then se genera una orden con folio y mensaje de confirmación

  @ORDER_002
  Scenario: La orden creada es consistente con los datos comerciales del flujo
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    And abre la PDP de una card elegible
    And agrega el producto al carrito
    And abre el carrito de compras
    And continúa al checkout desde el carrito
    And continúa como invitado
    And registra los datos del comprador del dataset
    And selecciona el método de entrega del dataset
    And abre la etapa de forma de pago
    And selecciona el método de contado del dataset y completa la tarjeta de prueba
    And captura el resumen comercial previo a confirmar
    And confirma la compra
    Then la orden es consistente con producto, carrito, envío, total y pago
    And la orden del dataLayer coincide con el flujo
