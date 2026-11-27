# Contrato funcional ejecutable (BDD) — exclusivo de Muebles América.
# Reemplaza a @PAY_001 común en --site muebles_america → CP_EC_MA_PAY_001;
# en otras marcas se descarta (MA-AISLAMIENTO-001).
# Steps en tests/bdd/steps/muebles_america/payment_steps.py (+ PDP/Cart/
# Checkout de MA y los comunes de búsqueda, carrito, invitado y entrega).
@muebles_america
Feature: Forma de pago de Muebles América
  Con el checkout completo, el usuario selecciona la forma de pago de
  contado y deja la compra lista para finalizar, sin confirmarla.

  # Intercalado 1:1 con los pasos de Context_Contratos/MA/CP_EC_MA_PAY_001.md.
  # Precondiciones (checkout completo, dirección válida y método de entrega
  # seleccionado): steps de PDP/Cart/Checkout de MA y los comunes de
  # captura del comprador y de entrega. Contado = `payment`/`card`
  # (Tarjeta Crédito / Débito, OpenPay). Nunca se pulsa "Finalizar compra".
  @PAY_001 @payment @cash_sale
  Scenario: Seleccionar la forma de pago de contado
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    And selecciona una card elegible y abre su PDP
    Then se abre la PDP del producto seleccionado
    When agrega el producto disponible al carrito
    And espera la confirmación de la adición
    And abre el carrito de compras
    And continúa al checkout desde el carrito
    And continúa como invitado
    And registra los datos del comprador del dataset
    And selecciona el método de entrega del dataset
    Then el método de entrega del dataset queda seleccionado
    When llega a la etapa de pago del checkout
    Then la etapa de pago está disponible
    When consulta los métodos de pago disponibles
    Then se muestran las opciones de pago habilitadas
    When identifica la forma de pago de contado del dataset
    Then el método de contado se encuentra entre las opciones
    When selecciona la forma de pago de contado
    Then la forma de pago de contado queda marcada como activa
    When completa los datos permitidos del método de contado
    Then la información del método de contado queda aceptada
    When revisa el resumen antes de la confirmación
    Then la compra queda lista para finalizar sin confirmarse
