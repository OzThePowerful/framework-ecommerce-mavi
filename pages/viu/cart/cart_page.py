"""Carrito de VIU: fachada sobre el componente common."""

from playwright.sync_api import Page

from core.execution.execution_context import ExecutionContext
from domain.models.cart import Cart, CartItem
from domain.money.money import Money
from pages.base_page import BasePage
from pages.common.components.cart.cart_component import CartComponent


class CartPage(BasePage):
    def __init__(self, page: Page, context: ExecutionContext) -> None:
        super().__init__(page, context)
        self.cart = CartComponent(page)

    def open_cart(self) -> None:
        self.cart.open_cart()

    def items(self) -> list[CartItem]:
        return self.cart.items()

    def read_cart(self) -> Cart:
        return self.cart.read_cart()

    def total_products(self) -> int:
        return self.cart.total_products()

    def page_subtotal(self) -> Money:
        return self.cart.page_subtotal()

    def page_discount(self) -> Money:
        return self.cart.page_discount()

    def page_total(self) -> Money:
        return self.cart.page_total()

    def continue_to_checkout(self) -> None:
        self.cart.continue_to_checkout()
