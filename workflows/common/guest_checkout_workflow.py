"""Workflow: Home → categoría → PDP → carrito → checkout como invitado.

Coordina pages; no contiene locators ni asserts. Devuelve el precio del
checkout para que el test lo valide.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from core.execution.execution_context import ExecutionContext
from core.execution.execution_errors import DataError
from core.logging.logger import get_logger
from domain.money.money import Money


@dataclass(frozen=True)
class GuestCheckoutRequest:
    department: str
    category: str
    category_href: str
    product_name: str

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "GuestCheckoutRequest":
        missing = [
            name for name in cls.__dataclass_fields__ if not record.get(name)
        ]
        if missing:
            raise DataError(f"Faltan campos para GuestCheckoutRequest: {missing}")
        return cls(**{name: str(record[name]) for name in cls.__dataclass_fields__})


class GuestCheckoutWorkflow:
    def __init__(self, pages, context: ExecutionContext) -> None:
        self._pages = pages
        self._log = get_logger(
            __name__,
            run_id=context.run_id,
            case_id=context.case_id or "-",
            site=context.site,
            environment=context.environment,
        )

    def run(self, request: GuestCheckoutRequest) -> Money:
        self._log.info("Abriendo home")
        home = self._pages.home()
        home.open_home()
        home.accept_cookies_if_present()
        home.close_promo_if_present()

        self._log.info("Navegando a %s > %s", request.department, request.category)
        home.open_category_from_menu(
            department=request.department,
            category=request.category,
            href=request.category_href,
        )

        self._log.info("Abriendo PDP de '%s'", request.product_name)
        self._pages.search().open_product(request.product_name)

        product = self._pages.product()
        product.wait_until_ready()
        product.add_to_cart()
        product.open_cart_from_notification()

        self._log.info("Avanzando del carrito al checkout como invitado")
        self._pages.cart().buy_now()

        checkout = self._pages.checkout()
        checkout.continue_as_guest()
        checkout.wait_until_ready()
        price = checkout.get_displayed_price()
        self._log.info("Precio mostrado en checkout: %s %s", price.amount, price.currency)
        return price
