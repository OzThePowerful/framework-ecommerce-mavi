"""Modelo de envío."""

from dataclasses import dataclass

from domain.money.money import Money


@dataclass(frozen=True)
class Shipping:
    method: str
    cost: Money
