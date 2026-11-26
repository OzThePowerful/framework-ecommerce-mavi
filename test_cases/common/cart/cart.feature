Feature: Carrito de compras
  Contrato común de Cart: la transición PDP → Cart conserva la integridad
  comercial del Product y permite continuar al checkout.
  Se materializa por marca vía --site:
    muebles_america → CP_EC_MA_CART_001 / CP_EC_MA_CART_002
    viu             → CP_EC_VIU_CART_001 / CP_EC_VIU_CART_002
  Los términos de búsqueda provienen del dataset del sitio activo.

  @CART_001
  Scenario: Agregar un producto disponible al carrito desde su PDP
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    And abre la PDP de una card elegible
    And agrega el producto al carrito
    And abre el carrito de compras
    Then el producto agregado es visible en el carrito con cantidad 1

  @CART_002
  Scenario: Continuar al checkout desde el carrito muestra la opción de invitado
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    And abre la PDP de una card elegible
    And agrega el producto al carrito
    And abre el carrito de compras
    And continúa al checkout desde el carrito
    Then se muestra la opción de continuar como invitado
