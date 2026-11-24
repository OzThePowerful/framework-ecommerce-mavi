"""Workflow de venta de contado multi-ecommerce (EC-SP01-018-1).

Coordina Home → Search → PDP → Cart → Checkout → Customer → Address →
Shipping → Payment → Order a través de la fachada de pages del sitio
activo. Las diferencias MA/VIU se resuelven por composición: el
PageFactory del ExecutionContext materializa la fachada de cada marca;
este workflow no contiene `if site`, locators, Playwright, asserts
funcionales ni lectura de YAML.

Errores de precondición se propagan sin ocultarlos: cada etapa anota su
nombre en la excepción (`BaseException.add_note`) y la relanza.

Casos relacionados: CP_EC_MA_E2E_001 / CP_EC_VIU_E2E_001.
"""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, TypeVar

from core.execution.execution_context import ExecutionContext
from core.execution.execution_errors import PaymentError
from core.logging.logger import get_logger
from domain.errors.precondition_error import PreconditionError
from domain.models.address import Address
from domain.models.cart import Cart
from domain.models.customer import Customer
from domain.models.order import Order
from domain.models.product import Product
from domain.models.shipping import Shipping
from domain.money.money import Money

T = TypeVar("T")


@dataclass(frozen=True)
class PaymentCard:
    """Datos de tarjeta de prueba (sandbox) recibidos por la petición.

    El workflow nunca lee la tarjeta de datasets ni del entorno: la
    recibe ya resuelta dentro del SaleRequest.
    """

    number: str
    exp_month: str
    exp_year: str
    cvv: str

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "PaymentCard":
        fields = ("number", "exp_month", "exp_year", "cvv")
        missing = [name for name in fields if not record.get(name)]
        if missing:
            raise PreconditionError(
                f"PaymentCard incompleta; faltan campos: {missing}"
            )
        return cls(**{name: str(record[name]) for name in fields})


@dataclass(frozen=True)
class SaleRequest:
    """Entrada del flujo de venta de contado.

    `confirm_order=True` ejecuta 'Finalizar compra' y crea una orden
    real — reservado a E2E con autorización explícita (stage).
    """

    search_term: str
    customer: Customer
    address: Address
    shipping_method: str
    payment_method: str
    card: PaymentCard
    confirm_order: bool = False


@dataclass(frozen=True)
class SaleResult:
    """Salida del flujo con los modelos de dominio de cada etapa."""

    product: Product
    cart: Cart
    customer: Customer
    address: Address
    shipping: Shipping
    summary: dict[str, Money]
    payment_method: str
    order: Order | None


class SaleCashWorkflow:
    """Coordina la venta de contado completa sin absorber la UI."""

    def __init__(self, pages, context: ExecutionContext) -> None:
        self._pages = pages
        self._log = get_logger(
            __name__,
            run_id=context.run_id,
            case_id=context.case_id or "-",
            site=context.site,
            environment=context.environment,
        )

    def run(self, request: SaleRequest) -> SaleResult:
        product = self._stage("product", lambda: self._select_product(request))
        cart = self._stage("cart", self._open_cart_and_advance)
        checkout = self._stage("guest", self._enter_as_guest)
        customer, address = self._stage(
            "customer_address", lambda: self._register_customer(checkout, request)
        )
        shipping = self._stage(
            "shipping", lambda: self._select_shipping(checkout, request)
        )
        self._stage("payment", lambda: self._prepare_payment(request))
        summary = self._stage("summary", checkout.summary_totals)
        order = (
            self._stage("order", lambda: self._confirm_order(request))
            if request.confirm_order
            else None
        )
        self._log.info(
            "Venta de contado completada%s",
            f" — folio {order.folio}" if order else " (sin confirmar)",
        )
        return SaleResult(
            product=product,
            cart=cart,
            customer=customer,
            address=address,
            shipping=shipping,
            summary=summary,
            payment_method=request.payment_method,
            order=order,
        )

    def _stage(self, name: str, action: Callable[[], T]) -> T:
        self._log.info("Etapa '%s' — inicio", name)
        try:
            result = action()
        except Exception as exc:
            exc.add_note(f"SaleCashWorkflow: falló en la etapa '{name}'")
            self._log.error("Etapa '%s' — error: %s", name, exc)
            raise
        self._log.info("Etapa '%s' — ok", name)
        return result

    def _select_product(self, request: SaleRequest) -> Product:
        home = self._pages.home()
        home.open_home()
        home.accept_cookies_if_present()
        home.wait_until_ready()
        home.close_promo_if_present()

        search = self._pages.search()
        search.search(request.search_term)
        search.load_all_cards()
        card = search.eligible_card()
        if card is None:
            raise PreconditionError(
                f"Búsqueda '{request.search_term}' sin cards elegibles "
                "(nombre, precio e identificador visibles)."
            )
        card.open()

        product_page = self._pages.product()
        if not product_page.is_available() or not product_page.is_add_to_cart_enabled():
            raise PreconditionError(
                "La PDP abierta no está disponible para agregar al carrito."
            )
        product = product_page.read_product()
        product_page.add_to_cart()
        product_page.dismiss_post_add_overlays()
        return product

    def _open_cart_and_advance(self) -> Cart:
        cart_page = self._pages.cart()
        cart_page.open_cart()
        cart = cart_page.read_cart()
        if cart.is_empty:
            raise PreconditionError(
                "El carrito quedó vacío tras agregar el producto."
            )
        cart_page.continue_to_checkout()
        return cart

    def _enter_as_guest(self):
        checkout = self._pages.checkout()
        checkout.wait_for_guest_gate()
        if not checkout.is_guest_gate_visible():
            raise PreconditionError(
                "El gate 'Continuar como invitado' no se mostró."
            )
        checkout.continue_as_guest()
        checkout.wait_until_ready()
        return checkout

    def _register_customer(self, checkout, request: SaleRequest):
        checkout.fill_customer_form(request.customer, request.address)
        errors = checkout.validation_errors()
        if errors:
            raise PreconditionError(
                f"El formulario del comprador quedó con errores: {errors}"
            )
        checkout.wait_payment_stage_enabled()
        return checkout.read_customer(), checkout.read_address()

    def _select_shipping(self, checkout, request: SaleRequest) -> Shipping:
        checkout.select_delivery_method(request.shipping_method)
        shipping = checkout.shipping()
        checkout.wait_payment_stage_enabled()
        return shipping

    def _prepare_payment(self, request: SaleRequest) -> None:
        payment = self._pages.payment()
        payment.open_payment_stage()
        try:
            # select_method espera la habilitación asíncrona del radio (KO)
            # y falla si el método no es seleccionable para este carrito.
            payment.select_method(request.payment_method)
        except PaymentError as exc:
            raise PreconditionError(
                f"El método '{request.payment_method}' no es seleccionable "
                "para este carrito."
            ) from exc
        payment.fill_card(
            number=request.card.number,
            exp_month=request.card.exp_month,
            exp_year=request.card.exp_year,
            cvv=request.card.cvv,
        )
        errors = payment.validation_errors()
        if errors:
            raise PreconditionError(
                f"Errores de validación de pago: {errors}"
            )
        payment.wait_place_order_enabled()

    def _confirm_order(self, request: SaleRequest) -> Order:
        payment = self._pages.payment()
        payment.confirm_order()
        order_page = self._pages.order()
        order_page.wait_success()
        return order_page.read_order(payment_method=request.payment_method)
