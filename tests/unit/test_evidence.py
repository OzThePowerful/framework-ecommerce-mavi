"""Evidencia ante fallo: estructura por caso, captura y manifest."""

import json
from pathlib import Path

import pytest

from core.evidence.artifact_paths import case_artifacts_dir, run_artifacts_dir
from core.evidence.evidence_manager import EvidenceManager

pytestmark = pytest.mark.unit


class _FailedReport:
    """Reporte de fallo mínimo equivalente al de pytest."""

    when = "call"
    failed = True
    longrepr = "AssertionError: fallo controlado"


def test_estructura_case_dir(run_context):
    base = case_artifacts_dir(run_context.run_id, "CP_EC_QA_001")
    assert base.parent == run_artifacts_dir(run_context.run_id)
    for subdir in ("screenshots", "logs", "traces", "videos"):
        assert (base / subdir).is_dir()


def test_sanitiza_case_id_para_filesystem():
    base = case_artifacts_dir("run1", "CP::param[1]")
    assert base.name == "CP_param_1_"


def test_sin_colision_entre_ejecuciones():
    paths = {
        case_artifacts_dir("run_a", "CP"),
        case_artifacts_dir("run_b", "CP"),
        case_artifacts_dir("run_a", "CP2"),
    }
    assert len(paths) == 3


def test_captura_fallo_genera_evidencia(page, run_context, execution_context):
    """Fallo controlado: screenshot, URL, excepción y manifest."""
    page.goto("about:blank")
    manager = EvidenceManager(run_context.run_id, "CP_EC_QA_FAIL")

    artifacts = manager.capture_failure(
        page, _FailedReport(), execution_context, "test_fallo_controlado"
    )

    screenshot = Path(artifacts["screenshot"])
    assert screenshot.is_file() and screenshot.stat().st_size > 0
    assert screenshot.parent.name == "screenshots"

    base = manager.base_dir
    assert (base / "logs" / "current_url.txt").read_text(
        encoding="utf-8"
    ) == "about:blank"
    assert "fallo controlado" in (
        base / "logs" / "exception.txt"
    ).read_text(encoding="utf-8")

    manifest = json.loads((base / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["run_id"] == run_context.run_id
    assert manifest["case_id"] == "CP_EC_QA_FAIL"
    assert manifest["outcome"] == "failed"
    assert manifest["site"] == execution_context.site
    assert manifest["environment"] == execution_context.environment
    assert manifest["browser"] == execution_context.browser
    assert manifest["page_url"] == "about:blank"
    assert "fallo controlado" in manifest["exception"]
    assert manifest["artifacts"]
