# Matriz de estrategia de locators — Muebles América y VIU

> **EC-SP01-008.** Levantamiento técnico del DOM real de ambos ecommerce en
> ambiente **stage**, ejecutado con Playwright sobre el DOM en vivo.
> Ambos sitios comparten el mismo stack (Magento + OneStepCheckout + frontend
> Vue), por lo que gran parte del DOM es estructuralmente idéntico; las
> diferencias por marca se concentran en URLs, menú y datasets.

## Jerarquía de prioridad aplicada

1. `data-testid`
2. `role` + accessible name
3. `label`
4. `aria-label`
5. `id`/`name` estable
6. atributos semánticos (JSON-LD, `type`, `itemprop`)
7. CSS estable (último recurso, documentado como riesgo)

## Antipatrones prohibidos

`data-v-*` (Vue scoped, cambia por build) · XPath absoluto · hashes generados
(`VI…`, `IW…`, `ko_unique_*`) · `nth()` arbitrario · `first()` para ocultar
ambigüedad · texto promocional volátil.

## Leyenda de estabilidad

- **Alta**: verificado en interacción real o atributo contractual (`data-testid`, `name` de formulario).
- **Media**: verificado en DOM pero depende de clase/estructura del tema.
- **Baja**: funciona hoy, documentado como frágil con alternativa propuesta.
- **Pendiente**: pantalla no alcanzable sin compra real; no se inventan selectores.

---

## Matriz

### Home

| Marca | Pantalla | Elemento | Responsabilidad | Selector principal | Selector alternativo | Estabilidad | Common / específico | Riesgo | Observación |
|---|---|---|---|---|---|---|---|---|---|
| Ambas | Home | Botón cerrar cookie | Aceptar/cerrar banner de cookies | `[data-testid='closeCookieButton']` | `role=button[name='Aceptar']` (pendiente nombre exacto) | Alta | Common | Bajo | Verificado en ambos sitios; único data-testid del banner |
| Ambas | Home | Header raíz | Scope de componentes del header | `header` | `role=banner` | Alta | Common | Bajo | Verificado (2 coincidencias: desktop/mobile → usar scope visible) |
| Ambas | Home | Nav principal | Scope del mega-menú | `header nav` | `role=navigation` | Alta | Common | Bajo | 1 nav por header |
| Ambas | Home | Logo | Marca / regreso a home | `header [class*='logo']` | `header a[href='/']` | Media | Common | Medio | Clase semántica del tema; sin data-testid |
| Ambas | Home | Acceso cuenta (desktop) | Abrir login | `header:visible a[href='/login']` | `role=link[name='Cuenta']` | Alta | Common | Bajo | Verificado en ambos; el `data-testid='accountButton'` pertenece al drawer móvil oculto |
| Ambas | Home | Botón minicart (desktop) | Abrir minicart | `header:visible button[aria-label='Abrir minicart']` | `role=button[name='Abrir minicart']` | Alta | Common | Bajo | Verificado en ambos (EC-SP01-009); `data-testid='openMicrocart'` vive en el drawer móvil oculto |
| Ambas | Home | Botón menú móvil | Abrir sidebar | `[data-testid='menuButton']` | — | Media | Common | Medio | Drawer móvil: oculto en viewport desktop; usar solo con viewport móvil |
| Ambas | Home | Botón departamentos | Abrir menú de categorías | `role=button[name='Departamentos']` | `header:visible button:has-text('Departamentos')` | Alta | Common | Bajo | Verificado en ambos (el botón existe también en MA desktop) |
| Ambas | Home | Sidebar | Contenedor menú lateral | `[data-testid='sidebar']` | — | Media | Common | Medio | 4 coincidencias (estados/duplicados) → scope + `:visible` |
| MA | Home | Cerrar promo overlay | Cerrar ventana promocional de entrada | `button[title='Close'] svg` | `role=button[name='Close']` | Media | Específico | Medio | Verificado en flujo E2E; aparición condicional |

### Search

