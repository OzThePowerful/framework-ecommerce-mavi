# Contrato funcional ejecutable (BDD) — exclusivo de Muebles América.
# Reemplaza al @HOME_001 común en --site muebles_america → CP_EC_MA_HOME_001;
# en otras marcas se descarta (MA-AISLAMIENTO-001).
# Steps en tests/bdd/steps/muebles_america/home_steps.py.
# Un step por cada paso del contrato (Context_Contratos/MA/CP_EC_MA_HOME_001.md).
@muebles_america
Feature: Home de Muebles América
  La página principal carga en estado utilizable, se identifica con la
  marca Muebles América y ofrece los controles mínimos para iniciar un
  flujo de compra.

  @HOME_001 @smoke @home
  Scenario: La home carga en estado utilizable e identifica la marca
    Given el usuario navega a la URL configurada del sitio activo
    When espera a que finalice la carga inicial de la home
    Then el sitio responde correctamente
    And la home queda en estado utilizable
    And la home se identifica con la marca del sitio activo
    And el buscador está visible y habilitado
    And el acceso al carrito está visible y habilitado
    And la navegación principal ofrece los elementos para comenzar una compra
