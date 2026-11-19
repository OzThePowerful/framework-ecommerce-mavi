"""Workflow de venta de contado (coordinación de pages; sin locators).

El flujo completo de venta se implementará en una tarea posterior;
EC-SP01-001 solo deja preparada la capa.
"""

from core.execution.execution_errors import FrameworkError


class SaleCashWorkflow:
    """Coordinará Home → Listing → PDP → Cart → Checkout → Payment → Order."""

    def __init__(self, pages) -> None:
        self._pages = pages

    def execute(self) -> None:
        raise FrameworkError(
            "SaleCashWorkflow aún no implementado (fuera del alcance EC-SP01-001)."
        )
