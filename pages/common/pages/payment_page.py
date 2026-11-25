"""Pago: fachada base compartida por las marcas."""

from playwright.sync_api import Page

from core.execution.execution_context import ExecutionContext
from pages.base_page import BasePage
from pages.common.components.payment.payment_component import (
    PaymentComponent,
)


class CommonPaymentPage(BasePage):
    def __init__(self, page: Page, context: ExecutionContext) -> None:
        super().__init__(page, context)
        self.payment = PaymentComponent(page)

    def open_payment_stage(self) -> None:
        self.payment.open_payment_stage()

    def payment_methods(self) -> list[str]:
        return self.payment.payment_methods()

    def is_method_selectable(self, method: str) -> bool:
        return self.payment.is_method_selectable(method)

    def select_method(self, method: str) -> None:
        self.payment.select_method(method)

    def selected_method(self) -> str | None:
        return self.payment.selected_method()

    def expects_external_provider(self, method: str) -> bool:
        return self.payment.expects_external_provider(method)

    def fill_card(self, number: str, exp_month: str, exp_year: str, cvv: str) -> None:
        self.payment.fill_card(number, exp_month, exp_year, cvv)

    def set_billing_same_as_shipping(self, checked: bool) -> None:
        self.payment.set_billing_same_as_shipping(checked)

    def is_billing_same_as_shipping(self) -> bool:
        return self.payment.is_billing_same_as_shipping()

    def is_place_order_enabled(self) -> bool:
        return self.payment.is_place_order_enabled()

    def wait_place_order_enabled(self, timeout: int = 20000) -> None:
        self.payment.wait_place_order_enabled(timeout=timeout)

    def confirm_order(self) -> None:
        self.payment.confirm_order()

    def validation_errors(self) -> list[str]:
        return self.payment.validation_errors()
