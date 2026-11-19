"""Errores de negocio (independientes de la UI)."""


class BusinessError(Exception):
    """Regla de negocio violada o estado inconsistente."""
