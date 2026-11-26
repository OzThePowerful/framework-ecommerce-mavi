# Contrato funcional ejecutable (BDD) — exclusivo de Muebles América.
# Reemplaza a @CHECKOUT_001 / @CHECKOUT_002 comunes en --site muebles_america
# → CP_EC_MA_CHECKOUT_001 / _002; en otras marcas se descarta
# (MA-AISLAMIENTO-001). @CHECKOUT_003 sigue común.
# Steps en tests/bdd/steps/muebles_america/checkout_steps.py (+ PDP/Cart de
# MA y los comunes de búsqueda, carrito y entrada como invitado).
@muebles_america
Feature: Checkout de Muebles América
  Desde un carrito válido, el usuario entra al checkout como invitado y
  encuentra disponibles los campos para registrar al comprador.

  # Intercalado 1:1 con los pasos de Context_Contratos/MA/CP_EC_MA_CHECKOUT_001.md.
  # Precondiciones (producto disponible en un carrito válido) reutilizan
  # PDP_001 y CART_001 de MA.
  @CHECKOUT_001 @checkout
  Scenario: Iniciar el checkout desde un carrito válido
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    And selecciona una card elegible y abre su PDP
    Then se abre la PDP del producto seleccionado
    And se registran el nombre, el identificador y el precio del producto
    And la disponibilidad permite comprar el producto
    When agrega el producto disponible al carrito
    Then el ecommerce procesa la adición del producto
    When espera la confirmación de la adición
    And abre el carrito de compras
    Then el carrito está disponible
    And el producto registrado está visible en el carrito con cantidad 1
    When continúa al checkout desde el carrito
    Then se muestra la opción de continuar el checkout como invitado
    When continúa como invitado
    Then la primera etapa del checkout queda cargada
    And los campos requeridos del comprador están disponibles para capturarse

  # Intercalado 1:1 con los pasos de Context_Contratos/MA/CP_EC_MA_CHECKOUT_002.md.
  # Precondición "Checkout iniciado": steps de CHECKOUT_001 de MA.
  # "Continuar" = abrir "Forma de pago"; nunca se pulsa "Finalizar compra".
  @CHECKOUT_002 @checkout @customer
  Scenario: Registrar datos válidos del comprador
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    And selecciona una card elegible y abre su PDP
    Then se abre la PDP del producto seleccionado
    When agrega el producto disponible al carrito
    And espera la confirmación de la adición
    And abre el carrito de compras
    And continúa al checkout desde el carrito
    And continúa como invitado
    Then la primera etapa del checkout queda cargada
    When obtiene los datos del comprador del dataset
    Then los datos del comprador están disponibles
    When captura el nombre del comprador
    Then el nombre queda válido
    When captura los apellidos del comprador
    Then los apellidos quedan válidos
    When captura el correo del comprador
    Then el correo queda aceptado
    When captura el teléfono del comprador
    Then el teléfono queda aceptado
    When completa los demás campos obligatorios del dataset
    Then los datos de dirección quedan aceptados
    When continúa a la forma de pago
    Then no quedan validaciones pendientes del comprador
