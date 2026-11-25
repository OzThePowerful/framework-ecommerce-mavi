# Contrato funcional ejecutable (BDD) — común a todas las marcas.
# Los steps viven en tests/bdd/steps/search_steps.py y los términos en
# data/<sitio>/search.yaml vía DataProvider. Al ejecutar con --site se
# materializan los casos por marca:
#   --site muebles_america → CP_EC_MA_SEARCH_001 / CP_EC_MA_SEARCH_002
#   --site viu             → CP_EC_VIU_SEARCH_001 / CP_EC_VIU_SEARCH_002
Feature: Búsqueda de productos
  Búsquedas positivas y negativas con un contrato común entre marcas.

  @SEARCH_001
  Scenario: Buscar un término con resultados devuelve cards elegibles
    Given el usuario abre la home del sitio activo
    And el buscador está disponible
    When busca el término con resultados del dataset
    Then se muestran al menos los resultados mínimos esperados
    And las cards cargadas por scroll coinciden con el contador de resultados
    And existe al menos una card elegible con nombre, precio e identificador
    And la card elegible abre la PDP del producto

  @SEARCH_002
  Scenario: Buscar un término sin resultados muestra el estado vacío
    Given el usuario abre la home del sitio activo
    When busca el término sin resultados del dataset
    Then se muestran cero resultados
