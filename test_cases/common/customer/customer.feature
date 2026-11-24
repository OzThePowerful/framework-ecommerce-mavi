# Contrato funcional ejecutable (BDD) — común a todas las marcas.
# La identidad del comprador llega por MAVI_GUEST_* (.env).
#   --site muebles_america → CP_EC_MA_CUSTOMER_001
#   --site viu             → CP_EC_VIU_CUSTOMER_001
Feature: Datos del comprador en checkout
  Contrato común de Customer: la captura del comprador como invitado
  persiste nombre, correo y teléfono verificables en el checkout.

  @CUSTOMER_001
  Scenario: La captura del comprador persiste nombre, correo y teléfono
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    And abre la PDP de una card elegible
    And agrega el producto al carrito
    And abre el carrito de compras
    And continúa al checkout desde el carrito
    And continúa como invitado
    And registra los datos del comprador del dataset
    Then los datos quedan aceptados y la etapa de pago queda habilitada
