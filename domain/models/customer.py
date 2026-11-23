"""Modelo de cliente."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Customer:
    name: str
    last_name: str
    email: str
    phone: str | None = None
