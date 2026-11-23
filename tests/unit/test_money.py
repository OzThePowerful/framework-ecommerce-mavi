"""Pruebas unitarias de Money: precisión decimal y normalización."""

from decimal import Decimal

import pytest

from domain.errors.business_error import BusinessError
from domain.money.money import Money

pytestmark = pytest.mark.unit


def test_suma_resta_y_multiplicacion():
    a = Money("11429.00")
    b = Money("571.00")
    assert (a + b).amount == Decimal("12000.00")
    assert (a - b).amount == Decimal("10858.00")
    assert (b * 2).amount == Decimal("1142.00")


def test_igualdad_y_orden():
    a = Money("100")
    b = Money("200")
    assert a == Money(Decimal("100"))
    assert a < b and a <= b and b > a and b >= a


def test_moneda_distinta_error_explicito():
    with pytest.raises(BusinessError):
        Money("1", "MXN") + Money("1", "USD")
    with pytest.raises(BusinessError):
        Money("1", "MXN") < Money("1", "USD")


def test_float_rechazado():
    with pytest.raises(BusinessError):
        Money(0.1)


def test_normalizacion_a_dos_decimales():
    assert Money("10.005").amount == Decimal("10.01")
    assert Money("10.004").amount == Decimal("10.00")
