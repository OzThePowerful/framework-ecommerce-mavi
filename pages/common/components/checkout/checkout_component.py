"""Componente Checkout (gate + estructura del acordeón OSC).

El formulario del comprador vive en `customer_form_component.py`;
aquí quedan la transición de entrada, la detección de etapa y el
estado de los pasos del acordeón.
"""

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.execution.execution_errors import NavigationError
from pages.common.components.checkout.checkout_locators import (
    CheckoutGateLocators,
    CheckoutLocators,
)

_STAGES = (
    ("entrega", CheckoutLocators.SHIPPING_STEP),
    ("forma_de_pago", CheckoutLocators.PAYMENT_STEP),
    ("resumen", CheckoutLocators.SUMMARY_STEP),
)


class CheckoutComponent:
    def __init__(self, page: Page, checkout_url_pattern: str | None = None) -> None:
        self.page = page
        self._checkout_url_pattern = checkout_url_pattern

    # --- Entrada --------------------------------------------------------
    def wait_for_guest_gate(self) -> None:
        self.page.locator(CheckoutGateLocators.GUEST_CONTINUE).first.wait_for(
            state="visible"
        )

    def is_guest_gate_visible(self) -> bool:
        return self.page.locator(CheckoutGateLocators.GUEST_CONTINUE).count() > 0

    def continue_as_guest(self) -> None:
        """Clic en 'Continuar como invitado' y espera de la navegación al OSC."""
        target = self._checkout_url_pattern or "**/onestepcheckout/**"
        try:
            with self.page.expect_navigation(url=target):
                self.page.locator(CheckoutGateLocators.GUEST_CONTINUE).first.click()
        except PlaywrightTimeoutError as exc:
            raise NavigationError(
                f"No se navegó a '{target}' tras continuar como invitado"
            ) from exc

    def wait_until_ready(self) -> None:
        """Loader OSC fuera + campos del comprador renderizados (KO lazy)."""
        loader = self.page.locator(CheckoutLocators.LOADER)
        if loader.count():
            loader.first.wait_for(state="detached")
        self.page.locator(CheckoutLocators.EMAIL).first.wait_for(state="visible")

    # --- Etapa del acordeón ---------------------------------------------
    def current_stage(self) -> str | None:
        """Etapa abierta del acordeón: entrega | forma_de_pago | resumen."""
        for stage, selector in _STAGES:
            el = self.page.locator(selector)
            if el.count() and "opened" in (el.first.get_attribute("class") or ""):
                return stage
        return None

    def is_payment_stage_enabled(self) -> bool:
        """'Forma de pago' habilitada (la dirección ya fue aceptada)."""
        button = self.page.locator(CheckoutLocators.PAYMENT_STEP)
        return button.count() > 0 and button.first.get_attribute("disabled") is None

    def wait_payment_stage_enabled(self, timeout: int = 20000) -> None:
        """La validación KO de la dirección habilita el paso de pago asíncronamente."""
        self.page.wait_for_function(
            """() => {
                const b = document.getElementById('paymentExpansionButton');
                return b && !b.hasAttribute('disabled');
            }""",
            timeout=timeout,
        )

    def required_fields(self) -> list[str]:
        """Names de los inputs obligatorios visibles en el formulario."""
        names: list[str] = []
        inputs = self.page.locator(CheckoutLocators.REQUIRED_INPUTS)
        for i in range(inputs.count()):
            name = inputs.nth(i).get_attribute("name")
            if name and name not in names:
                names.append(name)
        return names
