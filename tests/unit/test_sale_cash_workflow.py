"""Pruebas contractuales del SaleCashWorkflow (EC-SP01-018-1).

Fakes de pages que registran la secuencia de llamadas: verifican que el
workflow coordina etapas, propaga precondiciones sin ocultarlas y que el
mismo flujo corre en ambas marcas sin `if site`.
"""

from decimal import Decimal

import pytest

from core.execution.execution_context import ExecutionContext
from core.execution.execution_errors import NavigationError, PaymentError
from domain.errors.precondition_error import PreconditionError
from domain.models.address import Address
from domain.models.cart import Cart, CartItem
from domain.models.customer import Customer
from domain.models.order import Order
from domain.models.product import Product
from domain.models.shipping import Shipping
from domain.money.money import Money
from workflows.common.sale_cash_workflow import (
    PaymentCard,
    SaleCashWorkflow,
    SaleRequest,
)

PRODUCT = Product(sku="SKU-1", name="Parrilla QA", unit_price=Money(Decimal("1000")))
CUSTOMER = Customer(name="QA", last_name="Automation", email="qa@test.dev")
ADDRESS = Address(street="Av. Pruebas", zip_code="44100", city="GDL", state="Jalisco")
CARD = PaymentCard(number="4111111111111111", exp_month="11", exp_year="30", cvv="123")
SHIPPING = Shipping(method="a_domicilio", cost=Money(Decimal("0")))
ORDER = Order(order_id="1", folio="2000000001", payment_method="openpay_cards")


def _cart_with_item() -> Cart:
    return Cart(items=[CartItem(product=PRODUCT, quantity=1)])


class FakeHome:
    def __init__(self, calls):
        self._c = calls

    def open_home(self):
        self._c.append("home.open")

    def accept_cookies_if_present(self):
        self._c.append("home.cookies")

    def wait_until_ready(self):
        self._c.append("home.ready")

    def close_promo_if_present(self):
        self._c.append("home.promo")


class FakeCard:
    def __init__(self, calls):
        self._c = calls

    def open(self):
        self._c.append("search.card.open")


class FakeSearch:
    def __init__(self, calls, eligible=True):
        self._c = calls
        self._eligible = eligible

    def search(self, term):
        self._c.append(f"search.search:{term}")

    def load_all_cards(self):
        self._c.append("search.load_all")
        return 5

    def eligible_cards(self, max_cards=4):
        self._c.append("search.eligible")
        return [FakeCard(self._c)] if self._eligible else []

    def back_to_results(self):
        self._c.append("search.back")


class FakeProduct:
    def __init__(self, calls, available=True):
        self._c = calls
        self._available = available

    def wait_until_ready(self):
        self._c.append("pdp.ready")

    def is_available(self):
        return self._available

    def is_add_to_cart_enabled(self):
        return self._available

    def read_product(self):
        self._c.append("pdp.read")
        return PRODUCT

    def add_to_cart(self):
        self._c.append("pdp.add_to_cart")

    def dismiss_post_add_overlays(self):
        self._c.append("pdp.dismiss")


class FakeCart:
    def __init__(self, calls, empty=False):
        self._c = calls
        self._empty = empty

    def open_cart(self):
        self._c.append("cart.open")

    def read_cart(self):
        self._c.append("cart.read")
        return Cart() if self._empty else _cart_with_item()

    def continue_to_checkout(self):
        self._c.append("cart.checkout")


class FakeCheckout:
    def __init__(self, calls, errors=None, gate_visible=True):
        self._c = calls
        self._errors = errors or []
        self._gate = gate_visible

    def wait_for_guest_gate(self):
        self._c.append("checkout.wait_gate")

    def is_guest_gate_visible(self):
        return self._gate

    def continue_as_guest(self):
        self._c.append("checkout.guest")

    def wait_until_ready(self):
        self._c.append("checkout.ready")

    def fill_customer_form(self, customer, address):
        self._c.append(f"checkout.fill:{customer.email}")

    def validation_errors(self):
        return list(self._errors)

    def wait_payment_stage_enabled(self):
        self._c.append("checkout.payment_enabled")

    def read_customer(self):
        self._c.append("checkout.read_customer")
        return CUSTOMER

    def read_address(self):
        self._c.append("checkout.read_address")
        return ADDRESS

    def select_delivery_method(self, method):
        self._c.append(f"checkout.delivery:{method}")

    def shipping(self):
        self._c.append("checkout.shipping")
        return SHIPPING

    def summary_totals(self):
        self._c.append("checkout.summary")
        return {
            "subtotal": Money(Decimal("1000")),
            "discount": Money(Decimal("0")),
            "shipping": Money(Decimal("0")),
            "total": Money(Decimal("1000")),
        }


class FakePayment:
    def __init__(self, calls, selectable=True, errors=None):
        self._c = calls
        self._selectable = selectable
        self._errors = errors or []

    def open_payment_stage(self):
        self._c.append("payment.open")

    def is_method_selectable(self, method):
        self._c.append(f"payment.selectable:{method}")
        return self._selectable

    def select_method(self, method):
        # Contrato real: falla con PaymentError si el método no es
        # seleccionable tras esperar la habilitación del radio.
        if not self._selectable:
            raise PaymentError(f"método '{method}' no seleccionable")
        self._c.append(f"payment.select:{method}")

    def fill_card(self, number, exp_month, exp_year, cvv):
        self._c.append(f"payment.fill_card:{number[-4:]}")

    def validation_errors(self):
        return list(self._errors)

    def wait_place_order_enabled(self):
        self._c.append("payment.place_order_ready")

    def confirm_order(self):
        self._c.append("payment.confirm")


