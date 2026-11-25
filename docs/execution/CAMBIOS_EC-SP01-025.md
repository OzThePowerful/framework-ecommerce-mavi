# EC-SP01-025 — Consolidación de componentes comunes

Refactorización por **reutilización demostrada**: las fachadas de página de
ambas marcas eran idénticas salvo el import de locators. Se extraen bases a
`pages/common/pages/` y las fachadas de marca quedan como subclases delgadas.
**Cero `if site`**: toda variación vive en la subclase (locators + overrides).

## Decisiones por bloque

| Bloque | Decisión |
|---|---|
| `search_page`, `cart_page`, `payment_page`, `order_page` | Idénticas → base común; fachada marca = subclase vacía |
| `checkout_page` | Base común + overrides de marca: `continue_as_guest` (MA: `expect_navigation`; VIU: delega al gate) y `get_displayed_price` (MA: locator `TOTAL_PRICE`; VIU: `summary_total`) |
| `home_page` | Base común; la marca inyecta su mega-menú vía `MEGA_MENU` ClassVar. `close_promo_if_present` = no-op en base, override en MA |
| `product_page` | Base común con delegación PDP + `add_to_cart` vía `PRODUCT_LOCATORS` ClassVar; post-add (`dismiss_post_add_overlays`, `open_cart_from_notification`) implementado por marca |
| `search_locators` | Idénticos → mergeados a `pages/common/components/search/` (`GRID`) |
| `cart_locators.BUY_NOW_BUTTON` | Unificado: MA adopta `button.buy-now:visible` (verificado en ambas marcas; `:visible` discrimina la copia móvil) |
| Locators vacíos (`order`, `home` VIU, `checkout` VIU) | Eliminados — código muerto |
| Mega menu MA/VIU | Se mantienen específicos (DOM estructuralmente distinto, misma fachada) |
| `promotions_window` | Se mantiene MA-only |

## Archivos

- **Nuevos**: `pages/common/pages/{__init__,search_page,cart_page,payment_page,order_page,checkout_page,home_page,product_page}.py`
- **Simplificados**: `pages/{muebles_america,viu}/*/​*_page.py` — subclases delgadas; mismas rutas de import = PageFactory/steps intactos
- **Modificado**: `pages/common/components/cart/cart_locators.py` (+`BUY_NOW_BUTTON`)
- **Eliminados**: locators mergeados/vacíos (8 archivos)

## Validación

| Prueba | Resultado |
|---|---|
| compileall + ruff + 115 unit/arch + colección 21×2 | ✅ |
| `CP_EC_MA_SMOKE_001` | ✅ |
| `CP_EC_VIU_SMOKE_001` | ✅ |
| Suite afectada MA (`-k "not E2E"`) | ✅ 18/18 |
| Suite afectada VIU | ✅ 18/18 |
| `CP_EC_MA_E2E_001` orden real | ✅ folio **2000058591** |
| `CP_EC_VIU_E2E_001` orden real | ✅ folio **12000050255** |