| Marca | Pantalla | Elemento | Responsabilidad | Selector principal | Selector alternativo | Estabilidad | Common / específico | Riesgo | Observación |
|---|---|---|---|---|---|---|---|---|---|
| Ambas | Header | Input de búsqueda | Capturar término | `input[type='search'][aria-label='Buscar']:visible` | `input.input-search__input:visible` | Alta | Common | Bajo | 2 instancias (desktop/mobile); la `:visible` es la del viewport. Sin `name`/`id` → el `type`+`aria-label` es la estrategia (dato confirmado por el usuario: `data-v-*` presente, ignorado) |
| Ambas | Header | Botón/envío de búsqueda | Ejecutar búsqueda | `button[data-testid='subscribeSubmit']:visible` | `input[type='search']:visible` + `press('Enter')` | Alta | Common | Bajo | Verificado en ambos (EC-SP01-009): es el botón lupa junto al input; el data-testid dice "subscribe" pero es el submit del buscador |

### Search Results

| Marca | Pantalla | Elemento | Responsabilidad | Selector principal | Selector alternativo | Estabilidad | Common / específico | Riesgo | Observación |
|---|---|---|---|---|---|---|---|---|---|
| Ambas | Results | Grid de productos | Scope de resultados | `div.product-tile` | — | Alta | Common | Bajo | Verificado: VIU categoría → 50 tiles; MA categoría → verificado vía workflow |
| Ambas | Results | Link de producto | Navegar a PDP | `div.product-tile a[href*='.html']` | `role=link` dentro del tile | Media | Common | Medio | Href semántico `/nombre-producto.html` |

### Product Card

| Marca | Pantalla | Elemento | Responsabilidad | Selector principal | Selector alternativo | Estabilidad | Common / específico | Riesgo | Observación |
|---|---|---|---|---|---|---|---|---|---|
| Ambas | Product Card | Contenedor | Unidad de card | `div.product-tile` | — | Alta | Common | Bajo | Mismo selector que el tile del grid |
| Ambas | Product Card | Nombre | Leer nombre | `div.product-tile a[href*='.html']` | — | Media | Common | Medio | Texto del link = nombre; sin data-testid |
| Ambas | Product Card | Precio | Leer precio | `div.product-tile [class*='price']` | — | Media | Common | Medio | Verificar: puede haber precio regular + semanal → scope adicional requerido |

### PDP

| Marca | Pantalla | Elemento | Responsabilidad | Selector principal | Selector alternativo | Estabilidad | Common / específico | Riesgo | Observación |
|---|---|---|---|---|---|---|---|---|---|
| Ambas | PDP | Nombre del producto | Leer título | `script[type='application/ld+json']` → JSON `@type=Product` → `name` | — | Alta | Common | Bajo | **Sin `h1` en el DOM** (SPA Vue); JSON-LD verificado en ambos con nombre exacto |
| Ambas | PDP | Precio | Leer precio | `script[type='application/ld+json']` → `offers.price` | `[class*='price']` con scope de info de producto | Media | Common | Medio | El `[class*='price']` visible es precio semanal de financiamiento (`viu-weekly-price`); el precio principal no tiene clase semántica estable → JSON-LD es la fuente confiable |
| Ambas | PDP | Botón agregar al carrito | Añadir producto | `button.add-to-cart:visible` | `role=button` con `has-text` "carrito" dentro de scope PDP | Alta | Common | Bajo | 2 instancias en DOM (una oculta: layout desktop/sticky); `:visible` discrimina. Verificado en ambos |
| Ambas | PDP | Botón comprar ahora | Compra directa | `role=button[name='Comprar ahora']` | `button:has-text('Comprar ahora'):visible` | Media | Common | Medio | Verificado texto en VIU; mismo patrón MA por stack compartido |
| Ambas | PDP | Notificación "añadido" | Confirmar add-to-cart | `div.notifications.fixed span` | `role=status` / `role=alert` | Media | Common | Medio | Verificado MA en E2E; VIU observado idéntico |
| Ambas | PDP | Botón ir a carrito (notificación) | Navegar al carrito | `div.notifications button:visible` con scope de la notificación | `button.fw-600.fs-15.cl-white:visible` (actual MA) | Baja | Common | Alto | **Frágil**: utilidades CSS genéricas. Alternativa propuesta: scope en `div.notifications` + role button. Requiere refactor con verificación |

### MiniCart

