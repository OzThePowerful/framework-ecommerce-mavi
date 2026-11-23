"""Checkout de VIU: gate de invitado vía componente common."""

from playwright.sync_api import Page

from core.execution.execution_context import ExecutionContext
from pages.base_page import BasePage
from pages.common.components.checkout.checkout_component import (
    CheckoutComponent,
)


class CheckoutPage(BasePage):
    def __init__(self, page: Page, context: ExecutionContext) -> None:
        super().__init__(page, context)
        self.gate = CheckoutComponent(page)

    def wait_for_guest_gate(self) -> None:
        self.gate.wait_for_guest_gate()

    def is_guest_gate_visible(self) -> bool:
        return self.gate.is_guest_gate_visible()
