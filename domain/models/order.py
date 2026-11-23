"""Modelo de orden."""

from dataclasses import dataclass, field

from domain.models.cart import CartItem
from domain.models.shipping import Shipping
from domain.money.money import Money


@dataclass(frozen=True)
class Order:
    order_id: str
    items: list[CartItem] = field(default_factory=list)
    subtotal: Money | None = None
    discount: Money | None = None
    shipping: Shipping | None = None
    total: Money | None = None
    payment_method: str | None = None
    status: str = "created"
