# CAMBIOS EC-SP01-008 — DOM y estrategia de locators

**Tipo**: levantamiento técnico / documentación de arquitectura (sin Page Objects nuevos, conforme al alcance del contrato).

## Qué se hizo

Se sondeó el DOM real en **stage** de ambos ecommerce con Playwright headless,
recorriendo el flujo completo hasta donde el sitio lo permite sin compra real:

- **Muebles América** (`mueblesstage.mavi.mx`): home, header, mega-menú, PDP, notificación, carrito (`/carrito`), gate invitado y checkout (`mcstage.mueblesamerica.mx/onestepcheckout/`).
- **VIU** (`viustage.mavi.mx`): home, header, categoría, PDP, minicart, carrito (`/checkout/cart`), gate invitado y checkout (`mcstage.viu.mx/onestepcheckout/`).

## Entregable

`docs/architecture/matriz_locators.md` — matriz con las 10 columnas del contrato
(Marca, Pantalla, Elemento, Responsabilidad, Selector principal, Selector
alternativo, Estabilidad, Common/específico, Riesgo, Observación), cubriendo las
14 pantallas del alcance.

## Hallazgos verificados contra el DOM

- **Stack compartido**: ambos sitios son el mismo Magento + OneStepCheckout + frontend Vue → el checkout tiene `name` de formulario idénticos (`username`, `firstname`, `lastname`, `telephone`, `street[0]`, `postcode`, `city`, `region_id`, `country_id`, `discount_code`, `payment[method]`, `custom_attributes[...]`).
- **data-testid reales**: `closeCookieButton`, `accountButton`, `openMicrocart`, `menuButton`, `sidebar`, `subscribeSubmit` — idénticos en ambos.
- **Search**: `input[type='search'][aria-label='Buscar']` (2 instancias desktop/mobile, la visible es la activa; sin `name`/`id`; `data-v-*` ignorado).
- **PDP sin `h1` ni `span.price`**: el título/precio confiable es el **JSON-LD `@type=Product`** (verificado con nombre exacto en ambos). El `[class*='price']` visible es el precio semanal de financiamiento, no el principal.
- **add-to-cart**: `button.add-to-cart` da 2 instancias (una oculta) → `:visible` discrimina, verificado en ambos.
- **Gate invitado**: `role=button[name='Continuar como invitado']` verificado en ambos.
- **Total**: `strong span.price` verificado (count=1) en ambos checkouts.
- **Diferencias de marca**: URL del carrito (`/carrito` vs `/checkout/cart`), entrada a categorías (mega-menú hover vs botón `Departamentos`), flujo al carrito (modal promo vs minicart).

## Selectores frágiles detectados en el código actual

Documentados en la matriz con alternativa propuesta (refactor pendiente en los
sprints de Page Objects, fuera del alcance de esta tarea):

- `button.buy-now` + clases largas → `role=button[name='Pagar']` (verificado).
- `button.fw-600.fs-15.cl-white:visible` → scope en `div.notifications`.
- IDs dinámicos del checkout y `ko_unique_*` → `name`/`value` estables.
- `data-v-*` → prohibido como selector primario.

## Pendientes (sin inventar selectores)

- **Payment final / Order Confirmation**: requieren compra real; marcados `Pendiente` con riesgo alto.
- **Submit de búsqueda**: input verificado; Enter vs botón dedicado a confirmar al implementar el componente.
- **CTA minicart de MA**: el flujo real pasa por la notificación/modal promo; refactor pendiente.

## Criterio de aceptación

✅ Todos los elementos críticos del flujo P0 tienen estrategia de localización
**verificada contra el DOM real** de ambos sitios en stage.

## Validación

- Probes ejecutados contra el DOM en vivo (no fixtures ni mocks): home, categoría, PDP, carrito y checkout completos de ambas marcas.
- `ruff check .` y `compileall`: sin cambios de código Python — no aplican a una tarea documental.
- Suite existente intacta (no se modificó código ni tests).
