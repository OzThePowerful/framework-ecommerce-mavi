# Contrato funcional ejecutable (BDD) — común a todas las marcas.
# Los steps viven en tests/bdd/steps/home_steps.py.
#   --site muebles_america → CP_EC_MA_HOME_001
#   --site viu             → CP_EC_VIU_HOME_001
# Un step por cada paso del contrato (Context_Contratos/MA/CP_EC_MA_HOME_001.md).
Feature: Home del ecommerce
  Contrato común de Home: la página principal carga en estado utilizable,
  se identifica con la marca del sitio activo y ofrece los controles
  mínimos para iniciar un flujo de compra.

  @HOME_001 @smoke @home
  Scenario: La home carga en estado utilizable e identifica la marca
    Given el usuario navega a la URL configurada del sitio activo
    When espera a que finalice la carga inicial de la home
    Then el sitio responde correctamente
    And la home queda en estado utilizable
    And la home se identifica con la marca del sitio activo
    And el buscador está visible y habilitado
    And el acceso al carrito está disponible
    And la navegación principal ofrece los elementos para comenzar una compra