| Marca | Pantalla | Elemento | Responsabilidad | Selector principal | Selector alternativo | Estabilidad | Common / específico | Riesgo | Observación |
|---|---|---|---|---|---|---|---|---|---|
| Ambas | MiniCart | Abrir minicart (desktop) | Desplegar | `header:visible button[aria-label='Abrir minicart']` | `[data-testid='openMicrocart']` (drawer móvil) | Alta | Common | Bajo | Verificado en ambos (EC-SP01-009) |
| VIU | MiniCart | Contador | Leer items | `.minicart-count` | — | Media | Common | Medio | Verificado VIU; clase semántica del tema |
| VIU | MiniCart | Item de producto | Scope por producto | `.product-minicart` | — | Media | Common | Medio | Verificado VIU |
| VIU | MiniCart | Eliminar item | Quitar producto | `.mini-cart-delete-product` | `role=button[name='Eliminar']` | Media | Common | Medio | Verificado VIU |
| Ambas | MiniCart | CTA ir al carrito | Navegar al carrito | `a[href*='checkout/cart']:has-text('carrito')` ("Ir al carrito de compras") | `role=link[name='Ir al carrito de compras']` | Alta | Common | Bajo | Verificado en ambos → `/checkout/cart` (EC-SP01-012). El botón `fw-600.fs-15.cl-white` de la notificación MA abre el mismo drawer |

### Cart

| Marca | Pantalla | Elemento | Responsabilidad | Selector principal | Selector alternativo | Estabilidad | Common / específico | Riesgo | Observación |
|---|---|---|---|---|---|---|---|---|---|
| Ambas | Cart | URL del carrito | Navegación | `base_url + /checkout/cart` | — | Alta | Common | Bajo | Verificado en ambos vía minicart (EC-SP01-012). Corregido: `/carrito` no existe (hallazgo de probe defectuoso) |
| Ambas | Cart | Contenedor de ítems | Scope del listado | `.shopping-cart-products` | — | Alta | Common | Bajo | Verificado en ambos (EC-SP01-012) |
| Ambas | Cart | Item de producto | Scope por producto | `.shopping-cart-products .shopping-tile` | — | Alta | Common | Bajo | Verificado en ambos; reemplaza `.product-item-details` (no existe en el DOM Vue real) |
| Ambas | Cart | SKU del ítem | Identificar producto | `.shopping-tile .sku` (texto `SKU#: XXX`) | — | Alta | Common | Bajo | Verificado; el texto lleva prefijo `SKU#:` que se recorta |
| Ambas | Cart | Nombre del ítem | Identificar producto | `.shopping-tile .name` | — | Alta | Common | Bajo | Verificado; puede duplicarse (layout móvil/desktop) → `.first` |
| Ambas | Cart | Cantidad | Leer qty | `.shopping-tile .product-quantity.counter` (texto) | — | Media | Common | Medio | Verificado; es un contador, no input. `span.sum` es el botón "+", no el valor |
| Ambas | Cart | Precio vigente / tachado | Leer importes | `.shopping-tile span.price.cl-accent` / `span.price.line-through` | — | Alta | Common | Bajo | Verificado; ambos pueden duplicarse por layout → `.first` |
| Ambas | Cart | Eliminar ítem | Quitar producto | `.shopping-tile button.trash` ("Eliminar") | `role=button[name='Eliminar']` | Media | Common | Medio | Verificado MA |
| Ambas | Cart | Resumen | Scope de importes | `div.expansion-panel:has-text('Resumen de compra')` | — | Media | Common | Medio | Verificado; "Subtotal:" se lee del texto del panel (sin clase propia) |
| Ambas | Cart | Total | Leer total | `.total-price-value` | — | Alta | Common | Bajo | Verificado; label `Total (IVA incl.)` |
| Ambas | Cart | Contador de ítems | Leer total de productos | `.total-products` ("Total de productos N") | — | Alta | Common | Bajo | Verificado en ambos |
| Ambas | Cart | CTA Pagar / continuar | Ir al gate/checkout | `role=button[name='Pagar']` | `button.buy-now` largo actual (MA) | Alta (nuevo) / Baja (actual) | Common | Medio | `role=button[name='Pagar']` verificado count=1 en ambos. El selector actual MA (`button.buy-now` + clases largas) es frágil → refactor recomendado |
| VIU | Cart | Cupón | Aplicar descuento | `role=button[name='Cupón de descuento']` + `role=button[name='Aplicar']` | — | Media | Específico | Medio | Verificado en dump de botones del carrito VIU |
| VIU | Cart | Método de envío | Seleccionar/envío | `role=button[name='Método de envío']` | — | Media | Específico | Medio | Verificado en dump VIU |

