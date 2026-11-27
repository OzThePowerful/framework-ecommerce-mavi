# Contrato funcional ejecutable (BDD) — exclusivo de Muebles América.
# Reemplaza a @E2E_001 común en --site muebles_america → CP_EC_MA_E2E_001;
# en otras marcas se descarta (MA-AISLAMIENTO-001).
# Steps en tests/bdd/steps/muebles_america/e2e_steps.py (evidencia y
# validaciones de flujo) + los de Home/Search/PDP/Cart/Checkout/Payment/Order
# de MA y los comunes de búsqueda, carrito e invitado. No usa SaleCashWorkflow.
# PRECAUCIÓN: pulsa "Finalizar compra" y crea una orden REAL en el ambiente
# (autorizado solo en stage). Excluir de regresiones con -k "not ORDER and not E2E".
@muebles_america
Feature: Venta de contado de extremo a extremo en Muebles América
  Flujo Home → Search → PDP → Cart → Checkout → Customer → Address →
  Shipping → Payment → Order con evidencia por etapa y las validaciones
  obligatorias de producto, cantidad, precio, subtotal, descuento,
  shipping, total, forma de pago y folio.

  # Flujo del contrato Context_Contratos/MA/CP_EC_MA_E2E_001.md: cada etapa
  # con su acción, su verificación y su evidencia (screenshot; en el
  # checkout con los campos capturados enmascarados). Después, las 9
  # validaciones obligatorias intercaladas 1:1 con la tabla del contrato.
  @E2E_001 @e2e @cash_sale @critical
  Scenario: Validar flujo completo de venta de contado
    # Home
    Given el usuario abre la home del sitio activo
    Then la home queda en estado utilizable
    And queda la evidencia de la etapa "Home"
    # Search
    When busca el término con resultados del dataset
    Then la búsqueda se procesa para el término capturado
    And se muestra al menos un producto en el listado
    And queda la evidencia de la etapa "Search"
    # PDP
    When selecciona una card elegible y abre su PDP
    Then se abre la PDP del producto seleccionado
    And se registran el nombre, el identificador y el precio del producto
    And la disponibilidad permite comprar el producto
    And queda la evidencia de la etapa "PDP"
    # Cart
    When agrega el producto disponible al carrito
    Then el ecommerce procesa la adición del producto
    When espera la confirmación de la adición
    Then el ecommerce confirma la adición del producto
    When abre el carrito de compras
    Then el producto registrado está visible en el carrito con cantidad 1
    And el subtotal del carrito está disponible
    And queda la evidencia de la etapa "Cart"
    # Checkout
    When continúa al checkout desde el carrito
    Then se muestra la opción de continuar el checkout como invitado
    When continúa como invitado
    Then la primera etapa del checkout queda cargada
    And queda la evidencia de la etapa "Checkout"
    # Customer
    When obtiene los datos del comprador del dataset
    And captura el nombre del comprador
    And captura los apellidos del comprador
    And captura el correo del comprador
    And captura el teléfono del comprador
    Then el nombre queda válido
    And los apellidos quedan válidos
    And el correo queda aceptado
    And el teléfono queda aceptado
    And queda la evidencia de la etapa "Customer"
    # Address
    When obtiene el domicilio del dataset
    And captura el código postal del domicilio
    And selecciona la colonia del domicilio
    And completa la calle y el número del domicilio
    And completa la información adicional del domicilio
    Then el domicilio no tiene validaciones pendientes
    And queda la evidencia de la etapa "Address"
    # Shipping
    When consulta los métodos de entrega
    Then se ofrece al menos un método de entrega válido
    When selecciona el método de entrega del dataset
    Then el método de entrega del dataset queda seleccionado
    When obtiene el costo de envío
    Then el costo de envío es un importe observable o envío gratuito
    And queda la evidencia de la etapa "Shipping"
    # Payment
    When llega a la etapa de pago del checkout
    And consulta los métodos de pago disponibles
    And identifica la forma de pago de contado del dataset
    And selecciona la forma de pago de contado
    Then la forma de pago de contado queda marcada como activa
    When completa los datos permitidos del método de contado
    Then la información del método de contado queda aceptada
    And queda la evidencia de la etapa "Payment"
    # Order
    When revisa el resumen final de la compra
    Then la información de la compra está visible en el resumen
    When valida el total antes de confirmar la compra
    Then el total a pagar está disponible
    When ejecuta la confirmación de la compra
    Then la solicitud de compra queda procesada
    When espera la respuesta de la confirmación
    Then la confirmación no produce errores inesperados
    When revisa la página final de la compra
    Then se presenta la confirmación de la compra
    When obtiene el número de orden de la compra
    Then el número de orden es un identificador válido
    When obtiene la información final de la orden
    Then la información final de la orden está disponible
    And queda la evidencia de la etapa "Order"
    # Validaciones obligatorias
    When compara el producto de la orden con la compra
    Then el producto de la orden coincide con la compra
    When compara la cantidad de la orden con la compra
    Then la cantidad de la orden coincide con la compra
    When compara el precio del producto en todo el flujo
    Then el precio del producto es consistente en todo el flujo
    When verifica el subtotal de cada etapa
    Then el subtotal es matemáticamente correcto en cada etapa
    When compara el descuento de la orden con la compra
    Then el descuento de la orden coincide con la compra cuando aplica
    When compara el envío en todo el flujo
    Then el envío es consistente en todo el flujo
    When compara el total de la orden con la compra
    Then el total de la orden coincide con el checkout
    When revisa la forma de pago de la orden
    Then la forma de pago de la orden corresponde a contado
    When revisa el folio de la orden
    Then el folio de la orden es un identificador válido
    When reúne la evidencia de la venta de contado
    Then la venta de contado queda evidenciada de extremo a extremo
