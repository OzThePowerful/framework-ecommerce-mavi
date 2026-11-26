# Contrato funcional ejecutable (BDD) — común a todas las marcas.
# Los steps viven en tests/bdd/steps/pdp_steps.py; el sitio se elige con
# --site y materializa CP_EC_MA_PDP_001 / CP_EC_VIU_PDP_001.
Feature: Página de detalle de producto
  La PDP expone el modelo de dominio Product independientemente del DOM.

  # Intercalado 1:1 con los pasos de Context_Contratos/MA/CP_EC_MA_PDP_001.md.
  @PDP_001 @pdp
  Scenario: Un producto disponible abierto desde la búsqueda tiene la información para comprarlo
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    Then se muestran al menos los resultados mínimos esperados
    And se muestra al menos un producto en el listado
    When abre la PDP de una card elegible
    Then se abre la PDP del producto seleccionado
    And el producto tiene nombre no vacío
    And el producto expone un identificador válido o se documenta su ausencia
    And el precio es un importe válido mayor a cero
    And la disponibilidad permite comprar el producto
    And la acción de agregar al carrito está disponible y habilitada

  @PDP_002
  Scenario: Un configurable expone su padre y sus variantes como Product
    Given el usuario abre la home del sitio activo
    When busca el término del producto configurable del dataset
    And abre la PDP del producto configurable del dataset
    Then el producto es configurable y su sku padre coincide con el dataset
    And cada variante es un Product válido según las reglas de venta
