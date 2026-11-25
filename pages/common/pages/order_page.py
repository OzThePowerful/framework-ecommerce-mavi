"""Confirmación de orden: fachada base compartida por las marcas."""

from playwright.sync_api import Page

from core.execution.execution_context import ExecutionContext
from domain.models.order import Order
from pages.base_page import BasePage
from pages.common.components.order.order_component import OrderComponent


class CommonOrderPage(BasePage):
    def __init__(self, page: Page, context: ExecutionContext) -> None:
        super().__init__(page, context)
        self.confirmation = OrderComponent(page)

    def wait_success(self, timeout: int = 90000) -> None:
        self.confirmation.wait_success(timeout=timeout)

    def is_success(self) -> bool:
        return self.confirmation.is_success()

    def order_number(self) -> str | None:
        return self.confirmation.order_number()

    def confirmation_message(self) -> str | None:
        return self.confirmation.confirmation_message()

    def decline_message(self) -> str | None:
        return self.confirmation.decline_message()

    def read_order(self, payment_method: str | None = None) -> Order:
        return self.confirmation.read_order(payment_method)
