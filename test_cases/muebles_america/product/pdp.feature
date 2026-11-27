# Contrato funcional ejecutable (BDD) — exclusivo de Muebles América.
# Reemplaza al @PDP_001 común en --site muebles_america → CP_EC_MA_PDP_001;
# en otras marcas se descarta (MA-AISLAMIENTO-001). @PDP_002 sigue común.
# Steps en tests/bdd/steps/muebles_america/pdp_steps.py.
@muebles_america
Feature: Página de detalle de producto en Muebles América
  La PDP expone la información para comprar un producto disponible.

  # Intercalado 1:1 con los pasos de Context_Contratos/MA/CP_EC_MA_PDP_001.md.
  @PDP_001 @pdp
  Scenario: Un producto disponible abierto desde la búsqueda tiene la información para comprarlo
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    Then se muestran al menos los resultados mínimos esperados
    And se muestra al menos un producto en el listado
    When selecciona una card elegible y abre su PDP
    Then se abre la PDP del producto seleccionado
    And el producto tiene nombre no vacío
    And el producto expone un identificador válido o se documenta su ausencia
    And el precio es un importe válido mayor a cero
    And la disponibilidad permite comprar el producto
    And la acción de agregar al carrito está disponible y habilitada
