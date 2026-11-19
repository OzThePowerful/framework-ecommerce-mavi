"""Precondiciones de negocio no cumplidas."""

from domain.errors.business_error import BusinessError


class PreconditionError(BusinessError):
    """La operación no puede ejecutarse por una precondición funcional."""
