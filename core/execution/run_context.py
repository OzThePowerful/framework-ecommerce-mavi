"""Identidad de la ejecución: un RunContext por sesión de pytest."""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from core.evidence.artifact_paths import run_artifacts_dir


def new_run_id() -> str:
    """Genera un Run ID único por ejecución."""
    return uuid.uuid4().hex[:12]


@dataclass
class RunContext:
    run_id: str = field(default_factory=new_run_id)
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def artifacts_dir(self) -> Path:
        return run_artifacts_dir(self.run_id)
