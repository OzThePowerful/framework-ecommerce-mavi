# Contrato funcional ejecutable (BDD) — común a todas las marcas.
# Los steps viven en tests/bdd/steps/home_steps.py.
#   --site muebles_america → CP_EC_MA_HOME_001
#   --site viu             → CP_EC_VIU_HOME_001
Feature: Home del ecommerce
  Contrato común de Home: la página principal carga en estado utilizable
  e identifica inequívocamente la marca del sitio activo.

  @HOME_001
  Scenario: La home carga en estado utilizable e identifica la marca
    Given el usuario abre la home del sitio activo
    Then la home identifica la marca del sitio activo
    And el buscador está accesible
    And el acceso al carrito está disponible
    And la navegación principal está disponible
