Feature: Checkout y datos del comprador
  Contrato común de Checkout/Customer: desde un carrito válido hasta
  registrar correctamente la información requerida del comprador como
  invitado. Se materializa por marca vía --site:
    muebles_america → CP_EC_MA_CHECKOUT_001 / _002 / _003
    viu             → CP_EC_VIU_CHECKOUT_001 / _002 / _003
  Los datos del comprador y la dirección provienen del DataProvider.
  Fuera de alcance: selección de pago y confirmación de compra.

  @CHECKOUT_001
  Scenario: Iniciar el checkout desde un carrito válido
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    And abre la PDP de una card elegible
    And agrega el producto al carrito
    And abre el carrito de compras
    Then el producto agregado es visible en el carrito con cantidad 1
    When continúa al checkout desde el carrito
    Then el acceso como invitado está disponible
    When continúa como invitado
    Then la etapa de entrega está activa y los campos del comprador son obligatorios

  @CHECKOUT_002
  Scenario: Registrar los datos del comprador habilita la etapa de pago
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    And abre la PDP de una card elegible
    And agrega el producto al carrito
    And abre el carrito de compras
    And continúa al checkout desde el carrito
    And continúa como invitado
    And registra los datos del comprador del dataset
    Then los datos quedan aceptados y la etapa de pago queda habilitada

  @CHECKOUT_003
  Scenario: Seleccionar el método de entrega expone el costo de envío
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    And abre la PDP de una card elegible
    And agrega el producto al carrito
    And abre el carrito de compras
    And continúa al checkout desde el carrito
    And continúa como invitado
    And registra los datos del comprador del dataset
    And selecciona el método de entrega del dataset
    Then el método de entrega queda activo y el costo de envío está disponible
