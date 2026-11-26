# Contrato funcional ejecutable (BDD) — exclusivo de Muebles América.
# Reemplaza a @CART_001 / @CART_002 comunes en --site muebles_america →
# CP_EC_MA_CART_001 / CP_EC_MA_CART_002; en otras marcas se descarta
# (MA-AISLAMIENTO-001).
# Steps en tests/bdd/steps/muebles_america/cart_steps.py (+ PDP de MA y
# los comunes de búsqueda y carrito).
@muebles_america
Feature: Carrito de compras en Muebles América
  Un producto disponible se agrega al carrito desde su PDP y el carrito
  lo contiene con cantidad 1.

  # Intercalado 1:1 con los pasos de Context_Contratos/MA/CP_EC_MA_CART_001.md.
  # Los dos últimos Then son cobertura adicional (EC-SP01-012).
  @CART_001 @cart
  Scenario: Agregar un producto disponible al carrito desde su PDP
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    And selecciona una card elegible y abre su PDP
    Then se abre la PDP del producto seleccionado
    And se registran el nombre, el identificador y el precio del producto
    And la cantidad seleccionada en la PDP es 1
    When agrega el producto disponible al carrito
    Then el ecommerce procesa la adición del producto
    When espera la confirmación de la adición
    Then el ecommerce confirma la adición del producto
    When abre el carrito de compras
    Then el carrito está disponible
    And el producto registrado está visible en el carrito con cantidad 1
    And el carrito contiene el producto con datos coherentes con la PDP
    And los importes del carrito son consistentes con el subtotal y el total

  # Intercalado 1:1 con los pasos de Context_Contratos/MA/CP_EC_MA_CART_002.md.
  # Las precondiciones (PDP capturada y producto agregado) reutilizan CART_001.
  # El gate de invitado final es cobertura adicional del CART_002 anterior.
  @CART_002 @cart @commercial_validation
  Scenario: El carrito conserva producto, cantidad, precio y subtotal de la PDP
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    And selecciona una card elegible y abre su PDP
    Then se abre la PDP del producto seleccionado
    And se registran el nombre, el identificador y el precio del producto
    When agrega el producto disponible al carrito
    Then el ecommerce procesa la adición del producto
    When espera la confirmación de la adición
    And abre el carrito de compras
    Then el carrito está disponible
    And el nombre del producto en el carrito coincide con la PDP
    And el identificador del producto en el carrito coincide con la PDP o se documenta su ausencia
    And la cantidad en el carrito coincide con la cantidad seleccionada
    And el precio unitario en el carrito coincide con el precio aplicable de la PDP
    And el subtotal del carrito está disponible
    When calcula el subtotal esperado con precisión decimal
    Then el subtotal observado coincide con el esperado
    When continúa al checkout desde el carrito
    Then se muestra la opción de continuar el checkout como invitado