class FakeOrder:
    def __init__(self, calls):
        self._c = calls

    def wait_success(self):
        self._c.append("order.wait_success")

    def read_order(self, payment_method=None):
        self._c.append("order.read")
        return ORDER


class FakePages:
    """PageFactory falso con inyección de comportamientos."""

    def __init__(self, calls, **overrides):
        self._fakes = {
            "home": FakeHome(calls),
            "search": FakeSearch(calls),
            "product": FakeProduct(calls),
            "cart": FakeCart(calls),
            "checkout": FakeCheckout(calls),
            "payment": FakePayment(calls),
            "order": FakeOrder(calls),
        }
        self._fakes.update(overrides)

    def __getattr__(self, name):
        fake = self._fakes.get(name)
        if fake is None:
            raise AttributeError(name)
        return lambda: fake


def _context(site: str) -> ExecutionContext:
    return ExecutionContext.build(
        site, "stage", "default", "CP_EC_XX_E2E_001", "run-test"
    )


def _request(confirm: bool = False) -> SaleRequest:
    return SaleRequest(
        search_term="parrilla",
        customer=CUSTOMER,
        address=ADDRESS,
        shipping_method="a_domicilio",
        payment_method="openpay_cards",
        card=CARD,
        confirm_order=confirm,
    )


def _run(site, confirm=False, **overrides):
    calls = []
    workflow = SaleCashWorkflow(FakePages(calls, **overrides), _context(site))
    return workflow.run(_request(confirm)), calls


def test_coordina_las_etapas_en_orden():
    _, calls = _run("muebles_america")
    sequence = [
        "home.open",
        "search.search:parrilla",
        "pdp.add_to_cart",
        "cart.open",
        "cart.checkout",
        "checkout.guest",
        "checkout.fill:qa@test.dev",
        "checkout.delivery:a_domicilio",
        "payment.select:openpay_cards",
        "payment.place_order_ready",
        "checkout.summary",
    ]
    positions = [calls.index(c) for c in sequence]
    assert positions == sorted(positions), f"Orden incorrecto: {calls}"


def test_result_expone_los_modelos_de_cada_etapa():
    result, _ = _run("viu")
    assert result.product == PRODUCT
    assert result.cart.items[0].product.sku == "SKU-1"
    assert result.customer == CUSTOMER
    assert result.address == ADDRESS
    assert result.shipping == SHIPPING
    assert result.summary["total"] == Money(Decimal("1000"))
    assert result.payment_method == "openpay_cards"
    assert result.order is None


def test_no_confirma_la_orden_por_defecto():
    _, calls = _run("muebles_america")
    assert "payment.confirm" not in calls
    assert "order.read" not in calls


def test_confirm_order_crea_y_lee_la_orden():
    result, calls = _run("viu", confirm=True)
    assert "payment.confirm" in calls
    assert calls.index("payment.confirm") < calls.index("order.wait_success")
    assert result.order == ORDER


def test_sin_card_elegible_falla_como_precondicion():
    calls = []
    pages = FakePages(calls, search=FakeSearch(calls, eligible=False))
    workflow = SaleCashWorkflow(pages, _context("muebles_america"))
    with pytest.raises(PreconditionError, match="cards elegibles"):
        workflow.run(_request())
    assert "cart.open" not in calls


def test_pdp_no_disponible_falla_como_precondicion():
    calls = []
    pages = FakePages(calls, product=FakeProduct(calls, available=False))
    workflow = SaleCashWorkflow(pages, _context("muebles_america"))
    with pytest.raises(PreconditionError, match="PDP comprable"):
        workflow.run(_request())
    assert "pdp.add_to_cart" not in calls


def test_metodo_pago_no_seleccionable_falla_como_precondicion():
    calls = []
    pages = FakePages(calls, payment=FakePayment(calls, selectable=False))
    workflow = SaleCashWorkflow(pages, _context("viu"))
    with pytest.raises(PreconditionError, match="no es seleccionable"):
        workflow.run(_request())
    assert "payment.select:openpay_cards" not in calls


def test_errores_del_formulario_fallan_como_precondicion():
    calls = []
    pages = FakePages(calls, checkout=FakeCheckout(calls, errors=["CP inválido"]))
    workflow = SaleCashWorkflow(pages, _context("muebles_america"))
    with pytest.raises(PreconditionError, match="CP inválido"):
        workflow.run(_request())


def test_error_de_etapa_propaga_sin_ocultarse():
    class BrokenHome(FakeHome):
        def open_home(self):
            raise NavigationError("timeout en home")

    calls = []
    pages = FakePages(calls, home=BrokenHome(calls))
    workflow = SaleCashWorkflow(pages, _context("viu"))
    with pytest.raises(NavigationError) as excinfo:
        workflow.run(_request())
    assert "etapa 'product'" in str(excinfo.value.__notes__)


def test_el_mismo_flujo_cubre_ambas_marcas_sin_if_site():
    _, calls_ma = _run("muebles_america")
    _, calls_viu = _run("viu")
    assert calls_ma == calls_viu


def test_payment_card_desde_registro_valida_campos():
    card = PaymentCard.from_record(
        {"number": "4242", "exp_month": "12", "exp_year": "30", "cvv": "999"}
    )
    assert card.number == "4242"
    with pytest.raises(PreconditionError, match="exp_year"):
        PaymentCard.from_record({"number": "1", "exp_month": "1", "cvv": "1"})
