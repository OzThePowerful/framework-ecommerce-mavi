"""Gestión de evidencias de ejecución (screenshots, logs, manifest)."""

import json
from datetime import UTC, datetime
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError

from core.evidence.artifact_paths import case_artifacts_dir


class EvidenceManager:
    """Persiste evidencias bajo artifacts/runs/<run_id>/<case_id>/."""

    def __init__(self, run_id: str, case_id: str) -> None:
        self.run_id = run_id
        self.case_id = case_id
        self._base = case_artifacts_dir(run_id, case_id)

    @property
    def base_dir(self) -> Path:
        return self._base

    def save_screenshot(self, page, name: str, mask: list | None = None) -> Path:
        """Screenshot full-page; `mask` (locators de Playwright) tapa datos
        privados en la imagen. Sin `mask` el comportamiento no cambia."""
        path = self._base / "screenshots" / f"{name}.png"
        if mask:
            page.screenshot(path=str(path), full_page=True, mask=mask)
        else:
            page.screenshot(path=str(path), full_page=True)
        return path

    def save_log(self, name: str, content: str) -> Path:
        path = self._base / "logs" / f"{name}.txt"
        path.write_text(content, encoding="utf-8")
        return path

    def write_manifest(self, payload: dict) -> Path:
        path = self._base / "manifest.json"
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        return path

    def capture_failure(self, page, report, context, test_name: str) -> dict:
        """Captura el contexto de diagnóstico ante un fallo de test.

        Escribe: screenshot full-page, current_url.txt, exception.txt
        (longrepr original) y manifest.json. Devuelve las rutas para que
        el llamador pueda adjuntarlas a Allure.
        """
        artifacts: dict[str, Path | None] = {
            "screenshot": None,
            "url_log": None,
            "exception_log": None,
            "manifest": None,
        }
        try:
            current_url = page.url
        except PlaywrightError:
            current_url = "unavailable"
        try:
            artifacts["screenshot"] = self.save_screenshot(page, "failure")
        except PlaywrightError:
            pass
        artifacts["url_log"] = self.save_log("current_url", current_url)
        artifacts["exception_log"] = self.save_log(
            "exception", str(report.longrepr)
        )
        artifacts["manifest"] = self.write_manifest(
            {
                "run_id": self.run_id,
                "case_id": self.case_id,
                "test": test_name,
                "outcome": "failed",
                "site": context.site,
                "environment": context.environment,
                "browser": context.browser,
                "base_url": context.base_url,
                "page_url": current_url,
                "exception": str(report.longrepr),
                "captured_at": datetime.now(UTC).isoformat(),
                "artifacts": {
                    key: str(value) for key, value in artifacts.items() if value
                },
            }
        )
        return artifacts
