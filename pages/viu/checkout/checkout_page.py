"""Checkout de VIU (OneStepCheckout): fachada sobre componentes common."""

from playwright.sync_api import Page

from core.execution.execution_context import ExecutionContext
from domain.models.address import Address
from domain.models.customer import Customer
from pages.base_page import BasePage
from pages.common.components.checkout.checkout_component import (
    CheckoutComponent,
)
from pages.common.components.checkout.customer_form_component import (
    CustomerFormComponent,
)


class CheckoutPage(BasePage):
    def __init__(self, page: Page, context: ExecutionContext) -> None:
        super().__init__(page, context)
        self.gate = CheckoutComponent(page, context.checkout_url_pattern)
        self.customer_form = CustomerFormComponent(page)

    # --- Entrada --------------------------------------------------------
    def wait_for_guest_gate(self) -> None:
        self.gate.wait_for_guest_gate()

    def is_guest_gate_visible(self) -> bool:
        return self.gate.is_guest_gate_visible()

    def continue_as_guest(self) -> None:
        self.gate.continue_as_guest()

    # --- Etapa / estructura ---------------------------------------------
    def wait_until_ready(self) -> None:
        self.gate.wait_until_ready()

    def current_stage(self) -> str | None:
        return self.gate.current_stage()

    def is_payment_stage_enabled(self) -> bool:
        return self.gate.is_payment_stage_enabled()

    def wait_payment_stage_enabled(self) -> None:
        self.gate.wait_payment_stage_enabled()

    def required_fields(self) -> list[str]:
        return self.gate.required_fields()

    # --- Datos del comprador --------------------------------------------
    def fill_customer_form(self, customer: Customer, address: Address) -> None:
        self.customer_form.fill(customer, address)

    def read_customer(self) -> Customer:
        return self.customer_form.read_customer()

    def read_address(self) -> Address:
        return self.customer_form.read_address()

    def validation_errors(self) -> list[str]:
        return self.customer_form.validation_errors()
