"""Fixtures de evidencia por ejecución."""

import pytest

from core.evidence.evidence_manager import EvidenceManager


@pytest.fixture
def evidence_manager(run_context) -> EvidenceManager:
    """EvidenceManager ligado al Run ID de la sesión."""
    return EvidenceManager(run_context.run_id)
