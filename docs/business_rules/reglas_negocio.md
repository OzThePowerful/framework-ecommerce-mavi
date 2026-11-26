# Reglas de negocio de las páginas — Framework Ecommerce MAVI

Reglas funcionales que el framework implementa y verifica en cada página
del flujo de compra, extraídas del código. No incluye reglas de
arquitectura ni técnicas (ver `docs/standards/`).

- **Generado:** 2026-11-26 sobre la rama `steps-ma` (`f331422`)
- **Marcas:** Muebles América (MA), VIU
- **Tipos:** *Ecommerce* = comportamiento del sitio · *Validación* = criterio con que el framework acepta o elige
- Los datos privados (identidad del comprador) viven en `.env` (`MAVI_GUEST_<CODE>_*`) y no se copian aquí.

## Resumen

| Módulo | Reglas | Ecommerce | Validación | Con diferencia por marca |
|---|---|---|---|---|
| Home | 9 | 5 | 4 | 3 |
| Search | 8 | 5 | 3 | 1 |
| PDP | 11 | 6 | 5 | 1 |
| Cart | 6 | 3 | 3 | 1 |
| Checkout / Customer | 5 | 3 | 2 | 1 |
| Address | 2 | 2 | 0 | 0 |
| Shipping | 3 | 2 | 1 | 0 |
| Payment | 4 | 3 | 1 | 1 |
| Order | 4 | 2 | 2 | 0 |
| Flujo de venta de contado | 2 | 0 | 2 | 1 |
| Dominio (transversal) | 2 | 0 | 2 | 0 |
| **Total** | **56** | **31** | **25** | **9** |

## Home

