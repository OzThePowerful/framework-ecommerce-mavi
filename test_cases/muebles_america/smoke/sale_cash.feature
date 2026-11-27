# Contrato funcional ejecutable (BDD) — exclusivo de Muebles América.
# Reemplaza a @SMOKE_001 común en --site muebles_america → CP_EC_MA_SMOKE_001;
# en otras marcas se descarta (MA-AISLAMIENTO-001).
# Sin steps propios: reutiliza los de Home/Search/PDP/Cart/Checkout de MA y
# los comunes de home, búsqueda, carrito e invitado.
# Restricción del contrato: no confirma pago ni genera pedido (se detiene en
# la primera etapa del checkout).
@muebles_america
Feature: Smoke del flujo de compra de Muebles América
  Comprobación rápida de que las funciones críticas para iniciar una venta
  están operativas: Home → Search → PDP → Add to Cart → Cart → Checkout.

  # Intercalado 1:1 con los pasos de Context_Contratos/MA/CP_EC_MA_SMOKE_001.md.
  @smoke @SMOKE_001
  Scenario: Validar Smoke del flujo de compra previo al pago
    Given el usuario abre la home del sitio activo
    Then la home queda en estado utilizable
    When busca el término con resultados del dataset
    Then la búsqueda se procesa para el término capturado
    And la pantalla de resultados queda disponible
    And se muestra al menos un producto en el listado
    When selecciona una card elegible y abre su PDP
    Then se abre la PDP del producto seleccionado
    And la disponibilidad permite comprar el producto
    When agrega el producto disponible al carrito
    Then el ecommerce procesa la adición del producto
    When espera la confirmación de la adición
    Then el ecommerce confirma la adición del producto
    When abre el carrito de compras
    Then el carrito está disponible
    And el producto registrado está visible en el carrito con cantidad 1
    When continúa al checkout desde el carrito
    Then se muestra la opción de continuar el checkout como invitado
    When continúa como invitado
    Then la primera etapa del checkout queda cargada
