"""Dinero con moneda explícita; prohibido floats para montos."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from domain.errors.business_error import BusinessError

CENT = Decimal("0.01")


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "MXN"

    def __post_init__(self) -> None:
        if isinstance(self.amount, float):
            raise BusinessError(
                "Money no acepta float; usa Decimal o str."
            )
        amount = Decimal(str(self.amount)).quantize(
            CENT, rounding=ROUND_HALF_UP
        )
        object.__setattr__(self, "amount", amount)

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

    def __lt__(self, other: "Money") -> bool:
        self._check(other)
        return self.amount < other.amount

    def __le__(self, other: "Money") -> bool:
        self._check(other)
        return self.amount <= other.amount

    def __ge__(self, other: "Money") -> bool:
        self._check(other)
        return self.amount >= other.amount

    def __gt__(self, other: "Money") -> bool:
        self._check(other)
        return self.amount > other.amount
