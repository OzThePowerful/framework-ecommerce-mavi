"""Componente Order: éxito inequívoco y captura de la orden generada."""

import re

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.execution.execution_errors import (
    ElementStateError,
    NavigationError,
    PaymentError,
)
from domain.models.order import Order
from pages.common.components.order.order_locators import OrderLocators

_ORDER_RE = re.compile(
    r"(?:pedido|orden|order)[^0-9]{0,20}(\d{6,})", re.IGNORECASE
)


class OrderComponent:
    def __init__(self, page: Page) -> None:
        self.page = page

    # --- Éxito -----------------------------------------------------------
    def wait_success(self, timeout: int = 90000) -> None:
        """Espera la navegación a la página de éxito tras confirmar."""
        try:
            self.page.wait_for_url(
                OrderLocators.SUCCESS_URL, timeout=timeout
            )
        except PlaywrightTimeoutError as exc:
            decline = self.decline_message()
            if decline:
                raise PaymentError(
                    f"El pago fue rechazado: {decline}"
                ) from exc
            raise NavigationError(
                "No se llegó a la página de confirmación de orden"
            ) from exc
        try:
            self.page.locator(OrderLocators.SUCCESS_CONTAINER).first.wait_for(
                state="visible", timeout=20000
            )
        except PlaywrightTimeoutError as exc:
            raise ElementStateError(
                "La página de éxito no mostró el contenedor de confirmación"
            ) from exc

    def is_success(self) -> bool:
        """Éxito inequívoco: URL de éxito + contenedor + folio legible."""
        return (
            "success" in self.page.url
            and self.page.locator(OrderLocators.SUCCESS_CONTAINER).count() > 0
            and self.order_number() is not None
        )

    # --- Captura -----------------------------------------------------------
    def order_number(self) -> str | None:
        """Folio: "# NNNNNNNNNN" dentro de `.checkout-success` (regex);
        fallback sobre el body completo."""
        container = self.page.locator(OrderLocators.ORDER_NUMBER)
        if container.count():
            match = _ORDER_RE.search(container.first.inner_text())
            if match:
                return match.group(1)
        body = self.page.locator("body").inner_text()
        match = _ORDER_RE.search(body)
        return match.group(1) if match else None

    def confirmation_message(self) -> str | None:
        container = self.page.locator(OrderLocators.SUCCESS_CONTAINER)
        if not container.count():
            return None
        return container.first.inner_text().strip() or None

    def decline_message(self) -> str | None:
        errors = self.page.locator(OrderLocators.DECLINE_MESSAGE)
        for i in range(errors.count()):
            text = errors.nth(i).inner_text().strip()
            if text:
                return text
        return None

    def read_order(
        self,
        payment_method: str | None = None,
    ) -> Order:
        """Construye el modelo Order con lo observable en la página."""
        folio = self.order_number()
        if folio is None:
            raise ElementStateError(
                "No se pudo capturar el folio de la orden"
            )
        return Order(
            order_id=folio,
            folio=folio,
            payment_method=payment_method,
            confirmation_message=self.confirmation_message(),
        )
