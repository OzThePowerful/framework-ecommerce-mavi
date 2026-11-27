# Reglas de negocio de las páginas — Framework Ecommerce MAVI

Reglas de negocio del ecommerce (cómo se comporta el sitio) en cada
página del flujo de compra, extraídas del código. No incluye los
criterios de validación del framework ni reglas de arquitectura o
técnicas (ver `docs/standards/`).

- **Generado:** 2026-11-26 sobre la rama `steps-ma` (`01a0a6c`)
- **Marcas:** Muebles América (MA), VIU

## Resumen

| Módulo | Reglas | Con diferencia por marca |
|---|---|---|
| Home | 5 | 3 |
| Search | 5 | 0 |
| PDP | 6 | 1 |
| Cart | 3 | 1 |
| Checkout / Customer | 3 | 0 |
| Address | 2 | 0 |
| Shipping | 2 | 0 |
| Payment | 3 | 1 |
| Order | 2 | 0 |
| **Total** | **31** | **6** |

## Home

| ID | Regla | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|
| RN-HOME-01 | La home responde correctamente al abrir la URL configurada del sitio. | Status HTTP 200 ≤ status < 400 | Igual en ambas | [home_steps.py:L39-L45](../../tests/bdd/steps/home_steps.py#L39-L45) |
| RN-HOME-03 | La home se identifica con la marca del sitio: logo visible y título de la página con el nombre de la marca. | `home_001.expected_title_fragment`: MA `"Muebles América"` / VIU `"VIU"` | **Sí**: logo MA = imagen (`muebles-america-logo.png`); VIU = SVG. Fragmento de título distinto | [home_steps.py:L57-L66](../../tests/bdd/steps/home_steps.py#L57-L66), [header_locators.py:L19](../../pages/common/components/header/header_locators.py#L19), `data/<sitio>/home.yaml` |
| RN-HOME-06 | La navegación principal ofrece "Departamentos" como entrada al catálogo para comenzar una compra. | `home_001.expected_nav_items`: `["Departamentos"]` en ambas | Observado (no validado): MA Departamentos, Promociones, Créditos, OUTLET; VIU agrega Regalos | [home_steps.py:L85-L104](../../tests/bdd/steps/home_steps.py#L85-L104) |
| RN-HOME-08 | MA puede mostrar un popup promocional en la home, que se cierra para continuar; VIU no lo muestra. | Aparece solo a veces | **Sí**: solo MA | [muebles_america/home/home_page.py:L17-L21](../../pages/muebles_america/home/home_page.py#L17-L21), [common home_page.py:L59-L60](../../pages/common/pages/home_page.py#L59-L60) |
| RN-HOME-09 | El catálogo se recorre desde el menú de departamentos hasta una categoría. | `guest_checkout.linea_blanca`: MA `Departamentos > Línea blanca`; VIU `Línea blanca > Estufas` | **Sí**: MA tiene 2 niveles (departamento → categoría); VIU, 3 (trigger "Departamentos" → departamento → categoría) | [MA mega_menu_component.py:L18-L51](../../pages/muebles_america/components/mega_menu/mega_menu_component.py#L18-L51), [VIU mega_menu_component.py:L24-L64](../../pages/viu/components/mega_menu/mega_menu_component.py#L24-L64) |

## Search

| ID | Regla | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|
| RN-SEARCH-02 | Ejecutar la búsqueda lleva a la ruta de resultados del término capturado. | Ruta `/catalogsearch/result?q=<término>`; `q` == término | Igual en ambas | [search_steps.py:L51-L62](../../tests/bdd/steps/search_steps.py#L51-L62), [search_component.py:L50-L59](../../pages/common/components/search/search_component.py#L50-L59) |
| RN-SEARCH-03 | La pantalla de resultados siempre muestra el contador "N resultados de búsqueda", haya o no coincidencias. | Texto `resultados de búsqueda` | Igual en ambas | [search_steps.py:L64-L69](../../tests/bdd/steps/search_steps.py#L64-L69), [search_component.py:L39-L48](../../pages/common/components/search/search_component.py#L39-L48) |
| RN-SEARCH-05 | Las cards cargadas por scroll infinito coinciden con el total que declara el contador. | cards cargadas == contador | Igual en ambas | [search_steps.py:L106-L114](../../tests/bdd/steps/search_steps.py#L106-L114) |
| RN-SEARCH-07 | La card elegible abre la PDP de su propio producto. | El slug del enlace de la card está en la URL de la PDP | Igual en ambas | [search_steps.py:L126-L136](../../tests/bdd/steps/search_steps.py#L126-L136) |
| RN-SEARCH-08 | Un término sin coincidencias muestra el estado vacío: contador en 0 y ningún producto en el listado. El sitio no muestra otro mensaje. | `search.without_results`: término `"zzzz-producto-inexistente-qa"`, `expected_results: 0` en ambas | Igual en ambas | [search_steps.py:L88-L95](../../tests/bdd/steps/search_steps.py#L88-L95), [search_steps.py:L138-L144](../../tests/bdd/steps/search_steps.py#L138-L144) |

## PDP

| ID | Regla | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|
| RN-PDP-04 | El precio de lista es `regular_price` (o `original_price`, o `price`) y el vigente es `final_price` (o `price`). Hay precio promocional solo si el vigente es menor que el de lista. | — | Igual en ambas | [pdp_component.py:L36-L53](../../pages/common/components/pdp/pdp_component.py#L36-L53) |
| RN-PDP-06 | Regla de venta por estado: el producto se puede vender si está activo, visible en catálogo y búsqueda, en stock y con existencias. | `is_in_stock` y `qty > 0` y `status == 1` y `visibility == 4` | Igual en ambas | [pdp_component.py:L63-L72](../../pages/common/components/pdp/pdp_component.py#L63-L72) |
| RN-PDP-07 | La PDP muestra una etiqueta de disponibilidad: **Disponible**, **Agotado** o **Solo queda N** (pocas piezas). Solo "Disponible" y "Solo queda N" (N ≥ 1) permiten comprar. La etiqueta prevalece sobre el estado interno, que puede marcar en stock un producto agotado. | El umbral de "Solo queda N" se configura en el backend y el framework no lo valida | Igual en ambas | [pdp_steps.py:L126-L140](../../tests/bdd/steps/pdp_steps.py#L126-L140), [pdp_component.py:L88-L96](../../pages/common/components/pdp/pdp_component.py#L88-L96), [pdp_locators.py:L18-L21](../../pages/common/components/pdp/pdp_locators.py#L18-L21) |
| RN-PDP-09 | La acción de agregar al carrito está visible y habilitada. En un producto agotado no existe. | — | Igual en ambas | [pdp_steps.py:L150-L154](../../tests/bdd/steps/pdp_steps.py#L150-L154), [pdp_component.py:L74-L86](../../pages/common/components/pdp/pdp_component.py#L74-L86) |
| RN-PDP-10 | Un producto configurable tiene un SKU padre y variantes hijas. El SKU padre lleva un prefijo propio de cada marca; los SKU hijos son compartidos. | `products.configurable_colchon`: término `"winer"`, 4 variantes; padre MA `1COLC08920` / VIU `2COLC08920` | **Sí**: prefijo del padre (1 en MA, 2 en VIU) | [pdp_component.py:L105-L112](../../pages/common/components/pdp/pdp_component.py#L105-L112), [pdp_steps.py:L176-L186](../../tests/bdd/steps/pdp_steps.py#L176-L186), `data/<sitio>/products.yaml` |
| RN-PDP-11 | Cada variante es vendible si está en stock, con existencias y activa. La regla de visibilidad aplica solo al padre (los hijos no se exhiben solos). | `is_in_stock` y `qty > 0` y `status == 1`; hijos con `visibility = 1` | Igual en ambas | [pdp_component.py:L114-L144](../../pages/common/components/pdp/pdp_component.py#L114-L144), [pdp_steps.py:L188-L213](../../tests/bdd/steps/pdp_steps.py#L188-L213) |

## Cart

| ID | Regla | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|
| RN-CART-01 | Agregar al carrito se confirma con una notificación. En MA, algunos artículos muestran además una ventana de promociones. | — | **Sí**: la ventana de promociones solo existe en MA. El aviso de MA enlaza al carrito; el de VIU se acepta y el carrito se abre desde el header | [MA product_page.py:L23-L52](../../pages/muebles_america/product/product_page.py#L23-L52), [VIU product_page.py:L14-L45](../../pages/viu/product/product_page.py#L14-L45), [promotions_window_component.py:L15-L29](../../pages/muebles_america/components/promotions_window/promotions_window_component.py#L15-L29) |
| RN-CART-03 | En el carrito, un precio tachado es el de lista y el precio vigente es el promocional. Sin tachado, el vigente es el de lista. | — | Igual en ambas | [cart_component.py:L61-L75](../../pages/common/components/cart/cart_component.py#L61-L75) |
| RN-CART-06 | Desde el carrito se continúa al checkout, que ofrece "Continuar como invitado". | — | Igual en ambas | [cart_steps.py:L105-L111](../../tests/bdd/steps/cart_steps.py#L105-L111), [checkout_component.py:L30-L36](../../pages/common/components/checkout/checkout_component.py#L30-L36) |

## Checkout / Customer

| ID | Regla | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|
| RN-CHECKOUT-01 | Continuar como invitado lleva al checkout de una página (OneStepCheckout). | Patrón de URL por marca y ambiente en `config/sites.yaml` (`checkout_url_pattern`) | Igual en ambas | [checkout_component.py:L38-L47](../../pages/common/components/checkout/checkout_component.py#L38-L47), [MA checkout_page.py:L15-L31](../../pages/muebles_america/checkout/checkout_page.py#L15-L31) |
| RN-CHECKOUT-02 | Al entrar, la etapa activa es "Entrega" y son obligatorios correo, nombre, apellido, teléfono, calle, número exterior y código postal. | Campos `username`, `firstname`, `lastname`, `telephone`, `street[0]`, `custom_attributes[address_number]`, `postcode` | Igual en ambas | [checkout_steps.py:L45-L68](../../tests/bdd/steps/checkout_steps.py#L45-L68) |
| RN-CHECKOUT-03 | El checkout avanza por etapas: Entrega → Forma de pago → Resumen. "Forma de pago" se habilita solo después de aceptar los datos del comprador y la dirección. | — | Igual en ambas | [checkout_component.py:L17-L21](../../pages/common/components/checkout/checkout_component.py#L17-L21), [checkout_component.py:L65-L78](../../pages/common/components/checkout/checkout_component.py#L65-L78) |

## Address

| ID | Regla | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|
| RN-ADDRESS-01 | Capturar el código postal autocompleta colonia, ciudad y estado (al salir del campo). | `addresses.guadalajara`: CP `44100` → Americana / Guadalajara / Jalisco, en ambas | Igual en ambas | [address_component.py:L29-L68](../../pages/common/components/checkout/address_component.py#L29-L68), [address_steps.py:L14-L28](../../tests/bdd/steps/address_steps.py#L14-L28) |
| RN-ADDRESS-02 | El sitio normaliza a mayúsculas los campos autocompletados. La comparación no distingue mayúsculas. | — | Igual en ambas | [address_steps.py:L19-L28](../../tests/bdd/steps/address_steps.py#L19-L28) |

## Shipping

| ID | Regla | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|
| RN-SHIPPING-01 | Hay dos modos de entrega: a domicilio y retiro en sucursal. Solo uno queda activo. | `a_domicilio`, `sucursal`; `checkout.guest.shipping_method: "a_domicilio"` en ambas | Igual en ambas | [shipping_component.py:L21-L53](../../pages/common/components/checkout/shipping_component.py#L21-L53) |
| RN-SHIPPING-03 | El retiro en sucursal requiere elegir estado y sucursal ("Entregar aquí") y capturar el contacto de quien recoge: nombre, apellido paterno y teléfono (apellido materno opcional). | `checkout.guest.store_state: "Jalisco"` en ambas; se elige la primera sucursal | Igual en ambas | [shipping_component.py:L56-L124](../../pages/common/components/checkout/shipping_component.py#L56-L124), [shipping_steps.py:L20-L59](../../tests/bdd/steps/shipping_steps.py#L20-L59) |

## Payment

| ID | Regla | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|
| RN-PAYMENT-01 | Métodos de pago: tarjeta de crédito/débito de contado, efectivo en tiendas, transferencia, PayPal y crédito de la marca. El crédito de la marca **no** es contado. | `openpay_cards`, `openpay_stores`, `banktransfer`, `paypal_express`, `omnipro_pago_credito` | **Sí**: el crédito de la marca se llama "Mi crédito VIU" en VIU | [MA payment.yaml:L10-L43](../../data/muebles_america/payment.yaml#L10-L43), [VIU payment.yaml:L10-L43](../../data/viu/payment.yaml#L10-L43) |
| RN-PAYMENT-02 | Un método de pago solo se puede elegir si está presente y habilitado para el carrito; el sitio lo habilita de forma asíncrona. | — | Igual en ambas | [payment_component.py:L44-L75](../../pages/common/components/payment/payment_component.py#L44-L75) |
| RN-PAYMENT-04 | PayPal saca al comprador del dominio del ecommerce (ventana o redirección del proveedor). | `paypal_express` | Igual en ambas | [payment_locators.py:L33-L34](../../pages/common/components/payment/payment_locators.py#L33-L34), [payment_component.py:L94-L96](../../pages/common/components/payment/payment_component.py#L94-L96) |

## Order

| ID | Regla | Valores / datos | Diferencias por marca | Fuente |
|---|---|---|---|---|
| RN-ORDER-01 | Una compra es exitosa solo si se llega a la página de éxito, se ve la confirmación y hay folio legible. | URL `…/success/`, contenedor `.checkout-success` | Igual en ambas | [order_component.py:L26-L56](../../pages/common/components/order/order_component.py#L26-L56) |
| RN-ORDER-03 | Si el pago se rechaza, el checkout muestra el mensaje de declinación y no hay orden. | — | Igual en ambas | [order_component.py:L32-L37](../../pages/common/components/order/order_component.py#L32-L37), [order_component.py:L77-L83](../../pages/common/components/order/order_component.py#L77-L83) |

## Notas

- **Límite de efectivo $30,000 MXN (sin automatizar):** `payment.yaml` (`cash.max_amount_mxn: 30000`) y el docstring de [payment_component.py:L47-L48](../../pages/common/components/payment/payment_component.py#L47-L48) dicen que el efectivo (`openpay_stores`) no se puede elegir con un carrito > $30,000. El escenario `PAY_002` está `@pending` y no tiene steps: **ninguna prueba lo verifica**.
- **Meses sin intereses (sin automatizar):** la tarjeta MSI de sandbox (`card_msi`) está en `payment.yaml`, pero `PAY_003` está `@pending`, sin steps.
- **Disponibilidad en el flujo de venta:** el flujo de venta de contado del framework decide con la regla de estado (RN-PDP-06) y no con la etiqueta (RN-PDP-07). Un producto marcado "Agotado" con estado "en stock" solo lo detendría el botón ausente (RN-PDP-09).
- **Hallazgo en stage (VIU):** `WHIR00686` tiene estado "en stock, 6 piezas" pero la PDP lo muestra "Agotado" y sin botón de carrito. Por eso el término de búsqueda de VIU es `MABE00888` (`data/viu/search.yaml`).
- El estimado de entrega ("Entrega entre el …") se lee y se adjunta al reporte, pero no se valida.

## Historial

| Fecha | Commit | Cambios |
|---|---|---|
| 2026-11-26 | `f331422` | Versión inicial: 56 reglas en 11 módulos |
| 2026-11-26 | `01a0a6c` | Alcance reducido a reglas del ecommerce: 25 criterios de validación del framework retirados (RN-HOME-02, 04, 05, 07; RN-SEARCH-01, 04, 06; RN-PDP-01, 02, 03, 05, 08; RN-CART-02, 04, 05; RN-CHECKOUT-04, 05; RN-SHIPPING-02; RN-PAYMENT-03; RN-ORDER-02, 04; RN-VENTA-01, 02; RN-DOMINIO-01, 02). Quedan 31 reglas en 9 módulos; los IDs vigentes no cambian |
