"""Locators del carrito de Muebles América (solo definiciones).

Extienden los comunes con lo que usa CP_EC_MA_CART_001, verificado en
stage MA (MABE00902, desktop 1366×768):

- Tras agregar, el estado del SPA `cart.cartItems` recibe el sku con
  `qty` y un `server_item_id` (ítem aceptado por Magento: `POST
  /api/cart/update` → 200).
- El botón del minicart del header muestra el contador ("Carrito\\n1").
- La página del carrito es `CART_ROUTE`.

Viven en la marca porque CART_001 aplica solo a MA (MA-AISLAMIENTO-001).
"""

from pages.common.components.cart.cart_locators import (
    CartLocators as CommonCartLocators,
)


class CartLocators(CommonCartLocators):
    CART_ROUTE = "/checkout/cart"
    CART_ITEMS_EXPR = (
        "window.__INITIAL_STATE__ && window.__INITIAL_STATE__.cart"
        " ? (window.__INITIAL_STATE__.cart.cartItems || []).map(i => ({"
        "sku: i.sku, qty: i.qty, name: i.name,"
        " server_item_id: i.server_item_id || null}))"
        " : []"
    )
