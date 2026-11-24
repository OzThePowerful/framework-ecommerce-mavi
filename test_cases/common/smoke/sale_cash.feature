# Contrato funcional ejecutable (BDD) — común a todas las marcas.
# Delega el recorrido completo al GuestCheckoutWorkflow.
#   --site muebles_america → CP_EC_MA_SMOKE_001
#   --site viu             → CP_EC_VIU_SMOKE_001
Feature: Smoke de venta de contado
  Recorrido rápido Home → departamento → PDP → carrito → checkout como
  invitado que verifica el precio del pedido sin crear la orden.

  @SMOKE_001
  Scenario: Navegar al checkout como invitado muestra el precio del pedido
    Given el usuario abre la home del sitio activo
    When realiza el recorrido de venta de contado hasta el checkout como invitado
    Then el checkout muestra el precio del pedido
