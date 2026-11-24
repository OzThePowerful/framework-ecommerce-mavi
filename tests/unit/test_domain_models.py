"""Pruebas unitarias de los modelos de dominio.

MA y VIU deben producir los mismos tipos aunque su DOM difiera:
las pruebas parametrizadas por sitio construyen Customer/Address
desde los datasets reales consumidos vía DataProvider.
"""

from decimal import Decimal

import pytest

from data_providers.yaml_data_provider import YamlDataProvider
from domain.errors.precondition_error import PreconditionError
from domain.models.address import Address
from domain.models.cart import Cart, CartItem
from domain.models.customer import Customer
from domain.models.order import Order
from domain.models.product import Product
from domain.models.shipping import Shipping
from domain.money.money import Money

pytestmark = pytest.mark.unit

SITES = ("muebles_america", "viu")


def _product(price: str = "100", promo: str | None = None) -> Product:
    return Product(
        sku="SKU-1",
        name="Producto QA",
        unit_price=Money(price),
        promotional_price=Money(promo) if promo else None,
    )


def test_product_effective_price():
    assert _product().effective_price.amount == Decimal("100.00")
    assert _product(promo="80").effective_price.amount == Decimal("80.00")


def test_cartitem_subtotal_y_validacion():
    item = CartItem(product=_product("50"), quantity=3)
    assert item.subtotal.amount == Decimal("150.00")
    with pytest.raises(PreconditionError):
        CartItem(product=_product(), quantity=0)


def test_cartitem_precio_snapshot():
    item = CartItem(product=_product("100", promo="80"), quantity=1,
                    unit_price=Money("70"))
    assert item.subtotal.amount == Decimal("70.00")


def test_cart_totales():
    cart = Cart(
        items=[
            CartItem(product=_product("100"), quantity=2),
            CartItem(product=_product("50"), quantity=1),
        ],
        discount=Money("30"),
        shipping=Shipping(method="estandar", cost=Money("99")),
    )
    assert not cart.is_empty
    assert cart.subtotal.amount == Decimal("250.00")
    # 250 - 30 + 99
    assert cart.total.amount == Decimal("319.00")


def test_order_campos_minimos():
    order = Order(
        order_id="QA-1",
        items=[CartItem(product=_product("10"), quantity=1)],
        subtotal=Money("10"),
        shipping=Shipping(method="recoge", cost=Money("0")),
        total=Money("10"),
        payment_method="tarjeta",
    )
    assert order.status == "created"
    assert order.payment_method == "tarjeta"


@pytest.mark.parametrize("site", SITES)
def test_customer_desde_env(site, monkeypatch):
    """La identidad del comprador resuelve desde MAVI_GUEST_<SITIO>_*
    (.env/entorno), nunca de un dataset versionado."""
    from data_providers.customer_provider import resolve_guest_customer

    key = {"muebles_america": "MA", "viu": "VIU"}[site]
    prefix = f"MAVI_GUEST_{key}_"
    monkeypatch.setenv(f"{prefix}FIRST_NAME", "QA")
    monkeypatch.setenv(f"{prefix}LAST_NAME", "Automation")
    monkeypatch.setenv(f"{prefix}MOTHERS_NAME", "Team")
    monkeypatch.setenv(f"{prefix}EMAIL", "qa@equipo.test")
    monkeypatch.setenv(f"{prefix}PHONE", "3300000000")

    customer = resolve_guest_customer(site)
    assert isinstance(customer, Customer)
    assert customer.email == "qa@equipo.test"
    assert customer.mothers_name == "Team"


def test_customer_env_incompleto_error_explicito(monkeypatch):
    """Sin las variables requeridas el resolver falla con ConfigError."""
    from core.execution.execution_errors import ConfigError
    from data_providers.customer_provider import resolve_guest_customer

    for var in (
        "MAVI_GUEST_MA_FIRST_NAME",
        "MAVI_GUEST_MA_LAST_NAME",
        "MAVI_GUEST_MA_EMAIL",
        "MAVI_GUEST_MA_PHONE",
    ):
        monkeypatch.delenv(var, raising=False)
    with pytest.raises(ConfigError):
        resolve_guest_customer("muebles_america")


@pytest.mark.parametrize("site", SITES)
def test_address_desde_dataset(site):
    record = YamlDataProvider(site).get_record("addresses", "guadalajara")
    address = Address(
        street=record["street"],
        exterior_number=record.get("exterior_number"),
        neighborhood=record.get("neighborhood"),
        zip_code=record["zip_code"],
        city=record["city"],
        state=record["state"],
    )
    assert isinstance(address, Address)
    assert address.country == "MX"
