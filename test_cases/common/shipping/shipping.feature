# Contrato funcional ejecutable (BDD) — común a todas las marcas.
# Los steps viven en tests/bdd/steps/shipping_steps.py.
#   --site muebles_america → CP_EC_MA_SHIPPING_001 / CP_EC_MA_SHIPPING_002
#   --site viu             → CP_EC_VIU_SHIPPING_001 / CP_EC_VIU_SHIPPING_002
Feature: Método de entrega en checkout
  Contrato común de Shipping: el toggle domicilio/sucursal, el costo de
  envío calculado y el picker de tiendas para recoger en sucursal.

  @SHIPPING_001
  Scenario: La entrega a domicilio expone el costo y la estimación de envío
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

  @SHIPPING_002
  Scenario: El retiro en sucursal permite elegir tienda y registrar el contacto
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    And abre la PDP de una card elegible
    And agrega el producto al carrito
    And abre el carrito de compras
    And continúa al checkout desde el carrito
    And continúa como invitado
    And registra los datos del comprador del dataset
    And selecciona la entrega en sucursal
    And elige una tienda del estado del dataset
    And captura el contacto de recolección del comprador
    Then el modo de entrega queda en sucursal con tienda seleccionada
