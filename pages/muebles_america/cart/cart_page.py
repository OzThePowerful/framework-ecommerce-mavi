"""Carrito de Muebles América: fachada sobre la base common.

Agrega los sondeos que usa CP_EC_MA_CART_001 (MA-AISLAMIENTO-001):
estado del SPA tras agregar, contador del minicart y carrito abierto.
Devuelven estado, sin asserts.
"""

import re
import time
from urllib.parse import urlparse

from pages.common.pages.cart_page import CommonCartPage
from pages.muebles_america.cart.cart_locators import CartLocators

_POLL_MS = 250


class CartPage(CommonCartPage):
    def state_item(self, sku: str, timeout_ms: int = 10000) -> dict | None:
        """Ítem `sku` del estado del SPA (`cart.cartItems`).

        Espera hasta `timeout_ms` a que el ítem quede sincronizado con
        Magento (`server_item_id`). Devuelve el último ítem visto con ese
        sku, sincronizado o no, o None si nunca apareció.
        """
        deadline = time.monotonic() + timeout_ms / 1000
        last = None
        while True:
            items = self.page.evaluate(CartLocators.CART_ITEMS_EXPR) or []
            last = next((i for i in items if i.get("sku") == sku), last)
            if (last and last.get("server_item_id")) or time.monotonic() >= deadline:
                return last
            self.page.wait_for_timeout(_POLL_MS)

    def minicart_count(self) -> int:
        """Contador del minicart del header (0 si no muestra número)."""
        text = self.page.locator(CartLocators.OPEN_MINICART).first.inner_text()
        match = re.search(r"\d+", text or "")
        return int(match.group(0)) if match else 0

    def wait_for_minicart_count(self, expected: int, timeout_ms: int = 10000) -> int:
        """Espera a que el contador llegue a `expected`; devuelve el último
        valor observado (el llamador decide si coincide)."""
        deadline = time.monotonic() + timeout_ms / 1000
        while True:
            count = self.minicart_count()
            if count == expected or time.monotonic() >= deadline:
                return count
            self.page.wait_for_timeout(_POLL_MS)

    def is_open(self) -> bool:
        """Página del carrito abierta: ruta del carrito + contenedor visible."""
        on_route = urlparse(self.page.url).path.rstrip("/").endswith(
            CartLocators.CART_ROUTE
        )
        return on_route and self.page.locator(
            CartLocators.CART_ROOT
        ).first.is_visible()
