"""Dinero con moneda explícita; prohibido floats para montos."""

from dataclasses import dataclass
from decimal import Decimal

from domain.errors.business_error import BusinessError


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "MXN"

    def __post_init__(self) -> None:
        object.__setattr__(self, "amount", Decimal(str(self.amount)))

    def _check(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise BusinessError(
                f"Monedas distintas: {self.currency} vs {other.currency}"
            )

    def __add__(self, other: "Money") -> "Money":
        self._check(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._check(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: int) -> "Money":
        return Money(self.amount * factor, self.currency)
