"""Alias de compatibilidad: la implementación vive en workflows/common.

El SaleCashWorkflow es multi-ecommerce (EC-SP01-018-1); se mantiene
este módulo para no romper imports históricos del namespace MA.
"""

from workflows.common.sale_cash_workflow import (  # noqa: F401
    PaymentCard,
    SaleCashWorkflow,
    SaleRequest,
    SaleResult,
)
