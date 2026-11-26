"""Componente Shipping: modo de entrega, retiro en sucursal y costo.

El modo activo se detecta por la clase `StorePickupSelected` en los
toggles `#domicilio`/`#sucursal`. El costo y el estimado se leen del
resumen (`Costo de envío` → `Gratis` o importe en `Money`).
"""

import re
from decimal import Decimal

from playwright.sync_api import Page

from core.execution.execution_errors import FrameworkError
from domain.models.shipping import Shipping
from domain.money.money import Money
from pages.common.components.checkout.checkout_locators import (
    ShippingLocators,
)
from pages.common.components.checkout.field_utils import fill_visible

DELIVERY_METHODS = {"a_domicilio", "sucursal"}


class ShippingComponent:
    def __init__(self, page: Page) -> None:
        self.page = page

    # --- Modo de entrega ------------------------------------------------
    def select_delivery_method(self, method: str) -> None:
        if method == "a_domicilio":
            self.select_home_delivery()
        elif method == "sucursal":
            self.select_store_pickup()
        else:
            raise FrameworkError(
                f"Método de entrega desconocido: {method!r} "
                f"(válidos: {sorted(DELIVERY_METHODS)})"
            )

    def select_home_delivery(self) -> None:
        self.page.locator(ShippingLocators.DELIVERY_HOME).click()

    def select_store_pickup(self) -> None:
        self.page.locator(ShippingLocators.DELIVERY_PICKUP).click()

    def has_delivery_options(self) -> bool:
        """Al menos un modo de entrega presentado (domicilio o sucursal)."""
        home = self.page.locator(ShippingLocators.DELIVERY_HOME).first
        pickup = self.page.locator(ShippingLocators.DELIVERY_PICKUP).first
        return home.is_visible() or pickup.is_visible()

    def current_delivery_mode(self) -> str | None:
        home = self.page.locator(ShippingLocators.DELIVERY_HOME)
        pickup = self.page.locator(ShippingLocators.DELIVERY_PICKUP)
        if ShippingLocators.SELECTED_FLAG in (home.get_attribute("class") or ""):
            return "a_domicilio"
        if ShippingLocators.SELECTED_FLAG in (pickup.get_attribute("class") or ""):
            return "sucursal"
        return None

    # --- Store picker ---------------------------------------------------
    def open_store_picker(self) -> None:
        self.page.locator(ShippingLocators.OPEN_STORE_PICKER).first.click()
        self.page.locator(ShippingLocators.STORE_POPUP).first.wait_for(
            state="visible"
        )

    def close_store_picker(self) -> None:
        self.page.locator(ShippingLocators.STORE_CLOSE).first.click()

    def select_picker_state(self, state: str) -> None:
        """Elige el estado en el picker y espera las sucursales.

        Al cambiar de estado la lista se re-renderiza de forma asíncrona;
        esperar solo al primer renglón devuelve sucursales del estado
        anterior, así que se espera a que la lista quede estable.
        """
        self.page.locator(ShippingLocators.STORE_STATE_SELECT).select_option(
            label=state
        )
        self.page.locator(ShippingLocators.STORE_ROW).first.wait_for(
            state="visible"
        )
        previous: list[str] | None = None
        # KO repinta la lista de forma asíncrona: se sondea hasta que dos
        # lecturas consecutivas coinciden (no hay evento determinista).
        for _ in range(10):
            self.page.wait_for_timeout(300)
            current = self.stores()
            if current and current == previous:
                return
            previous = current

    def stores(self) -> list[str]:
        """Nombres de sucursales visibles en el picker (debe estar abierto)."""
        rows = self.page.locator(ShippingLocators.STORE_ROW)
        return [
            rows.nth(i).locator(ShippingLocators.STORE_NAME).inner_text().strip()
            for i in range(rows.count())
            if rows.nth(i).is_visible()
        ]

    def select_store(self, store_name: str) -> None:
        """Elige 'Entregar aquí' en la sucursal indicada y cierra el picker."""
        row = self.page.locator(
            ShippingLocators.STORE_ROW, has_text=store_name
        ).first
        if not row.count():
            raise FrameworkError(
                f"Sucursal no encontrada en el picker: {store_name!r} "
                f"(visibles: {self.stores()})"
            )
        row.locator(ShippingLocators.STORE_DELIVER_HERE).click()
        self.page.locator(ShippingLocators.STORE_POPUP).first.wait_for(
            state="hidden"
        )

    def fill_pickup_contact(
        self,
        firstname: str,
        father_name: str,
        phone: str,
        mother_name: str | None = None,
    ) -> None:
        """Datos de quien recoge en sucursal (campos propios del pickup)."""
        fill_visible(self.page, ShippingLocators.PICKUP_FIRSTNAME, firstname)
        fill_visible(self.page, ShippingLocators.PICKUP_FATHER, father_name)
        if mother_name:
            fill_visible(self.page, ShippingLocators.PICKUP_MOTHER, mother_name)
        fill_visible(self.page, ShippingLocators.PICKUP_PHONE, phone)

    # --- Resumen: costo y estimado ---------------------------------------
    def shipping(self) -> Shipping:
        """Modelo de envío con el modo actual y su costo."""
        return Shipping(
            method=self.current_delivery_mode() or "desconocido",
            cost=self.shipping_cost(),
        )

    def shipping_cost(self, timeout: int = 20000) -> Money:
        """Costo de envío; espera a que el OSC lo calcule ('Aún no calculado')."""
        text = self._wait_shipping_ready(timeout)
        match = re.search(
            r"env\S*\s*:?\s*(Gratis|\$?[\d,]+\.\d+)", text, re.IGNORECASE
        )
        if not match:
            raise FrameworkError(
                f"El resumen no expone costo de envío: {text[:200]!r}"
            )
        raw = match.group(1)
        if raw.lower().startswith("gratis"):
            return Money(Decimal("0"))
        digits = re.sub(r"[^\d.]", "", raw)
        return Money(Decimal(digits))

    def _wait_shipping_ready(self, timeout: int) -> str:
        """Devuelve el texto del resumen cuando el envío ya tiene valor."""
        summary = self.page.locator(ShippingLocators.SUMMARY_PANEL).first
        summary.wait_for(state="visible")
        self.page.wait_for_function(
            """() => {
                const el = document.querySelector('.omni-summary-totals');
                if (!el) return false;
                return /env\\S*\\s*:?\\s*(Gratis|\\$[\\d,.]+)/i.test(el.innerText);
            }""",
            timeout=timeout,
        )
        return summary.inner_text()

    def summary_totals(self) -> dict[str, Money]:
        """Importes del resumen del checkout (Subtotal/Envío/Total) en Money.

        Etiquetas tolerantes: 'Envío' o 'Costo de envío';
        'Total (IVA incl.)' o 'Total'.
        """
        text = self._summary_text()
        return {
            "subtotal": self._money_row(text, r"subtotal"),
            "shipping": self._money_row(text, r"(?:costo de )?env\S*"),
            "total": self._money_row(text, r"total(?: \(iva incl\.?\))?", last=True),
        }

    def summary_total(self) -> Money:
        """Solo la fila Total del resumen.

        Tolera etapas donde el envío aún no está calculado
        ('Envío: Aún no calculado'), a diferencia de summary_totals().
        """
        return self._money_row(
            self._summary_text(), r"total(?: \(iva incl\.?\))?", last=True
        )

    def _money_row(self, text: str, label_re: str, last: bool = False) -> Money:
        matches = re.findall(
            rf"{label_re}\s*:?\s*(Gratis|\$[\d,]+\.\d+)",
            text,
            re.IGNORECASE,
        )
        if not matches:
            raise FrameworkError(
                f"El resumen no expone la fila {label_re!r}: {text[:200]!r}"
            )
        raw = matches[-1] if last else matches[0]
        if raw.lower().startswith("gratis"):
            return Money(Decimal("0"))
        digits = re.sub(r"[^\d.]", "", raw)
        return Money(Decimal(digits))

    def delivery_estimate(self) -> str | None:
        match = re.search(
            r"Entrega entre el [^\n]+", self._summary_text()
        )
        return match.group(0).strip() if match else None

    def _summary_text(self) -> str:
        """Texto del bloque de totales del resumen (.omni-summary-totals)."""
        summary = self.page.locator(ShippingLocators.SUMMARY_PANEL).first
        summary.wait_for(state="visible")
        return summary.inner_text()
