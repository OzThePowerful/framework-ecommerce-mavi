"""Componente CustomerForm: datos personales del comprador en el OSC.

La dirección la resuelve `AddressComponent` (responsabilidad separada,
EC-SP01-015); este componente cubre identidad: correo, nombres,
apellidos y teléfono. Los `name` se repiten entre secciones KO, por
eso los selectores llevan `:visible`.
"""

from playwright.sync_api import Page

from domain.models.address import Address
from domain.models.customer import Customer
from pages.common.components.checkout.address_component import (
    AddressComponent,
)
from pages.common.components.checkout.checkout_locators import (
    CheckoutLocators,
)
from pages.common.components.checkout.field_utils import (
    fill_visible,
    value,
    value_or_none,
)


class CustomerFormComponent:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.address = AddressComponent(page)

    # --- Escritura ------------------------------------------------------
    def fill(self, customer: Customer, address: Address) -> None:
        """Llena datos del comprador y delega la dirección."""
        fill_visible(self.page, CheckoutLocators.EMAIL, customer.email)
        fill_visible(self.page, CheckoutLocators.FIRSTNAME, customer.name)
        fill_visible(self.page, CheckoutLocators.LASTNAME, customer.last_name)
        if customer.mothers_name:
            fill_visible(
                self.page, CheckoutLocators.MOTHERS_NAME, customer.mothers_name
            )
        if customer.phone:
            fill_visible(self.page, CheckoutLocators.PHONE, customer.phone)
        self.address.fill(address)

    # --- Lectura --------------------------------------------------------
    def read_customer(self) -> Customer:
        return Customer(
            email=value(self.page, CheckoutLocators.EMAIL),
            name=value(self.page, CheckoutLocators.FIRSTNAME),
            last_name=value(self.page, CheckoutLocators.LASTNAME),
            mothers_name=value_or_none(self.page, CheckoutLocators.MOTHERS_NAME),
            phone=value_or_none(self.page, CheckoutLocators.PHONE),
        )

    def read_address(self) -> Address:
        return self.address.read()

    def validation_errors(self) -> list[str]:
        """Mensajes de validación visibles del formulario."""
        errors = self.page.locator(CheckoutLocators.FIELD_ERRORS)
        return [
            errors.nth(i).inner_text().strip()
            for i in range(errors.count())
            if errors.nth(i).inner_text().strip()
        ]
