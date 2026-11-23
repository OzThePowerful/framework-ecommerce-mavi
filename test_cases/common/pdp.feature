# Contrato funcional ejecutable (BDD) — común a todas las marcas.
# Los steps viven en tests/bdd/steps/pdp_steps.py; el sitio se elige con
# --site y materializa CP_EC_MA_PDP_001 / CP_EC_VIU_PDP_001.
Feature: Página de detalle de producto
  La PDP expone el modelo de dominio Product independientemente del DOM.

  Scenario: Abrir una PDP desde la búsqueda expone el modelo Product
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    And abre la PDP de una card elegible
    Then el modelo Product tiene nombre, sku e identificador
    And el precio es válido y la disponibilidad cumple las reglas de venta
    And el CTA de agregar al carrito está habilitado

  Scenario: Un configurable expone su padre y sus variantes como Product
    Given el usuario abre la home del sitio activo
    When busca el término del producto configurable del dataset
    And abre la PDP del producto configurable del dataset
    Then el producto es configurable y su sku padre coincide con el dataset
    And cada variante es un Product válido según las reglas de venta
