"""Alias de compatibilidad: la implementación vive en workflows/common.

El GuestCheckoutWorkflow es multi-ecommerce desde que VIU expone el
menú de departamentos (EC-SP01-019); se mantiene este módulo para no
romper imports históricos del namespace MA.
"""

from workflows.common.guest_checkout_workflow import (  # noqa: F401
    GuestCheckoutRequest,
    GuestCheckoutWorkflow,
)
