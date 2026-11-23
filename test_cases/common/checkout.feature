Feature: Checkout y datos del comprador
  Contrato común de Checkout/Customer: desde un carrito válido hasta
  registrar correctamente la información requerida del comprador como
  invitado. Se materializa por marca vía --site:
    muebles_america → CP_EC_MA_CHECKOUT_001 / CP_EC_MA_CHECKOUT_002
    viu             → CP_EC_VIU_CHECKOUT_001 / CP_EC_VIU_CHECKOUT_002
  Los datos del comprador y la dirección provienen del DataProvider.
  Fuera de alcance: selección de pago y confirmación de compra.

  Scenario: Acceder al checkout como invitado y exponer los campos requeridos
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    And abre la PDP de una card elegible
    And agrega el producto al carrito
    And abre el carrito de compras
    And continúa al checkout desde el carrito
    And continúa como invitado
    Then la etapa de entrega está activa y los campos del comprador son obligatorios

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
