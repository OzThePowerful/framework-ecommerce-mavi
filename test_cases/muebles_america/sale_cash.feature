# Contrato funcional ejecutable (BDD). Los steps viven en tests/bdd/steps/.
Feature: Venta de contado en Muebles América
  Flujo E2E UI: Home → departamento → PDP → carrito → checkout invitado.

  @pending
  Scenario: Navegar al checkout como invitado desde la home
    Given el usuario abre la home de Muebles América
    When navega al departamento "Línea blanca"
    And abre el producto "Campana Decorativa De Pared Midea MJWM7736S3GS"
    And agrega el producto al carrito
    And continúa al checkout como invitado
    Then el checkout muestra el precio del pedido
