"""Pruebas unitarias del RunContext / Run ID."""

import pytest

from core.evidence import artifact_paths
from core.execution.run_context import RunContext, new_run_id

pytestmark = pytest.mark.unit


def test_run_id_unico():
    ids = {new_run_id() for _ in range(50)}
    assert len(ids) == 50


def test_artifacts_dir_por_run(tmp_path, monkeypatch):
    monkeypatch.setattr(artifact_paths, "ARTIFACTS_DIR", tmp_path)
    context = RunContext(run_id="abc123")
    assert context.artifacts_dir == tmp_path / "runs" / "abc123"
    assert context.artifacts_dir.is_dir()
