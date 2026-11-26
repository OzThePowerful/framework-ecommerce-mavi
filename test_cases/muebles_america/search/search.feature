# Contrato funcional ejecutable (BDD) — exclusivo de Muebles América.
# Reemplaza a @SEARCH_001 / @SEARCH_002 comunes en --site muebles_america
# → CP_EC_MA_SEARCH_001 / CP_EC_MA_SEARCH_002; en otras marcas se
# descarta (MA-AISLAMIENTO-001). Steps en tests/bdd/steps/search_steps.py
# (comunes) y tests/bdd/steps/muebles_america/; términos en
# data/muebles_america/search.yaml vía DataProvider.
@muebles_america
Feature: Búsqueda de productos en Muebles América
  Búsquedas positivas y negativas de Muebles América.

  # Intercalado 1:1 con los pasos de Context_Contratos/MA/CP_EC_MA_SEARCH_001.md.
  # El step de scroll vs contador es cobertura adicional (EC-SP01-010).
  @SEARCH_001 @search
  Scenario: Buscar un término válido muestra resultados navegables
    Given el usuario abre la home del sitio activo
    Then la home queda en estado utilizable
    And el buscador está visible y habilitado
    When captura en el buscador el término con resultados del dataset
    Then el buscador acepta el término capturado
    When ejecuta la búsqueda
    Then la búsqueda se procesa para el término capturado
    And la pantalla de resultados queda disponible
    And se muestran al menos los resultados mínimos esperados
    And se muestra al menos un producto en el listado
    And las cards cargadas por scroll coinciden con el contador de resultados
    And existe al menos una card elegible con nombre, precio e identificador
    And la card elegible abre la PDP del producto

  # Intercalado 1:1 con los pasos de Context_Contratos/MA/CP_EC_MA_SEARCH_002.md.
  # El estado vacío del sitio es el contador "0 resultados de búsqueda".
  @SEARCH_002 @search @negative
  Scenario: Buscar un término sin resultados muestra el estado vacío
    Given el usuario abre la home del sitio activo
    Then la home queda en estado utilizable
    When captura en el buscador el término sin resultados del dataset
    Then el buscador acepta el término capturado
    When ejecuta la búsqueda
    Then la búsqueda se procesa para el término capturado
    And la pantalla de resultados queda disponible
    And no aparece ningún producto en el listado
    And se muestran cero resultados
