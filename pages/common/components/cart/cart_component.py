"""Componente Cart: minicart + página de carrito (/checkout/cart).

Lee ítems como `CartItem` y el carrito completo como `Cart` de dominio;
los importes se normalizan a `Money`/`Decimal`.
"""

import re
import time
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse

from playwright.sync_api import Page

from core.execution.execution_errors import FrameworkError
from domain.models.cart import Cart, CartItem
from domain.models.product import Product
from domain.money.money import Money
from pages.common.components.cart.cart_locators import CartLocators

_POLL_MS = 250
_SUMMARY_SUBTOTAL = re.compile(r"Subtotal:\s*\$?\s*([\d,]+\.\d{2})")


def _money(text: str) -> Money:
    """'$11,189.00' → Money(11189.00)."""
    digits = re.sub(r"[^\d.]", "", text or "")
    try:
        return Money(Decimal(digits))
    except InvalidOperation as exc:
        raise FrameworkError(f"Importe no legible: {text!r}") from exc


class CartComponent:
    def __init__(self, page: Page) -> None:
        self.page = page

    # --- Navegación -----------------------------------------------------
    def open_cart(self) -> None:
        """Abre el minicart desde el header y navega a /checkout/cart."""
        self.page.locator(CartLocators.OPEN_MINICART).first.click()
        go = self.page.locator(CartLocators.GO_TO_CART).first
        go.wait_for(state="visible")
        go.click()
        self.page.wait_for_url("**/checkout/cart**", timeout=15000)
        self.wait_until_ready()

    def wait_until_ready(self) -> None:
        self.page.locator(CartLocators.CART_ROOT).first.wait_for(state="visible")

    # --- Ítems ----------------------------------------------------------
    def items(self) -> list[CartItem]:
        """Ítems del carrito como CartItem (producto + cantidad + precio)."""
        rows = self.page.locator(CartLocators.CART_ROOT).locator(
            CartLocators.ITEM_ROW
        )
        items: list[CartItem] = []
        for i in range(rows.count()):
            row = rows.nth(i)
            sku_text = row.locator(CartLocators.ITEM_SKU).first.inner_text() or ""
            sku = sku_text.replace("SKU#:", "").strip()
            name = (
                row.locator(CartLocators.ITEM_NAME).first.inner_text() or ""
            ).strip()
            qty_text = row.locator(CartLocators.ITEM_QTY).first.inner_text() or "1"
            qty = int(re.search(r"\d+", qty_text).group(0))
            final = _money(
                row.locator(CartLocators.ITEM_PRICE_CURRENT).first.inner_text()
            )
            crossed = row.locator(CartLocators.ITEM_PRICE_CROSSED)
            regular = (
                _money(crossed.first.inner_text())
                if crossed.count()
                else final
            )
            product = Product(
                sku=sku,
                name=name,
                unit_price=regular,
                promotional_price=final if final.amount < regular.amount else None,
            )
            items.append(CartItem(product=product, quantity=qty, unit_price=final))
        return items

    def read_cart(self) -> Cart:
        """El carrito completo como modelo de dominio."""
        return Cart(items=self.items(), discount=self.page_discount())

    # --- Estado del SPA (confirmación backend del add) -------------------
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

    # --- Resumen --------------------------------------------------------
    def total_products(self) -> int:
        text = self.page.locator(CartLocators.TOTAL_PRODUCTS).first.inner_text()
        match = re.search(r"(\d+)", text or "")
        return int(match.group(1)) if match else -1

    def page_subtotal(self) -> Money:
        summary = self.page.locator(CartLocators.SUMMARY).first.inner_text()
        match = re.search(r"Subtotal:\s*\$?([\d,]+\.\d+)", summary or "")
        return _money(match.group(1)) if match else Money(Decimal("0"))

    def page_discount(self) -> Money:
        summary = self.page.locator(CartLocators.SUMMARY).first.inner_text()
        match = re.search(r"Descuento:\s*-?\$?([\d,]+\.\d+)", summary or "")
        return _money(match.group(1)) if match else Money(Decimal("0"))

    def summary_subtotal(self) -> Money | None:
        """'Subtotal:' del resumen de compra, o None si el resumen no lo
        muestra.

        A diferencia de `page_subtotal()` (0 si no lo encuentra), devuelve
        None para que el llamador distinga 'ausente' de 'cero'.
        """
        summary = self.page.locator(CartLocators.SUMMARY)
        if not summary.count():
            return None
        match = _SUMMARY_SUBTOTAL.search(summary.first.inner_text() or "")
        if not match:
            return None
        return Money(Decimal(match.group(1).replace(",", "")))

    def page_total(self) -> Money:
        return _money(
            self.page.locator(CartLocators.TOTAL_VALUE).first.inner_text()
        )

    # --- Transición -----------------------------------------------------
    def continue_to_checkout(self) -> None:
        self.page.locator(CartLocators.CONTINUE).click()
