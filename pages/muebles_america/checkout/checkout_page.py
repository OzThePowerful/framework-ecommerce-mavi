"""Checkout de Muebles América (OneStepCheckout)."""

import re
from decimal import Decimal, InvalidOperation

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.execution.execution_context import ExecutionContext
from core.execution.execution_errors import ElementStateError, NavigationError
from domain.models.address import Address
from domain.models.customer import Customer
from domain.models.shipping import Shipping
from domain.money.money import Money
from pages.base_page import BasePage
from pages.common.components.checkout.checkout_component import (
    CheckoutComponent,
)
from pages.common.components.checkout.customer_form_component import (
    CustomerFormComponent,
)
from pages.common.components.checkout.shipping_component import (
    ShippingComponent,
)
from pages.muebles_america.checkout.checkout_locators import CheckoutLocators


class CheckoutPage(BasePage):
    def __init__(self, page: Page, context: ExecutionContext) -> None:
        super().__init__(page, context)
        self.gate = CheckoutComponent(page, context.checkout_url_pattern)
        self.customer_form = CustomerFormComponent(page)
        self.delivery = ShippingComponent(page)

    # --- Entrada --------------------------------------------------------
    def wait_for_guest_gate(self) -> None:
        self.gate.wait_for_guest_gate()

    def is_guest_gate_visible(self) -> bool:
        return self.gate.is_guest_gate_visible()

    def continue_as_guest(self) -> None:
        """Continúa como invitado esperando la navegación al checkout.

        El patrón de URL proviene de sites.yaml vía ExecutionContext;
        el page no conoce hosts ni ambientes.
        """
        try:
            with self.page.expect_navigation(
                url=self.context.checkout_url_pattern
            ):
                self.page.locator(CheckoutLocators.GUEST_CONTINUE_BUTTON).click()
        except PlaywrightTimeoutError as exc:
            raise NavigationError(
                "No se navegó a "
                f"'{self.context.checkout_url_pattern}' tras continuar como "
                "invitado"
            ) from exc

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

    # --- Entrega --------------------------------------------------------
    def select_delivery_method(self, method: str) -> None:
        self.delivery.select_delivery_method(method)

    def current_delivery_mode(self) -> str | None:
        return self.delivery.current_delivery_mode()

    def shipping(self) -> Shipping:
        return self.delivery.shipping()

    def shipping_cost(self) -> Money:
        return self.delivery.shipping_cost()

    def summary_totals(self) -> dict[str, Money]:
        return self.delivery.summary_totals()

    def delivery_estimate(self) -> str | None:
        return self.delivery.delivery_estimate()

    # --- Recoger en sucursal -------------------------------------------
    def open_store_picker(self) -> None:
        self.delivery.open_store_picker()

    def select_picker_state(self, state: str) -> None:
        self.delivery.select_picker_state(state)

    def stores(self) -> list[str]:
        return self.delivery.stores()

    def select_store(self, store_name: str) -> None:
        self.delivery.select_store(store_name)

    def fill_pickup_contact(
        self,
        firstname: str,
        father_name: str,
        phone: str,
        mother_name: str | None = None,
    ) -> None:
        self.delivery.fill_pickup_contact(
            firstname, father_name, phone, mother_name
        )

    # --- Resumen ----------------------------------------------------------
    def get_displayed_price(self) -> Money:
        """Expone el precio mostrado como Money; la validación la hace el test."""
        text = self.page.locator(CheckoutLocators.TOTAL_PRICE).first.inner_text()
        # Formato mostrado: "$12,999.00" (separador de miles ",", decimal ".").
        digits = re.sub(r"[^\d.]", "", text)
        try:
            return Money(Decimal(digits))
        except InvalidOperation as exc:
            raise ElementStateError(
                f"El precio del checkout no tiene un importe legible: {text!r}"
            ) from exc