### Checkout (gate + formulario)

| Marca | Pantalla | Elemento | Responsabilidad | Selector principal | Selector alternativo | Estabilidad | Common / específico | Riesgo | Observación |
|---|---|---|---|---|---|---|---|---|---|
| Ambas | Checkout | Continuar como invitado | Entrar al checkout guest | `role=button[name='Continuar como invitado']` | — | Alta | Common | Bajo | Verificado en ambos (E2E MA + probe VIU) |
| Ambas | Checkout | Loader de checkout | Esperar SPA listo | `#checkout-loader` | — | Alta | Common | Bajo | Verificado MA; mismo OSC en VIU |
| Ambas | Checkout | Email | Identidad del guest | `input[name='username']` | — | Alta | Common | Bajo | Verificado ambos; el `id` (`customer-email`) es generado → no usar |
| Ambas | Checkout | Nombre | Datos personales | `input[name='firstname']` | — | Alta | Common | Bajo | name estable de Magento |
| Ambas | Checkout | Apellido paterno | Datos personales | `input[name='lastname']` | — | Alta | Common | Bajo | name estable |
| Ambas | Checkout | Apellido materno | Datos personales | `input[name='custom_attributes[address_mothers_name]']` | — | Alta | Common | Bajo | Presente en ambos (mismo OSC) |
| Ambas | Checkout | Teléfono | Contacto | `input[name='telephone']` | — | Alta | Common | Bajo | name estable |
| Ambas | Checkout | Calle | Dirección | `input[name='street[0]']` | — | Alta | Common | Bajo | name estable |
| Ambas | Checkout | Número exterior | Dirección | `input[name='custom_attributes[address_number]']` | — | Alta | Common | Bajo | Verificado ambos |
| Ambas | Checkout | Código postal | Dirección | `input[name='postcode']` | — | Alta | Common | Bajo | name estable |
| Ambas | Checkout | Colonia | Dirección | `input[name='custom_attributes[colonia]']` | — | Alta | Common | Bajo | Verificado ambos |
| Ambas | Checkout | Ciudad | Dirección | `input[name='city']` | — | Alta | Common | Bajo | name estable |
| Ambas | Checkout | Estado | Dirección | `select[name='region_id']` | — | Alta | Common | Bajo | SELECT; elegir por `label`/value |
| Ambas | Checkout | País | Dirección | `select[name='country_id']` | — | Alta | Common | Bajo | SELECT; usualmente prefijado MX |
| Ambas | Checkout | Referencia | Dirección | `input[name='custom_attributes[address_reference]']` | — | Alta | Common | Bajo | Opcional |
| Ambas | Checkout | Crear cuenta | Opción registro | `input[name='create-account-checkbox']` | `role=checkbox` con label | Alta | Common | Bajo | Dejar desmarcado para guest |
| Ambas | Checkout | Radios método envío | Elegir envío | `input[type='radio']` dentro de sección shipping (por `value`/`id` observable) | — | Media | Common | Medio | MA observado: `mavis_store_pickup_store_pickup`, `flatrate_flatrate`; names genéricos (`radio`/`ko_unique_*`) → usar `value`/`id` del método, no el name |
| Ambas | Checkout | Radios método pago | Elegir pago | `input[name='payment[method]']` por `id` del método | — | Alta | Common | Bajo | IDs observados estables: `openpay_cards`, `paypal_express`, `banktransfer`, `openpay_stores`, `omnipro_pago_credito` (set puede variar por marca) |
| Ambas | Checkout | Cupón | Aplicar descuento | `input[name='discount_code']` | `#discount-code` | Alta | Common | Bajo | Verificado VIU (`id='discount-code'`); mismo name MA |
| Ambas | Checkout | Total de la orden | Validar precio | `strong span.price` | — | Alta | Common | Bajo | Verificado count=1 en ambos checkouts (lo usa el test P0) |
| Ambas | Checkout | Tipo de cliente (radio) | guest/registrado | `input[value='guest']` / `input[value='client']` | — | Media | Common | Medio | `name` son `ko_unique_*` (Knockout, regenerado) → seleccionar por `value` |

### Payment / Order Confirmation

