"""Modelo de orden."""

from dataclasses import dataclass, field

from domain.models.cart import CartItem
from domain.money.money import Money


@dataclass(frozen=True)
class Order:
    order_id: str
    items: list[CartItem] = field(default_factory=list)
    total: Money | None = None
    status: str = "created"
