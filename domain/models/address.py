"""Modelo de dirección de envío."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Address:
    street: str
    city: str
    state: str
    zip_code: str
    exterior_number: str | None = None
    interior_number: str | None = None
    neighborhood: str | None = None
    references: str | None = None
    country: str = "MX"
