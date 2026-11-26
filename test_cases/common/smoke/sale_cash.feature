# Contrato funcional ejecutable (BDD) — común a todas las marcas.
# Delega el recorrido completo al GuestCheckoutWorkflow.
#   --site muebles_america → CP_EC_MA_SMOKE_001
#   --site viu             → CP_EC_VIU_SMOKE_001
Feature: Smoke de venta de contado
  Recorrido rápido Home → departamento → PDP → carrito → checkout como
  invitado que verifica el precio del pedido sin crear la orden.

  @smoke
  @SMOKE_001
  Scenario: Smoke del flujo de compra previo al pago
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    And abre la PDP de una card elegible
    And agrega el producto al carrito
    And abre el carrito de compras
    Then el producto agregado es visible en el carrito con cantidad 1
    When continúa al checkout desde el carrito
    Then el acceso como invitado está disponible
