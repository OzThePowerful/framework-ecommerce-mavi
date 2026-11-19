"""Modelo de producto."""

from dataclasses import dataclass

from domain.money.money import Money


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    unit_price: Money
