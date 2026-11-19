"""Modelo de carrito."""

from dataclasses import dataclass, field
from decimal import Decimal

from domain.models.product import Product
from domain.money.money import Money


@dataclass(frozen=True)
class CartItem:
    product: Product
    quantity: int = 1

    @property
    def subtotal(self) -> Money:
        return self.product.unit_price * self.quantity


@dataclass
class Cart:
    items: list[CartItem] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not self.items

    def total(self) -> Money:
        total = Money(Decimal("0"))
        for item in self.items:
            total = total + item.subtotal
        return total
