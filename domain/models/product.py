"""Modelo de producto."""

from dataclasses import dataclass

from domain.money.money import Money


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    unit_price: Money
    product_id: str | None = None
    promotional_price: Money | None = None
    availability: bool = True

    @property
    def effective_price(self) -> Money:
        return self.promotional_price or self.unit_price
