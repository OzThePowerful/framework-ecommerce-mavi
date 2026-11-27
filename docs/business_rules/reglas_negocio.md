# Reglas de negocio de las páginas — Framework Ecommerce MAVI

Reglas de negocio del ecommerce (cómo se comporta el sitio) en cada
página del flujo de compra, extraídas del código. No incluye los
criterios de validación del framework ni reglas de arquitectura o
técnicas (ver `docs/standards/`).

- **Generado:** 2026-11-27 sobre la rama `steps-ma` (`1031943`)
- **Marcas:** Muebles América (MA), VIU
- **Cobertura por marca:** en esta rama los escenarios de MA viven en
  `test_cases/muebles_america/` y verifican más comportamiento que el
  contrato común que corre VIU (VIU evoluciona el suyo en `origin/viu`).
  "Verificado solo en MA" indica que la regla se observó y se prueba en
  MA, pero en esta rama ninguna prueba la verifica en VIU. **No** es una
  diferencia de comportamiento.

## Resumen

| Módulo | Reglas | Con diferencia por marca |
|---|---|---|
| Home | 5 | 3 |
| Search | 5 | 0 |
| PDP | 7 | 1 |
| Cart | 4 | 1 |
| Checkout / Customer | 3 | 0 |
| Address | 2 | 0 |
| Shipping | 4 | 0 |
| Payment | 5 | 1 |
| Order | 4 | 0 |
| **Total** | **39** | **6** |

## Home

