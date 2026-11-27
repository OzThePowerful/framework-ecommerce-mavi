"""Confirmación de orden de Muebles América: fachada sobre la base common.

El comportamiento es el de la base común; aquí se agregan la lectura del
encabezado de la página de éxito (CP_EC_MA_ORDER_001) y la información
final de la orden publicada en el dataLayer (CP_EC_MA_ORDER_002).
"""

import time
from decimal import Decimal

from domain.money.money import Money
from pages.common.components.order.order_locators import (
    OrderLocators as CommonOrderLocators,
)
from pages.common.pages.order_page import CommonOrderPage
from pages.muebles_america.order.order_locators import OrderLocators


def _money(value) -> Money | None:
    """Importe numérico del dataLayer (int/float/str) → Money, o None."""
    if value is None or value == "":
        return None
    return Money(Decimal(str(value)))


class OrderPage(CommonOrderPage):
    def success_heading(self) -> str | None:
        """Encabezado visible de la página final (`.page-title`), o None."""
        title = self.page.locator(f"{CommonOrderLocators.SUCCESS_TITLE}:visible")
        if not title.count():
            return None
        return " ".join(title.first.inner_text().split()) or None

    # --- Información final de la orden (CP_EC_MA_ORDER_002) ---------------
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
