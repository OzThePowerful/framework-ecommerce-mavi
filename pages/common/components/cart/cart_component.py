"""Componente Cart: minicart + página de carrito (/checkout/cart).

Lee ítems como `CartItem` y el carrito completo como `Cart` de dominio;
los importes se normalizan a `Money`/`Decimal`.
"""

import re
from decimal import Decimal, InvalidOperation

from playwright.sync_api import Page

from core.execution.execution_errors import FrameworkError
from domain.models.cart import Cart, CartItem
from domain.models.product import Product
from domain.money.money import Money
from pages.common.components.cart.cart_locators import CartLocators


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

    def page_total(self) -> Money:
        return _money(
            self.page.locator(CartLocators.TOTAL_VALUE).first.inner_text()
        )

    # --- Transición -----------------------------------------------------
    def continue_to_checkout(self) -> None:
        self.page.locator(CartLocators.CONTINUE).click()
