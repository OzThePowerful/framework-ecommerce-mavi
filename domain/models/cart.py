"""Modelo de carrito."""

from dataclasses import dataclass, field
from decimal import Decimal

from domain.errors.precondition_error import PreconditionError
from domain.models.product import Product
from domain.models.shipping import Shipping
from domain.money.money import Money

ZERO = Money(Decimal("0"))


@dataclass(frozen=True)
class CartItem:
    product: Product
    quantity: int = 1
    unit_price: Money | None = None

    def __post_init__(self) -> None:
        if self.quantity < 1:
            raise PreconditionError("quantity debe ser >= 1")

    @property
    def effective_unit_price(self) -> Money:
        return self.unit_price or self.product.effective_price

    @property
    def subtotal(self) -> Money:
        return self.effective_unit_price * self.quantity


@dataclass
class Cart:
    items: list[CartItem] = field(default_factory=list)
    discount: Money = ZERO
    shipping: Shipping | None = None

    @property
    def is_empty(self) -> bool:
        return not self.items

    @property
    def subtotal(self) -> Money:
        total = ZERO
        for item in self.items:
            total = total + item.subtotal
        return total

    @property
    def shipping_cost(self) -> Money:
        return self.shipping.cost if self.shipping else ZERO

    @property
    def total(self) -> Money:
        return self.subtotal - self.discount + self.shipping_cost
