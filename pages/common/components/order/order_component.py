"""Componente Order: éxito inequívoco y captura de la orden generada."""

import re
import time
from decimal import Decimal

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.execution.execution_errors import (
    ElementStateError,
    NavigationError,
    PaymentError,
)
from domain.models.order import Order
from domain.money.money import Money
from pages.common.components.order.order_locators import OrderLocators

_ORDER_RE = re.compile(
    r"(?:pedido|orden|order)[^0-9]{0,20}(\d{6,})", re.IGNORECASE
)


def _money(value) -> Money | None:
    """Importe numérico del dataLayer (int/float/str) → Money, o None."""
    if value is None or value == "":
        return None
    return Money(Decimal(str(value)))


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

    # --- Información final de la orden (dataLayer `purchase`) ------------
    def success_heading(self) -> str | None:
        """Encabezado visible de la página final (`.page-title`), o None."""
        title = self.page.locator(f"{OrderLocators.SUCCESS_TITLE}:visible")
        if not title.count():
            return None
        return " ".join(title.first.inner_text().split()) or None

    def final_order(self, folio: str, timeout_ms: int = 10000) -> dict | None:
        """Orden final según los eventos `purchase` del dataLayer cuyo
        `transaction_id` es `folio`; None si no aparece en `timeout_ms`.

        Devuelve `{folio, items[{sku, name, qty, price, list_price}],
        subtotal, shipping, total, coupon, sale_type, events}`: importes en
        Money; `subtotal` = Σ price × qty; campos ausentes en un evento se
        completan con el otro; `events` conserva cada evento normalizado
        por separado (el step decide si son coherentes). Solo lectura.
        """
        deadline = time.monotonic() + timeout_ms / 1000
        while True:
            events = [
                self._normalize(e)
                for e in self.page.evaluate(OrderLocators.PURCHASE_EVENTS_EXPR)
                if str(e.get("transaction_id")) == folio
            ]
            if events or time.monotonic() >= deadline:
                break
            self.page.wait_for_timeout(250)
        if not events:
            return None
        merged = {key: value for key, value in events[0].items() if key != "items"}
        merged["items"] = [dict(item) for item in events[0]["items"]]
        for event in events[1:]:
            for key, value in event.items():
                if key != "items" and merged.get(key) in (None, ""):
                    merged[key] = value
            for item, other in zip(merged["items"], event["items"], strict=False):
                for key, value in other.items():
                    if item.get(key) is None:
                        item[key] = value
        merged["events"] = events
        return merged

    @staticmethod
    def _normalize(ecommerce: dict) -> dict:
        items = [
            {
                "sku": item.get("item_id"),
                "name": item.get("item_name"),
                "qty": int(item["quantity"]) if item.get("quantity") is not None else None,
                "price": _money(item.get("price")),
                "list_price": _money(item.get("price_sin_descuento")),
            }
            for item in ecommerce.get("items") or []
        ]
        subtotal = None
        if items and all(i["price"] and i["qty"] for i in items):
            subtotal = Money(Decimal("0"))
            for item in items:
                subtotal = subtotal + item["price"] * item["qty"]
        return {
            "folio": str(ecommerce.get("transaction_id")),
            "items": items,
            "subtotal": subtotal,
            "shipping": _money(ecommerce.get("shipping")),
            "total": _money(ecommerce.get("value")),
            "coupon": (ecommerce.get("coupon") or "").strip(),
            "sale_type": ecommerce.get("tipo_pago"),
        }