| Marca | Pantalla | Elemento | Responsabilidad | Selector principal | Selector alternativo | Estabilidad | Common / específico | Riesgo | Observación |
|---|---|---|---|---|---|---|---|---|---|
| Ambas | Payment | Botón realizar pedido | Confirmar compra | **Pendiente** | `role=button` en sección payment (verificar nombre real al alcanzar la pantalla) | Pendiente | Common | Alto | No se ejecutó compra real; el radio `payment[method]` está verificado pero el CTA final requiere levantamiento con pago de prueba |
| Ambas | Payment | Formulario de tarjeta | Captura de datos | **Pendiente** | — | Pendiente | Common | Alto | Depende del método (OpenPay/PayPal redirigen); no verificado |
| Ambas | Order Confirmation | Número de orden | Confirmar compra | **Pendiente** | — | Pendiente | Common | Alto | Pantalla solo alcanzable tras compra; mapear en sprint de checkout completo |
| Ambas | Order Confirmation | Resumen de orden | Validar pedido | **Pendiente** | — | Pendiente | Common | Alto | Ídem |

---

## Componentes realmente comunes (misma implementación MA/VIU)

- **Header completo**: mismos `data-testid` (`accountButton`, `openMicrocart`, `menuButton`, `subscribeSubmit`, `sidebar` — los tres primeros en el drawer móvil), mismos controles desktop (`aria-label='Abrir minicart'`, `a[href='/login']`, botón `Departamentos`) y mismo search input (`type=search` + `aria-label='Buscar'`).
- **Cookie banner**: `[data-testid='closeCookieButton']`.
- **Grilla/tile de producto**: `div.product-tile`.
- **PDP**: `button.add-to-cart`, notificación `div.notifications.fixed`, JSON-LD `Product`.
- **Checkout OSC completo**: mismos `name` de formulario (guest/address/shipping/payment/discount), `#checkout-loader`, `role=button[name='Continuar como invitado']`, `strong span.price`.
- **Cart items**: `.product-item-details`, `role=button[name='Pagar']`.

**Conclusión arquitectónica**: Header, Search, Results, Product Card, PDP, MiniCart y Checkout son candidatos a `pages/common/`; las diferencias se resuelven por configuración.

## Diferencias por marca

| Aspecto | Muebles América | VIU |
|---|---|---|
| URL carrito | `/carrito` | `/checkout/cart` |
| URL checkout | `mcstage.mueblesamerica.mx/onestepcheckout/` | `mcstage.viu.mx/onestepcheckout/` |
| Entrada a categorías | Mega-menú hover (`role=button[name='{department}']` + `a[href]`) | Botón `Departamentos` + links `/departamentos/*.html` |
| Flujo al carrito | Notificación + modal promo `Añadido al carrito` | Minicart `Ir al carrito de compras` |
| Promo overlay | `button[title='Close']` al entrar | No observado en probes |

## Selectores frágiles en uso (a refactorizar en sprints de Page Objects)

| Selector actual | Ubicación | Problema | Alternativa propuesta |
|---|---|---|---|
| `button.buy-now` + clases largas | `cart_locators.py` (MA) | Cadena de utilidades CSS | `role=button[name='Pagar']` (verificado) |
| `button.fw-600.fs-15.cl-white:visible` | `product_locators.py` (MA) | Clases de estilo genéricas | Scope `div.notifications` + `button:visible` |
| Add-to-cart con clases largas | `product_locators.py` (MA) | Cadena CSS + `data-v` potencial | `button.add-to-cart:visible` (verificado) |
| `id` dinámicos checkout (`VI…`, `IW…`) | Checkout ambos | Generados por render | `name` estable (ya documentado) |
| `ko_unique_*` | Radios tipo cliente | Knockout regenera | `input[value='guest'/'client']` |
| `data-v-*` | Todo el frontend | Vue scoped, cambia por build | Nunca como selector primario |

## Cobertura del criterio de aceptación

- **Elementos críticos del flujo P0** (home → categoría → PDP → carrito → checkout guest → total): todos con selector principal **verificado contra el DOM real**.
- **Payment final y Order Confirmation**: marcados `Pendiente` por requerir compra; el contrato prohíbe inventar selectores, quedan para el sprint de checkout completo.
- **Search por query**: input verificado en ambos; el submit (Enter vs botón) queda como observación a confirmar al implementar el componente.