| ID | Regla | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|
| RN-HOME-01 | La home responde correctamente al abrir la URL configurada del sitio. | Status HTTP 200 ≤ status < 400 | Igual en ambas (verificado solo en MA) | [MA home_steps.py:L41-L46](../../tests/bdd/steps/muebles_america/home_steps.py#L41-L46) |
| RN-HOME-03 | La home se identifica con la marca del sitio: logo visible (enlace a inicio) y título de la página con el nombre de la marca. | `home_001.expected_title_fragment`: MA `"Muebles América"` / VIU `"VIU"` | **Sí**: logo MA = enlace "Página de Inicio" con imagen `muebles-america-logo.png`; fragmento de título distinto. En VIU el título no se verifica en esta rama | [MA home_steps.py:L59-L67](../../tests/bdd/steps/muebles_america/home_steps.py#L59-L67), [MA header_locators.py:L3-L7](../../pages/muebles_america/components/header/header_locators.py#L3-L7), `data/<sitio>/home.yaml` |
| RN-HOME-06 | La navegación principal ofrece "Departamentos" como entrada al catálogo para comenzar una compra. | `home_001.expected_nav_items`: MA `["Departamentos"]` | Verificado solo en MA. Observado en MA: Departamentos, Promociones, Créditos, OUTLET | [MA home_steps.py:L87-L97](../../tests/bdd/steps/muebles_america/home_steps.py#L87-L97), [MA header_locators.py:L6-L7](../../pages/muebles_america/components/header/header_locators.py#L6-L7), [MA home.yaml:L6-L8](../../data/muebles_america/home.yaml#L6-L8) |
| RN-HOME-08 | MA puede mostrar un popup promocional en la home, que se cierra para continuar; VIU no lo muestra. | Aparece solo a veces | **Sí**: solo MA | [MA home_page.py:L21-L25](../../pages/muebles_america/home/home_page.py#L21-L25), [common home_page.py:L61-L62](../../pages/common/pages/home_page.py#L61-L62) |
| RN-HOME-09 | El catálogo se recorre desde el menú de departamentos hasta una categoría. | `guest_checkout.linea_blanca`: MA `Departamentos > Línea blanca`; VIU `Línea blanca > Estufas` | **Sí**: MA tiene 2 niveles (departamento → categoría); VIU, 3 (trigger "Departamentos" → departamento → categoría) | [MA mega_menu_component.py:L18-L51](../../pages/muebles_america/components/mega_menu/mega_menu_component.py#L18-L51), [VIU mega_menu_component.py:L24-L64](../../pages/viu/components/mega_menu/mega_menu_component.py#L24-L64) |

## Search

| ID | Regla | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|
| RN-SEARCH-02 | Ejecutar la búsqueda lleva a la ruta de resultados del término capturado. | Ruta `/catalogsearch/result?q=<término>`; `q` == término | Igual en ambas (verificado solo en MA) | [MA search_steps.py:L38-L48](../../tests/bdd/steps/muebles_america/search_steps.py#L38-L48), [search_component.py:L50-L59](../../pages/common/components/search/search_component.py#L50-L59), [search_locators.py:L6-L7](../../pages/common/components/search/search_locators.py#L6-L7) |
| RN-SEARCH-03 | La pantalla de resultados siempre muestra el contador "N resultados de búsqueda", haya o no coincidencias. | Texto `resultados de búsqueda` | Igual en ambas | [MA search_steps.py:L51-L55](../../tests/bdd/steps/muebles_america/search_steps.py#L51-L55), [search_component.py:L39-L48](../../pages/common/components/search/search_component.py#L39-L48) |
| RN-SEARCH-05 | Las cards cargadas por scroll infinito coinciden con el total que declara el contador. | cards cargadas == contador | Igual en ambas | [search_steps.py:L43-L50](../../tests/bdd/steps/search_steps.py#L43-L50) |
| RN-SEARCH-07 | La card de un producto abre la PDP de ese mismo producto. | El slug del enlace de la card está en la URL de la PDP | Igual en ambas | [search_steps.py:L63-L72](../../tests/bdd/steps/search_steps.py#L63-L72), [MA pdp_steps.py:L44-L60](../../tests/bdd/steps/muebles_america/pdp_steps.py#L44-L60) |
| RN-SEARCH-08 | Un término sin coincidencias muestra el estado vacío: contador en 0 y ningún producto en el listado. El sitio no muestra otro mensaje. | `search.without_results`: término `"zzzz-producto-inexistente-qa"`, `expected_results: 0` en ambas | Igual en ambas | [search_steps.py:L75-L81](../../tests/bdd/steps/search_steps.py#L75-L81), [MA search_steps.py:L75-L81](../../tests/bdd/steps/muebles_america/search_steps.py#L75-L81) |

## PDP

| ID | Regla | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|
| RN-PDP-04 | El precio de lista es `regular_price` (o `original_price`, o `price`) y el vigente es `final_price` (o `price`). Hay precio promocional solo si el vigente es menor que el de lista. | — | Igual en ambas | [pdp_component.py:L36-L53](../../pages/common/components/pdp/pdp_component.py#L36-L53) |
| RN-PDP-06 | Regla de venta por estado: el producto se puede vender si está activo, visible en catálogo y búsqueda, en stock y con existencias. | `is_in_stock` y `qty > 0` y `status == 1` y `visibility == 4` | Igual en ambas | [pdp_component.py:L63-L72](../../pages/common/components/pdp/pdp_component.py#L63-L72), [pdp_steps.py:L55-L71](../../tests/bdd/steps/pdp_steps.py#L55-L71) |
| RN-PDP-07 | La PDP muestra una etiqueta de disponibilidad: **Disponible**, **Agotado** o **Solo queda N** / **Solo quedan N** (pocas piezas). Solo "Disponible" y "Solo queda(n) N" con N ≥ 1 permiten comprar. La etiqueta llega después de cargar la página (la consulta un servicio de stock aparte) y prevalece sobre el estado interno, que puede marcar en stock un producto agotado. | Servicio `/api/stock/check`. Observado en stage MA (2026-11-27): `MABE00902` → "Solo quedan 24"; `WHIR00789` → "Solo quedan 12". El umbral de "Solo queda(n) N" se configura en el backend | Verificado solo en MA | [MA product_locators.py:L5-L23](../../pages/muebles_america/product/product_locators.py#L5-L23), [MA product_page.py:L23-L33](../../pages/muebles_america/product/product_page.py#L23-L33), [MA pdp_steps.py:L19-L20](../../tests/bdd/steps/muebles_america/pdp_steps.py#L19-L20), [MA pdp_steps.py:L128-L149](../../tests/bdd/steps/muebles_america/pdp_steps.py#L128-L149) |
| RN-PDP-09 | La acción de agregar al carrito está visible y habilitada. En un producto agotado no existe. | — | Igual en ambas | [pdp_component.py:L74-L86](../../pages/common/components/pdp/pdp_component.py#L74-L86), [pdp_steps.py:L74-L78](../../tests/bdd/steps/pdp_steps.py#L74-L78), [MA pdp_steps.py:L152-L157](../../tests/bdd/steps/muebles_america/pdp_steps.py#L152-L157) |
| RN-PDP-10 | Un producto configurable tiene un SKU padre y variantes hijas. El SKU padre lleva un prefijo propio de cada marca; los SKU hijos son compartidos. | `products.configurable_colchon`: término `"winer"`, 4 variantes; padre MA `1COLC08920` / VIU `2COLC08920` | **Sí**: prefijo del padre (1 en MA, 2 en VIU) | [pdp_component.py:L95-L102](../../pages/common/components/pdp/pdp_component.py#L95-L102), [pdp_steps.py:L100-L110](../../tests/bdd/steps/pdp_steps.py#L100-L110), `data/<sitio>/products.yaml` |
| RN-PDP-11 | Cada variante es vendible si está en stock, con existencias y activa. La regla de visibilidad aplica solo al padre (los hijos no se exhiben solos). | `is_in_stock` y `qty > 0` y `status == 1`; hijos con `visibility = 1` | Igual en ambas | [pdp_component.py:L104-L134](../../pages/common/components/pdp/pdp_component.py#L104-L134), [pdp_steps.py:L112-L136](../../tests/bdd/steps/pdp_steps.py#L112-L136) |
| RN-PDP-12 | La PDP llega con cantidad 1 preseleccionada; no hay selector de cantidad visible. | Cantidad mostrada `"1"` | Verificado solo en MA | [pdp_component.py:L59-L61](../../pages/common/components/pdp/pdp_component.py#L59-L61), [MA product_page.py:L35-L41](../../pages/muebles_america/product/product_page.py#L35-L41), [MA cart_steps.py:L55-L63](../../tests/bdd/steps/muebles_america/cart_steps.py#L55-L63) |

## Cart

| ID | Regla | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|
| RN-CART-01 | Agregar al carrito se confirma con una notificación que nombra el producto. En MA, algunos artículos muestran además una ventana de promociones. | MA: "Tu producto … ha sido agregado a tu carrito de compras." | **Sí**: la ventana de promociones solo existe en MA. El aviso de MA enlaza al carrito; el de VIU se acepta y el carrito se abre desde el header | [MA product_page.py:L43-L82](../../pages/muebles_america/product/product_page.py#L43-L82), [VIU product_page.py:L14-L45](../../pages/viu/product/product_page.py#L14-L45), [promotions_window_component.py:L15-L29](../../pages/muebles_america/components/promotions_window/promotions_window_component.py#L15-L29), [MA cart_steps.py:L103-L124](../../tests/bdd/steps/muebles_america/cart_steps.py#L103-L124) |
| RN-CART-03 | En el carrito, un precio tachado es el de lista y el precio vigente es el promocional. Sin tachado, el vigente es el de lista. | — | Igual en ambas | [cart_component.py:L61-L75](../../pages/common/components/cart/cart_component.py#L61-L75) |
| RN-CART-06 | Desde el carrito se continúa al checkout, que ofrece "Continuar como invitado". | — | Igual en ambas | [cart_steps.py:L105-L111](../../tests/bdd/steps/cart_steps.py#L105-L111), [MA cart_steps.py:L265-L272](../../tests/bdd/steps/muebles_america/cart_steps.py#L265-L272), [checkout_component.py:L30-L36](../../pages/common/components/checkout/checkout_component.py#L30-L36) |
| RN-CART-07 | Al agregar, el producto queda registrado en el carrito del servidor (con su cantidad) y el contador del carrito en el header se actualiza. | Estado `cart.cartItems` con `sku`, `qty` y `server_item_id` (`POST /api/cart/update` → 200); minicart "Carrito 1" | Verificado solo en MA | [MA cart_locators.py:L3-L12](../../pages/muebles_america/cart/cart_locators.py#L3-L12), [MA cart_page.py:L23-L54](../../pages/muebles_america/cart/cart_page.py#L23-L54), [MA cart_steps.py:L79-L91](../../tests/bdd/steps/muebles_america/cart_steps.py#L79-L91) |

## Checkout / Customer

| ID | Regla | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|
| RN-CHECKOUT-01 | Continuar como invitado lleva al checkout de una página (OneStepCheckout). | Patrón de URL por marca y ambiente en `config/sites.yaml` (`checkout_url_pattern`) | Igual en ambas | [checkout_component.py:L38-L47](../../pages/common/components/checkout/checkout_component.py#L38-L47), [MA checkout_page.py:L18-L40](../../pages/muebles_america/checkout/checkout_page.py#L18-L40) |
| RN-CHECKOUT-02 | Al entrar, la etapa activa es "Entrega" y son obligatorios correo, nombre, apellido, teléfono, calle, número exterior y código postal. La ciudad es de solo lectura (la llena el código postal). | Campos `username`, `firstname`, `lastname`, `telephone`, `street[0]`, `custom_attributes[address_number]`, `postcode` (MA: `checkout.entry.required_fields`) | Igual en ambas | [checkout_steps.py:L45-L61](../../tests/bdd/steps/checkout_steps.py#L45-L61), [MA checkout_steps.py:L55-L102](../../tests/bdd/steps/muebles_america/checkout_steps.py#L55-L102), [MA checkout.yaml:L13-L25](../../data/muebles_america/checkout.yaml#L13-L25) |
| RN-CHECKOUT-03 | El checkout avanza por etapas: Entrega → Forma de pago → Resumen. "Forma de pago" está deshabilitada al entrar y se habilita solo después de aceptar los datos del comprador y la dirección. | — | Igual en ambas | [checkout_component.py:L17-L21](../../pages/common/components/checkout/checkout_component.py#L17-L21), [checkout_component.py:L65-L78](../../pages/common/components/checkout/checkout_component.py#L65-L78), [MA checkout_steps.py:L281-L306](../../tests/bdd/steps/muebles_america/checkout_steps.py#L281-L306) |

## Address

| ID | Regla | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|
| RN-ADDRESS-01 | Capturar el código postal autocompleta la colonia, la ciudad y el estado. La colonia es una lista con las colonias del código postal y el sitio preselecciona la primera. | `addresses.guadalajara`: CP `44100` → colonias AMERICANA, GUADALAJARA CENTRO (se preselecciona AMERICANA) / Guadalajara / Jalisco, en ambas | Igual en ambas (la lista de colonias, verificada solo en MA) | [address_component.py:L29-L68](../../pages/common/components/checkout/address_component.py#L29-L68), [address_steps.py:L14-L28](../../tests/bdd/steps/address_steps.py#L14-L28), [MA checkout_locators.py:L14-L16](../../pages/muebles_america/checkout/checkout_locators.py#L14-L16), [MA checkout_steps.py:L365-L404](../../tests/bdd/steps/muebles_america/checkout_steps.py#L365-L404) |
| RN-ADDRESS-02 | El sitio normaliza a mayúsculas los campos autocompletados. La comparación no distingue mayúsculas. | — | Igual en ambas | [address_steps.py:L19-L28](../../tests/bdd/steps/address_steps.py#L19-L28) |

## Shipping

| ID | Regla | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|
| RN-SHIPPING-01 | Hay dos modos de entrega: a domicilio y retiro en sucursal. Solo uno queda activo, y "A tu domicilio" viene preseleccionado. | `a_domicilio`, `sucursal`; `checkout.guest.shipping_method: "a_domicilio"` en ambas | Igual en ambas (la preselección, verificada solo en MA) | [shipping_component.py:L21-L53](../../pages/common/components/checkout/shipping_component.py#L21-L53), [MA checkout_locators.py:L17-L18](../../pages/muebles_america/checkout/checkout_locators.py#L17-L18), [MA checkout_steps.py:L471-L497](../../tests/bdd/steps/muebles_america/checkout_steps.py#L471-L497) |
| RN-SHIPPING-03 | El retiro en sucursal requiere elegir estado y sucursal ("Entregar aquí") y capturar el contacto de quien recoge: nombre, apellido paterno y teléfono (apellido materno opcional). | `checkout.guest.store_state: "Jalisco"` en ambas; se elige la primera sucursal | Igual en ambas | [shipping_component.py:L56-L125](../../pages/common/components/checkout/shipping_component.py#L56-L125), [shipping_steps.py:L15-L50](../../tests/bdd/steps/shipping_steps.py#L15-L50) |
| RN-SHIPPING-04 | El costo de envío se calcula al completar el domicilio: antes, el resumen muestra "Envío: Aún no calculado"; después, "Costo de envío: Gratis" o un importe. | `MABE00902` a domicilio en CP 44100 → "Gratis" (observado) | Verificado solo en MA | [MA checkout_locators.py:L19-L20](../../pages/muebles_america/checkout/checkout_locators.py#L19-L20), [MA checkout_page.py:L124-L135](../../pages/muebles_america/checkout/checkout_page.py#L124-L135), [shipping_component.py:L134-L162](../../pages/common/components/checkout/shipping_component.py#L134-L162), [MA checkout_steps.py:L500-L529](../../tests/bdd/steps/muebles_america/checkout_steps.py#L500-L529) |
| RN-SHIPPING-05 | El resumen del checkout muestra, por producto, la fecha estimada de entrega ("Entrega entre el X y el Y"). | p.ej. "Entrega entre el 28 y el 30 de Noviembre." | Verificado solo en MA | [MA checkout_locators.py:L22-L25](../../pages/muebles_america/checkout/checkout_locators.py#L22-L25), [MA checkout_page.py:L153-L188](../../pages/muebles_america/checkout/checkout_page.py#L153-L188), [MA order_steps.py:L78](../../tests/bdd/steps/muebles_america/order_steps.py#L78) |

## Payment

| ID | Regla | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|
| RN-PAYMENT-01 | Métodos de pago: tarjeta de crédito/débito de contado, efectivo en tiendas, transferencia, PayPal y crédito de la marca. El crédito de la marca **no** es contado. | `openpay_cards` "Tarjeta Crédito / Débito", `openpay_stores` "Efectivo", `banktransfer` "Transferencia bancaria / Pago en tienda", `paypal_express` "PayPal", `omnipro_pago_credito` "Crédito Muebles América" (nombres observados en stage MA, `CAMBIOS_CP_EC_MA_PAY_001.md`; en el código solo está el de la tarjeta, `payment.card.label`) | **Sí**: el crédito de la marca se llama "Mi crédito VIU" en VIU | [MA payment.yaml:L15-L51](../../data/muebles_america/payment.yaml#L15-L51), [VIU payment.yaml:L10-L43](../../data/viu/payment.yaml#L10-L43), [MA payment_locators.py:L4-L5](../../pages/muebles_america/payment/payment_locators.py#L4-L5), [MA payment_steps.py:L115-L132](../../tests/bdd/steps/muebles_america/payment_steps.py#L115-L132) |
| RN-PAYMENT-02 | Un método de pago solo se puede elegir si está presente y habilitado para el carrito; el sitio lo habilita de forma asíncrona. Ningún método viene preseleccionado y, sin método, el botón "Finalizar compra" está deshabilitado. | — | Igual en ambas (sin preselección y botón deshabilitado: verificado solo en MA) | [payment_component.py:L44-L75](../../pages/common/components/payment/payment_component.py#L44-L75), [MA payment_steps.py:L80-L102](../../tests/bdd/steps/muebles_america/payment_steps.py#L80-L102) |
| RN-PAYMENT-04 | PayPal saca al comprador del dominio del ecommerce (ventana o redirección del proveedor). | `paypal_express` | Igual en ambas | [payment_locators.py:L33-L34](../../pages/common/components/payment/payment_locators.py#L33-L34), [payment_component.py:L94-L96](../../pages/common/components/payment/payment_component.py#L94-L96) |
| RN-PAYMENT-05 | Al elegir un método, su bloque queda marcado como activo y el botón de confirmación cambia de "Finalizar compra" a "Pagar con <método>". | p.ej. "Pagar con Tarjeta Crédito / Débito" | Verificado solo en MA | [MA payment_locators.py:L8-L9](../../pages/muebles_america/payment/payment_locators.py#L8-L9), [MA payment_page.py:L53-L64](../../pages/muebles_america/payment/payment_page.py#L53-L64), [MA payment_steps.py:L143-L165](../../tests/bdd/steps/muebles_america/payment_steps.py#L143-L165) |
| RN-PAYMENT-06 | El pago con tarjeta exige número, vencimiento y CVV; el botón de confirmación se habilita solo con los datos completos. La facturación usa por defecto la dirección de entrega ("Utilizar dirección de Entrega"). | `payment.card` (tarjeta sandbox OpenPay) | Verificado solo en MA | [MA payment.yaml:L12-L14](../../data/muebles_america/payment.yaml#L12-L14), [MA payment_steps.py:L179-L203](../../tests/bdd/steps/muebles_america/payment_steps.py#L179-L203), [MA payment_steps.py:L212-L253](../../tests/bdd/steps/muebles_america/payment_steps.py#L212-L253) |

## Order

| ID | Regla | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|
| RN-ORDER-01 | Una compra es exitosa solo si se llega a la página de éxito, se ve la confirmación y hay folio legible. La página dice "¡Gracias por tu compra! Hemos recibido tu pedido." y "Tu N° de pedido es: # <folio>", y avisa que llegará un correo de confirmación. | URL `…/checkout/onepage/success/`, contenedor `.checkout-success`, encabezado `.page-title`; folio de 10 dígitos en MA (p.ej. `2000059239`) | Igual en ambas (textos verificados solo en MA) | [order_component.py:L26-L57](../../pages/common/components/order/order_component.py#L26-L57), [MA order_page.py:L27-L32](../../pages/muebles_america/order/order_page.py#L27-L32), [MA order_steps.py:L180-L195](../../tests/bdd/steps/muebles_america/order_steps.py#L180-L195) |
| RN-ORDER-03 | Si el pago se rechaza, el checkout muestra el mensaje de declinación y no hay orden. | — | Igual en ambas | [order_component.py:L32-L37](../../pages/common/components/order/order_component.py#L32-L37), [order_component.py:L77-L83](../../pages/common/components/order/order_component.py#L77-L83) |
| RN-ORDER-05 | Al confirmar, OpenPay tokeniza la tarjeta y Magento crea la orden (la respuesta devuelve el id interno de la orden, distinto del folio); después se registra el resultado y el sitio redirige a la página de éxito. | `POST …/guest-carts/<id>/checkout-information` → token OpenPay (201) → `POST …/guest-carts/<id>/payment-information` (200, p.ej. `"65770"`) → `…/mavi-placeorderhistory/…/saveResponseResult` | Verificado solo en MA | [MA payment_locators.py:L11-L16](../../pages/muebles_america/payment/payment_locators.py#L11-L16), [MA payment_page.py:L89-L127](../../pages/muebles_america/payment/payment_page.py#L89-L127), [MA order_steps.py:L128-L166](../../tests/bdd/steps/muebles_america/order_steps.py#L128-L166) |
| RN-ORDER-06 | La página de éxito publica la orden en el `dataLayer` (eventos `purchase` de GA4 y de MAVI): folio, total, envío, cupón, productos (SKU, nombre, precio, precio sin descuento, cantidad) y tipo de pago. Una venta con tarjeta se informa como **contado**. Es la única fuente de la orden final visible desde la UI. | `transaction_id` = folio; `tipo_pago: "contado"` (`payment.card.sale_type` en MA) | Verificado solo en MA | [MA order_locators.py:L1-L19](../../pages/muebles_america/order/order_locators.py#L1-L19), [MA order_page.py:L35-L69](../../pages/muebles_america/order/order_page.py#L35-L69), [MA order_steps.py:L266-L285](../../tests/bdd/steps/muebles_america/order_steps.py#L266-L285), [MA payment.yaml:L19](../../data/muebles_america/payment.yaml#L19) |

## Notas

- **Límite de efectivo $30,000 MXN (sin automatizar):** `payment.yaml` de ambas marcas (`cash.max_amount_mxn: 30000`) y el docstring de [payment_component.py:L47-L48](../../pages/common/components/payment/payment_component.py#L47-L48) dicen que el efectivo (`openpay_stores`) no se puede elegir con un carrito > $30,000. El escenario `PAY_002` está `@pending` y no tiene steps: **ninguna prueba lo verifica**.
- **Meses sin intereses (sin automatizar):** la tarjeta MSI de sandbox (`card_msi`) está en `payment.yaml`, pero `PAY_003` está `@pending`, sin steps.
- **Disponibilidad en el flujo de venta:** los escenarios de MA exigen la etiqueta de la PDP (RN-PDP-07). El escenario común (VIU) y el `SaleCashWorkflow` deciden con la regla de estado (RN-PDP-06): un producto "Agotado" con estado "en stock" solo lo detendría el botón ausente (RN-PDP-09).
- **Hallazgo en stage (VIU):** `WHIR00686` tiene estado "en stock, 6 piezas", pero la PDP lo muestra "Agotado" y sin botón de carrito. Por eso el término de búsqueda de VIU es `MABE00888` (`data/viu/search.yaml`).
- **Hallazgo en stage (MA, 2026-11-27):** algunas cards de la búsqueda no muestran precio aunque la PDP sí lo tiene (p.ej. `WHIR00789` en "parrilla": card sin precio, PDP $11,189.00). Ninguna prueba lo verifica como regla. El escenario común de E2E falla por esto en MA (lee el precio de la primera card).
- **Etiqueta de stock bajo en plural (MA, 2026-11-27):** el sitio pasó a mostrar "Solo quedan N" para N > 1 (antes se había observado "Solo queda N"). RN-PDP-07 acepta ambas.
- **Validación por campo en el checkout (observada en MA, sin prueba negativa):** un correo inválido marca el campo con error y un mensaje debajo; un teléfono corto marca el campo con error; al corregirlos, el error desaparece ([MA checkout_locators.py:L7-L10](../../pages/muebles_america/checkout/checkout_locators.py#L7-L10)). Las pruebas solo verifican que los datos válidos se aceptan sin error.
- **Correo del comprador (mencionado, sin prueba):** según EC-SP01-017, el checkout valida el correo contra un servicio externo y rechaza en silencio los dominios ficticios (`@example.com`); por eso la identidad del comprador es real y vive en `.env` (`MAVI_GUEST_<SITIO>_*`).
- **Consulta de la orden (observado en MA, sin prueba):** la consulta de pedidos de invitado (`/sales/guest/form`) da 404 y "Mis pedidos" (`/my-account/orders`) requiere iniciar sesión; por eso la orden final se lee del `dataLayer` (RN-ORDER-06).
- **Importes con envío y descuento:** las reglas de envío, descuento y total solo se han observado con envío gratis y sin promoción (`MABE00902`).

## Historial

| Fecha | Commit | Cambios |
|---|---|---|
| 2026-11-26 | `f331422` | Versión inicial: 56 reglas en 11 módulos |
| 2026-11-26 | `01a0a6c` | Alcance reducido a reglas del ecommerce: 25 criterios de validación del framework retirados (RN-HOME-02, 04, 05, 07; RN-SEARCH-01, 04, 06; RN-PDP-01, 02, 03, 05, 08; RN-CART-02, 04, 05; RN-CHECKOUT-04, 05; RN-SHIPPING-02; RN-PAYMENT-03; RN-ORDER-02, 04; RN-VENTA-01, 02; RN-DOMINIO-01, 02). Quedan 31 reglas en 9 módulos; los IDs vigentes no cambian |
| 2026-11-27 | `1031943` | Actualización tras MA-AISLAMIENTO-001 y los contratos de MA (CART, CHECKOUT, PAY, ORDER, SMOKE, E2E): 8 nuevas (RN-PDP-12, RN-CART-07, RN-SHIPPING-04, 05, RN-PAYMENT-05, 06, RN-ORDER-05, 06); 21 con fuentes o valores actualizados; 0 retiradas. Total 39 reglas en 9 módulos |