| ID | Regla | Tipo | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|---|
| RN-HOME-01 | La home responde correctamente al abrir la URL configurada del sitio. | Ecommerce | Status HTTP 200 ≤ status < 400 | Igual en ambas | [home_steps.py:L39-L45](../../tests/bdd/steps/home_steps.py#L39-L45) |
| RN-HOME-02 | Tras la carga inicial (y descartar el banner de cookies) la home queda utilizable: header visible y ningún overlay bloqueando la interacción. | Validación | — | Igual en ambas | [home_steps.py:L47-L54](../../tests/bdd/steps/home_steps.py#L47-L54), [home_page.py:L43-L57](../../pages/common/pages/home_page.py#L43-L57) |
| RN-HOME-03 | La home se identifica con la marca del sitio: logo visible y título de la página con el nombre de la marca. | Ecommerce | `home_001.expected_title_fragment`: MA `"Muebles América"` / VIU `"VIU"` | **Sí**: logo MA = imagen (`muebles-america-logo.png`); VIU = SVG. Fragmento de título distinto | [home_steps.py:L57-L66](../../tests/bdd/steps/home_steps.py#L57-L66), [header_locators.py:L19](../../pages/common/components/header/header_locators.py#L19), `data/<sitio>/home.yaml` |
| RN-HOME-04 | El buscador del header está visible y habilitado para capturar un término. | Validación | — | Igual en ambas | [home_steps.py:L69-L74](../../tests/bdd/steps/home_steps.py#L69-L74), [header_component.py:L32-L35](../../pages/common/components/header/header_component.py#L32-L35) |
| RN-HOME-05 | El acceso al carrito del header está visible y habilitado. | Validación | — | Igual en ambas | [home_steps.py:L77-L82](../../tests/bdd/steps/home_steps.py#L77-L82), [header_component.py:L37-L40](../../pages/common/components/header/header_component.py#L37-L40) |
| RN-HOME-06 | La navegación principal ofrece "Departamentos" como entrada al catálogo para comenzar una compra. | Ecommerce | `home_001.expected_nav_items`: `["Departamentos"]` en ambas | Observado (no validado): MA Departamentos, Promociones, Créditos, OUTLET; VIU agrega Regalos | [home_steps.py:L85-L104](../../tests/bdd/steps/home_steps.py#L85-L104) |
| RN-HOME-07 | El acceso a la cuenta (login) está visible en el header. | Validación | — | Igual en ambas | [test_home.py:L34-L36](../../tests/smoke/test_home.py#L34-L36) |
| RN-HOME-08 | MA puede mostrar un popup promocional en la home, que se cierra para continuar; VIU no lo muestra. | Ecommerce | Aparece solo a veces | **Sí**: solo MA | [muebles_america/home/home_page.py:L17-L21](../../pages/muebles_america/home/home_page.py#L17-L21), [common home_page.py:L59-L60](../../pages/common/pages/home_page.py#L59-L60) |
| RN-HOME-09 | El catálogo se recorre desde el menú de departamentos hasta una categoría. | Ecommerce | `guest_checkout.linea_blanca`: MA `Departamentos > Línea blanca`; VIU `Línea blanca > Estufas` | **Sí**: MA tiene 2 niveles (departamento → categoría); VIU, 3 (trigger "Departamentos" → departamento → categoría) | [MA mega_menu_component.py:L18-L51](../../pages/muebles_america/components/mega_menu/mega_menu_component.py#L18-L51), [VIU mega_menu_component.py:L24-L64](../../pages/viu/components/mega_menu/mega_menu_component.py#L24-L64) |

## Search

| ID | Regla | Tipo | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|---|
| RN-SEARCH-01 | El buscador conserva el término capturado antes de ejecutar la búsqueda. | Validación | — | Igual en ambas | [search_steps.py:L37-L44](../../tests/bdd/steps/search_steps.py#L37-L44) |
| RN-SEARCH-02 | Ejecutar la búsqueda lleva a la ruta de resultados del término capturado. | Ecommerce | Ruta `/catalogsearch/result?q=<término>`; `q` == término | Igual en ambas | [search_steps.py:L51-L62](../../tests/bdd/steps/search_steps.py#L51-L62), [search_component.py:L50-L59](../../pages/common/components/search/search_component.py#L50-L59) |
| RN-SEARCH-03 | La pantalla de resultados siempre muestra el contador "N resultados de búsqueda", haya o no coincidencias. | Ecommerce | Texto `resultados de búsqueda` | Igual en ambas | [search_steps.py:L64-L69](../../tests/bdd/steps/search_steps.py#L64-L69), [search_component.py:L39-L48](../../pages/common/components/search/search_component.py#L39-L48) |
| RN-SEARCH-04 | Un término válido devuelve al menos el mínimo de resultados esperado y muestra al menos un producto. | Validación | `search.with_results`: `min_results: 1`; término MA `"parrilla"` / VIU `"MABE00888"` | **Sí**: término distinto (VIU usa un SKU disponible, ver Notas) | [search_steps.py:L71-L74](../../tests/bdd/steps/search_steps.py#L71-L74), [search_steps.py:L97-L104](../../tests/bdd/steps/search_steps.py#L97-L104) |
| RN-SEARCH-05 | Las cards cargadas por scroll infinito coinciden con el total que declara el contador. | Ecommerce | cards cargadas == contador | Igual en ambas | [search_steps.py:L106-L114](../../tests/bdd/steps/search_steps.py#L106-L114) |
| RN-SEARCH-06 | Una card es elegible para comprar si está visible, enlaza a la PDP, tiene precio de contado > 0 y botón de agregar al carrito. Se toma la primera elegible, no por posición fija. | Validación | precio > 0 | Igual en ambas | [search_component.py:L104-L115](../../pages/common/components/search/search_component.py#L104-L115), [product_card.py:L34-L49](../../pages/common/components/product_card/product_card.py#L34-L49) |
| RN-SEARCH-07 | La card elegible abre la PDP de su propio producto. | Ecommerce | El slug del enlace de la card está en la URL de la PDP | Igual en ambas | [search_steps.py:L126-L136](../../tests/bdd/steps/search_steps.py#L126-L136) |
| RN-SEARCH-08 | Un término sin coincidencias muestra el estado vacío: contador en 0 y ningún producto en el listado. El sitio no muestra otro mensaje. | Ecommerce | `search.without_results`: término `"zzzz-producto-inexistente-qa"`, `expected_results: 0` en ambas | Igual en ambas | [search_steps.py:L88-L95](../../tests/bdd/steps/search_steps.py#L88-L95), [search_steps.py:L138-L144](../../tests/bdd/steps/search_steps.py#L138-L144) |

## PDP

| ID | Regla | Tipo | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|---|
| RN-PDP-01 | La PDP abierta corresponde a la card elegida: la URL contiene el slug de la card y el nombre coincide (sin distinguir mayúsculas ni espacios). | Validación | — | Igual en ambas | [pdp_steps.py:L41-L76](../../tests/bdd/steps/pdp_steps.py#L41-L76) |
| RN-PDP-02 | El producto tiene nombre no vacío. | Validación | — | Igual en ambas | [pdp_steps.py:L79-L82](../../tests/bdd/steps/pdp_steps.py#L79-L82) |
| RN-PDP-03 | El producto expone al menos un identificador válido: el SKU aparece en la URL y/o el product_id es numérico. Si falta uno, se documenta como "ausente". | Validación | — | Igual en ambas | [pdp_steps.py:L85-L106](../../tests/bdd/steps/pdp_steps.py#L85-L106), [pdp_component.py:L47-L49](../../pages/common/components/pdp/pdp_component.py#L47-L49) |
| RN-PDP-04 | El precio de lista es `regular_price` (o `original_price`, o `price`) y el vigente es `final_price` (o `price`). Hay precio promocional solo si el vigente es menor que el de lista. | Ecommerce | — | Igual en ambas | [pdp_component.py:L36-L53](../../pages/common/components/pdp/pdp_component.py#L36-L53) |
| RN-PDP-05 | El precio es un importe válido: unitario y efectivo > 0, efectivo ≤ unitario y promocional < unitario. | Validación | — | Igual en ambas | [pdp_steps.py:L109-L123](../../tests/bdd/steps/pdp_steps.py#L109-L123) |
| RN-PDP-06 | Regla de venta por estado: el producto se puede vender si está activo, visible en catálogo y búsqueda, en stock y con existencias. | Ecommerce | `is_in_stock` y `qty > 0` y `status == 1` y `visibility == 4` | Igual en ambas | [pdp_component.py:L63-L72](../../pages/common/components/pdp/pdp_component.py#L63-L72) |
| RN-PDP-07 | La PDP muestra una etiqueta de disponibilidad: **Disponible**, **Agotado** o **Solo queda N** (pocas piezas). Solo "Disponible" y "Solo queda N" (N ≥ 1) permiten comprar. La etiqueta prevalece sobre el estado interno, que puede marcar en stock un producto agotado. | Ecommerce | El umbral de "Solo queda N" se configura en el backend y el framework no lo valida | Igual en ambas | [pdp_steps.py:L126-L140](../../tests/bdd/steps/pdp_steps.py#L126-L140), [pdp_component.py:L88-L96](../../pages/common/components/pdp/pdp_component.py#L88-L96), [pdp_locators.py:L18-L21](../../pages/common/components/pdp/pdp_locators.py#L18-L21) |
| RN-PDP-08 | Para comprar hay stock positivo y la cantidad seleccionada es al menos 1 (sin selector visible, la cantidad es 1). | Validación | stock > 0; cantidad ≥ 1 | Igual en ambas | [pdp_steps.py:L142-L143](../../tests/bdd/steps/pdp_steps.py#L142-L143), [pdp_component.py:L59-L61](../../pages/common/components/pdp/pdp_component.py#L59-L61) |
| RN-PDP-09 | La acción de agregar al carrito está visible y habilitada. En un producto agotado no existe. | Ecommerce | — | Igual en ambas | [pdp_steps.py:L150-L154](../../tests/bdd/steps/pdp_steps.py#L150-L154), [pdp_component.py:L74-L86](../../pages/common/components/pdp/pdp_component.py#L74-L86) |
| RN-PDP-10 | Un producto configurable tiene un SKU padre y variantes hijas. El SKU padre lleva un prefijo propio de cada marca; los SKU hijos son compartidos. | Ecommerce | `products.configurable_colchon`: término `"winer"`, 4 variantes; padre MA `1COLC08920` / VIU `2COLC08920` | **Sí**: prefijo del padre (1 en MA, 2 en VIU) | [pdp_component.py:L105-L112](../../pages/common/components/pdp/pdp_component.py#L105-L112), [pdp_steps.py:L176-L186](../../tests/bdd/steps/pdp_steps.py#L176-L186), `data/<sitio>/products.yaml` |
| RN-PDP-11 | Cada variante es vendible si está en stock, con existencias y activa. La regla de visibilidad aplica solo al padre (los hijos no se exhiben solos). | Ecommerce | `is_in_stock` y `qty > 0` y `status == 1`; hijos con `visibility = 1` | Igual en ambas | [pdp_component.py:L114-L144](../../pages/common/components/pdp/pdp_component.py#L114-L144), [pdp_steps.py:L188-L213](../../tests/bdd/steps/pdp_steps.py#L188-L213) |

## Cart

| ID | Regla | Tipo | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|---|
| RN-CART-01 | Agregar al carrito se confirma con una notificación. En MA, algunos artículos muestran además una ventana de promociones. | Ecommerce | — | **Sí**: la ventana de promociones solo existe en MA. El aviso de MA enlaza al carrito; el de VIU se acepta y el carrito se abre desde el header | [MA product_page.py:L23-L52](../../pages/muebles_america/product/product_page.py#L23-L52), [VIU product_page.py:L14-L45](../../pages/viu/product/product_page.py#L14-L45), [promotions_window_component.py:L15-L29](../../pages/muebles_america/components/promotions_window/promotions_window_component.py#L15-L29) |
| RN-CART-02 | Lo que llega al carrito coincide con la PDP: un ítem con el mismo SKU, nombre, cantidad y precio efectivo. | Validación | — | Igual en ambas | [cart_steps.py:L39-L73](../../tests/bdd/steps/cart_steps.py#L39-L73) |
| RN-CART-03 | En el carrito, un precio tachado es el de lista y el precio vigente es el promocional. Sin tachado, el vigente es el de lista. | Ecommerce | — | Igual en ambas | [cart_component.py:L61-L75](../../pages/common/components/cart/cart_component.py#L61-L75) |
| RN-CART-04 | Los importes del carrito son consistentes: subtotal = Σ(precio efectivo × cantidad); total = subtotal − descuento + envío. Subtotal, descuento y total mostrados coinciden con el cálculo. | Validación | — | Igual en ambas | [cart_steps.py:L76-L102](../../tests/bdd/steps/cart_steps.py#L76-L102), [cart.py:L24-L56](../../domain/models/cart.py#L24-L56) |
| RN-CART-05 | Un ítem del carrito tiene cantidad de al menos 1. | Validación | cantidad ≥ 1 (invariante del modelo) | Igual en ambas | [cart.py:L20-L22](../../domain/models/cart.py#L20-L22) |
| RN-CART-06 | Desde el carrito se continúa al checkout, que ofrece "Continuar como invitado". | Ecommerce | — | Igual en ambas | [cart_steps.py:L105-L111](../../tests/bdd/steps/cart_steps.py#L105-L111), [checkout_component.py:L30-L36](../../pages/common/components/checkout/checkout_component.py#L30-L36) |

## Checkout / Customer

| ID | Regla | Tipo | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|---|
| RN-CHECKOUT-01 | Continuar como invitado lleva al checkout de una página (OneStepCheckout). | Ecommerce | Patrón de URL por marca y ambiente en `config/sites.yaml` (`checkout_url_pattern`) | Igual en ambas | [checkout_component.py:L38-L47](../../pages/common/components/checkout/checkout_component.py#L38-L47), [MA checkout_page.py:L15-L31](../../pages/muebles_america/checkout/checkout_page.py#L15-L31) |
| RN-CHECKOUT-02 | Al entrar, la etapa activa es "Entrega" y son obligatorios correo, nombre, apellido, teléfono, calle, número exterior y código postal. | Ecommerce | Campos `username`, `firstname`, `lastname`, `telephone`, `street[0]`, `custom_attributes[address_number]`, `postcode` | Igual en ambas | [checkout_steps.py:L45-L68](../../tests/bdd/steps/checkout_steps.py#L45-L68) |
| RN-CHECKOUT-03 | El checkout avanza por etapas: Entrega → Forma de pago → Resumen. "Forma de pago" se habilita solo después de aceptar los datos del comprador y la dirección. | Ecommerce | — | Igual en ambas | [checkout_component.py:L17-L21](../../pages/common/components/checkout/checkout_component.py#L17-L21), [checkout_component.py:L65-L78](../../pages/common/components/checkout/checkout_component.py#L65-L78) |
| RN-CHECKOUT-04 | Los datos del comprador quedan aceptados: correo, nombre y apellido iguales a los capturados, sin errores de validación y con el código postal guardado. | Validación | Identidad desde `.env` (`MAVI_GUEST_<CODE>_*`) | Igual en ambas | [checkout_steps.py:L79-L117](../../tests/bdd/steps/checkout_steps.py#L79-L117) |
| RN-CHECKOUT-05 | El checkout muestra un precio del pedido mayor a cero (smoke de venta de contado). | Validación | precio > 0 | **Sí**: MA lee el precio destacado y VIU el total del resumen (mismo criterio) | [sale_cash_steps.py:L40-L45](../../tests/bdd/steps/sale_cash_steps.py#L40-L45), [MA checkout_page.py:L34-L44](../../pages/muebles_america/checkout/checkout_page.py#L34-L44), [VIU checkout_page.py:L12-L14](../../pages/viu/checkout/checkout_page.py#L12-L14) |

## Address

| ID | Regla | Tipo | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|---|
| RN-ADDRESS-01 | Capturar el código postal autocompleta colonia, ciudad y estado (al salir del campo). | Ecommerce | `addresses.guadalajara`: CP `44100` → Americana / Guadalajara / Jalisco, en ambas | Igual en ambas | [address_component.py:L29-L68](../../pages/common/components/checkout/address_component.py#L29-L68), [address_steps.py:L14-L28](../../tests/bdd/steps/address_steps.py#L14-L28) |
| RN-ADDRESS-02 | El sitio normaliza a mayúsculas los campos autocompletados. La comparación no distingue mayúsculas. | Ecommerce | — | Igual en ambas | [address_steps.py:L19-L28](../../tests/bdd/steps/address_steps.py#L19-L28) |

## Shipping

| ID | Regla | Tipo | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|---|
| RN-SHIPPING-01 | Hay dos modos de entrega: a domicilio y retiro en sucursal. Solo uno queda activo. | Ecommerce | `a_domicilio`, `sucursal`; `checkout.guest.shipping_method: "a_domicilio"` en ambas | Igual en ambas | [shipping_component.py:L21-L53](../../pages/common/components/checkout/shipping_component.py#L21-L53) |
| RN-SHIPPING-02 | El costo de envío queda disponible una vez calculado: "Gratis" (= 0) o un importe ≥ 0. | Validación | "Aún no calculado" = todavía sin costo | Igual en ambas | [shipping_component.py:L134-L162](../../pages/common/components/checkout/shipping_component.py#L134-L162), [checkout_steps.py:L120-L147](../../tests/bdd/steps/checkout_steps.py#L120-L147) |
| RN-SHIPPING-03 | El retiro en sucursal requiere elegir estado y sucursal ("Entregar aquí") y capturar el contacto de quien recoge: nombre, apellido paterno y teléfono (apellido materno opcional). | Ecommerce | `checkout.guest.store_state: "Jalisco"` en ambas; se elige la primera sucursal | Igual en ambas | [shipping_component.py:L56-L124](../../pages/common/components/checkout/shipping_component.py#L56-L124), [shipping_steps.py:L20-L59](../../tests/bdd/steps/shipping_steps.py#L20-L59) |

## Payment

| ID | Regla | Tipo | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|---|
| RN-PAYMENT-01 | Métodos de pago: tarjeta de crédito/débito de contado, efectivo en tiendas, transferencia, PayPal y crédito de la marca. El crédito de la marca **no** es contado. | Ecommerce | `openpay_cards`, `openpay_stores`, `banktransfer`, `paypal_express`, `omnipro_pago_credito` | **Sí**: el crédito de la marca se llama "Mi crédito VIU" en VIU | [MA payment.yaml:L10-L43](../../data/muebles_america/payment.yaml#L10-L43), [VIU payment.yaml:L10-L43](../../data/viu/payment.yaml#L10-L43) |
| RN-PAYMENT-02 | Un método de pago solo se puede elegir si está presente y habilitado para el carrito; el sitio lo habilita de forma asíncrona. | Ecommerce | — | Igual en ambas | [payment_component.py:L44-L75](../../pages/common/components/payment/payment_component.py#L44-L75) |
| RN-PAYMENT-03 | Pago de contado con tarjeta: queda seleccionado el método del dataset, sin errores de validación, y "Finalizar compra" queda habilitado. Fuera de ORDER/E2E, el framework nunca hace clic ahí. | Validación | `checkout.guest.payment_method: "openpay_cards"` | Igual en ambas | [payment_steps.py:L49-L79](../../tests/bdd/steps/payment_steps.py#L49-L79), [payment_component.py:L190-L217](../../pages/common/components/payment/payment_component.py#L190-L217) |
| RN-PAYMENT-04 | PayPal saca al comprador del dominio del ecommerce (ventana o redirección del proveedor). | Ecommerce | `paypal_express` | Igual en ambas | [payment_locators.py:L33-L34](../../pages/common/components/payment/payment_locators.py#L33-L34), [payment_component.py:L94-L96](../../pages/common/components/payment/payment_component.py#L94-L96) |

## Order

| ID | Regla | Tipo | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|---|
| RN-ORDER-01 | Una compra es exitosa solo si se llega a la página de éxito, se ve la confirmación y hay folio legible. | Ecommerce | URL `…/success/`, contenedor `.checkout-success` | Igual en ambas | [order_component.py:L26-L56](../../pages/common/components/order/order_component.py#L26-L56) |
| RN-ORDER-02 | El folio es numérico (al menos 6 dígitos después de "pedido"/"orden") y el mensaje de confirmación menciona "pedido" o "compra". | Validación | p.ej. "¡Gracias por tu compra! … Tu N° de pedido es: # NNNNNNNNNN" | Igual en ambas | [order_component.py:L16-L18](../../pages/common/components/order/order_component.py#L16-L18), [order_steps.py:L29-L43](../../tests/bdd/steps/order_steps.py#L29-L43) |
| RN-ORDER-03 | Si el pago se rechaza, el checkout muestra el mensaje de declinación y no hay orden. | Ecommerce | — | Igual en ambas | [order_component.py:L32-L37](../../pages/common/components/order/order_component.py#L32-L37), [order_component.py:L77-L83](../../pages/common/components/order/order_component.py#L77-L83) |
| RN-ORDER-04 | La orden es consistente con el flujo: SKU del carrito = PDP; subtotal del resumen = carrito; envío del resumen = envío elegido; total = subtotal − descuento + envío; método de pago = el elegido. | Validación | — | Igual en ambas | [order_steps.py:L65-L95](../../tests/bdd/steps/order_steps.py#L65-L95) |

## Flujo de venta de contado

| ID | Regla | Tipo | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|---|
| RN-VENTA-01 | La venta de contado se detiene con un error de precondición de negocio si: no hay card elegible; la PDP no está disponible o no deja agregar al carrito; el carrito queda vacío; no aparece "Continuar como invitado"; el formulario tiene errores; el método de pago no es seleccionable; o el pago tiene errores. | Validación | `checkout.guest.search_term`: MA `"estufa"` / VIU `"MIDE00067"` | **Sí**: término distinto | [sale_cash_workflow.py:L146-L235](../../workflows/common/sale_cash_workflow.py#L146-L235) |
| RN-VENTA-02 | Integridad comercial de extremo a extremo: SKU y precio efectivo del carrito = PDP, cantidad ≥ 1, subtotal y envío del resumen consistentes, total = subtotal − descuento + envío y método de pago = el solicitado. | Validación | — | Igual en ambas | [e2e_steps.py:L84-L115](../../tests/bdd/steps/e2e_steps.py#L84-L115) |

## Dominio (transversal)

| ID | Regla | Tipo | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|---|
| RN-DOMINIO-01 | Los importes se manejan con moneda explícita y 2 decimales (redondeo a la mitad hacia arriba), nunca con decimales flotantes. No se operan monedas distintas entre sí. | Validación | Moneda por defecto `MXN` | Igual en ambas | [money.py:L8-L38](../../domain/money/money.py#L8-L38) |
| RN-DOMINIO-02 | El precio efectivo de un producto es el promocional si existe; si no, el unitario. | Validación | — | Igual en ambas | [product.py:L17-L19](../../domain/models/product.py#L17-L19) |

## Notas

- **Límite de efectivo $30,000 MXN (sin automatizar):** `payment.yaml` (`cash.max_amount_mxn: 30000`) y el docstring de [payment_component.py:L47-L48](../../pages/common/components/payment/payment_component.py#L47-L48) dicen que el efectivo (`openpay_stores`) no se puede elegir con un carrito > $30,000. El escenario `PAY_002` está `@pending` y no tiene steps: **ninguna prueba lo verifica**.
- **Meses sin intereses (sin automatizar):** la tarjeta MSI de sandbox (`card_msi`) está en `payment.yaml`, pero `PAY_003` está `@pending`, sin steps.
- **Disponibilidad en el flujo de venta:** `SaleCashWorkflow` decide con la regla de estado (RN-PDP-06) y no con la etiqueta (RN-PDP-07). Un producto marcado "Agotado" con estado "en stock" solo lo detendría el botón ausente (RN-PDP-09).
- **Hallazgo en stage (VIU):** `WHIR00686` tiene estado "en stock, 6 piezas" pero la PDP lo muestra "Agotado" y sin botón de carrito. Por eso VIU busca `MABE00888` (RN-SEARCH-04).
- El estimado de entrega ("Entrega entre el …") se lee y se adjunta al reporte, pero no se valida.

## Historial

| Fecha | Commit | Cambios |
|---|---|---|
| 2026-11-26 | `f331422` | Versión inicial: 56 reglas en 11 módulos |
