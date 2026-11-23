Feature: Pago de contado en checkout
  Contrato común de Payment: desde un carrito válido y checkout de
  invitado completo, seleccionar el método de contado y preparar la
  orden hasta la última frontera permitida. Se materializa por marca
  vía --site:
    muebles_america → CP_EC_MA_PAY_001
    viu             → CP_EC_VIU_PAY_001
  La tarjeta llega por variables de entorno MAVI_PAY_* (nunca
  versionada). Fuera de alcance: confirmar la orden — el botón
  'Finalizar compra' se valida habilitado, nunca se ejecuta.

  Scenario: Seleccionar contado y preparar la orden sin confirmarla
    Given el usuario abre la home del sitio activo
    When busca el término con resultados del dataset
    And abre la PDP de una card elegible
    And agrega el producto al carrito
    And abre el carrito de compras
    And continúa al checkout desde el carrito
    And continúa como invitado
    And registra los datos del comprador del dataset
    And selecciona el método de entrega del dataset
    And abre la etapa de forma de pago
    And selecciona el método de contado del dataset y completa la tarjeta de prueba
    Then el método de contado queda seleccionado y la orden lista para confirmar
