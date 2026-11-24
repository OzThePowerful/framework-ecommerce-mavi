# Contrato funcional ejecutable (BDD) — común a todas las marcas.
# La dirección llega por data/<sitio>/addresses.yaml vía DataProvider.
#   --site muebles_america → CP_EC_MA_ADDRESS_001
#   --site viu             → CP_EC_VIU_ADDRESS_001
Feature: Dirección de entrega en checkout
  Contrato común de Address: el código postal dispara el lookup que
  autocompleta colonia, ciudad y estado del domicilio.

  @ADDRESS_001
  Scenario: La dirección autocompleta colonia, ciudad y estado desde el código postal
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    And abre la PDP de una card elegible
    And agrega el producto al carrito
    And abre el carrito de compras
    And continúa al checkout desde el carrito
    And continúa como invitado
    And registra los datos del comprador del dataset
    Then la dirección autocompleta colonia, ciudad y estado del dataset
