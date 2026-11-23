Feature: Carrito de compras
  Contrato común de Cart: la transición PDP → Cart conserva la integridad
  comercial del Product y permite continuar al checkout.
  Se materializa por marca vía --site:
    muebles_america → CP_EC_MA_CART_001 / CP_EC_MA_CART_002
    viu             → CP_EC_VIU_CART_001 / CP_EC_VIU_CART_002
  Los términos de búsqueda provienen del dataset del sitio activo.

  Scenario: Agregar un producto y validar la integridad comercial del carrito
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    And abre la PDP de una card elegible
    And agrega el producto al carrito
    And abre el carrito de compras
    Then el carrito contiene el producto con datos coherentes con la PDP
    And los importes del carrito son consistentes con el subtotal y el total

  Scenario: Continuar al checkout desde el carrito muestra la opción de invitado
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    And abre la PDP de una card elegible
    And agrega el producto al carrito
    And abre el carrito de compras
    And continúa al checkout desde el carrito
    Then se muestra la opción de continuar como invitado
