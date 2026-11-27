# Contrato funcional ejecutable (BDD) — común a todas las marcas.
# Delega el flujo completo al SaleCashWorkflow (workflows/common).
#   --site muebles_america → CP_EC_MA_E2E_001
#   --site viu             → CP_EC_VIU_E2E_001
# PRECAUCIÓN: ejecuta 'Finalizar compra' y crea una orden REAL en el
# ambiente (acción autorizada solo en stage).
Feature: Venta de contado de extremo a extremo
  Flujo consolidado Home → Search → PDP → Cart → Checkout → Customer →
  Address → Shipping → Payment → Order coordinado por SaleCashWorkflow.

  @E2E_001
  Scenario: El flujo completo de venta de contado genera la orden
    Given el usuario prepara una venta de contado con datos de prueba
    When ejecuta el flujo completo de venta de contado
    Then se genera una orden con folio y mensaje de confirmación
    And la integridad comercial del flujo es consistente de extremo a extremo
    And la evidencia de la venta de contado está completa
