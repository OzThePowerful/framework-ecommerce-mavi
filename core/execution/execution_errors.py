"""Taxonomía de errores técnicos del framework.

Política: los errores se clasifican; está prohibido `except Exception: pass`.
La evidencia conserva siempre la causa original (`raise ... from exc`).
"""


class FrameworkError(Exception):
    """Error base del Framework Ecommerce MAVI."""


class ConfigError(FrameworkError):
    """Configuración inválida o incompleta."""


class UnknownSiteError(ConfigError):
    """El sitio solicitado no existe en sites.yaml."""


class UnknownEnvironmentError(ConfigError):
    """El ambiente solicitado no existe para el sitio."""


class UnknownProfileError(ConfigError):
    """El perfil de ejecución no existe en execution_profiles.yaml."""


class NavigationError(FrameworkError):
    """Fallo de navegación o de espera de URL."""


class ElementStateError(FrameworkError):
    """El elemento no alcanzó el estado esperado."""


class DataError(FrameworkError):
    """Dataset inexistente, inválido o fuente de datos no disponible."""


class SiteEnvironmentError(FrameworkError):
    """El ambiente destino no permite la operación solicitada."""


class PaymentError(FrameworkError):
    """Error durante la etapa de pago."""
