"""Selector de ejecución por Case ID (EC-SP01-020).

Resolución: Case ID → ecommerce → feature → scenario → ejecución.
`--case-id CP_EC_<CODE>_<MODULO>_<NNN>` deriva el sitio desde el código
de marca, valida el ID contra el catálogo oficial (`plane_catalog.yaml`)
y nunca redirige silenciosamente: formato inválido, ID inexistente o
conflicto con --site/MAVI_ECOM_SITE explícito fallan con ConfigError.
"""

import difflib
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from core.config.config_loader import PROJECT_ROOT, load_sites
from core.execution.execution_errors import ConfigError

_CATALOG_PATH = PROJECT_ROOT / "test_cases" / "plane_catalog.yaml"
_CASE_ID_RE = re.compile(r"^CP_EC_([A-Z]+)_([A-Z0-9]+_\d{3})$")


@dataclass(frozen=True)
class CaseSelection:
    """Un Case ID validado: su marca y el sitio del que depende."""

    case_id: str
    site: str
    site_code: str


def _site_by_code(sites: dict | None = None) -> dict[str, str]:
    """Mapa código de marca → site key ('MA' → 'muebles_america')."""
    catalog = (sites or load_sites()).get("sites", {})
    return {
        entry["code"]: key
        for key, entry in catalog.items()
        if entry.get("code")
    }


def catalog_case_ids(path: Path = _CATALOG_PATH) -> frozenset[str]:
    """IDs declarados en el catálogo oficial (fuente de verdad)."""
    if not path.exists():
        raise ConfigError(
            f"Catálogo de casos no encontrado: {path}. "
            "Regenerarlo con scripts/build_plane_catalog.py."
        )
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return frozenset(c["id"] for c in data.get("casos", []))


def parse_case_id(
    raw: str, sites: dict | None = None, catalog: frozenset[str] | None = None
) -> CaseSelection:
    """Valida un Case ID y resuelve el sitio del que depende.

    Falla explícitamente con ConfigError si el formato no cumple
    `CP_EC_<CODE>_<MODULO>_<NNN>`, si el código no existe en sites.yaml
    o si el ID no está en el catálogo oficial.
    """
    case_id = (raw or "").strip()
    match = _CASE_ID_RE.match(case_id)
    if not match:
        raise ConfigError(
            f"Case ID inválido: {raw!r}. "
            "Formato esperado: CP_EC_<MA|VIU>_<MODULO>_<NNN> "
            "(ej. CP_EC_MA_CART_001)."
        )
    code = match.group(1)
    by_code = _site_by_code(sites)
    site = by_code.get(code)
    if site is None:
        raise ConfigError(
            f"El código de marca '{code}' no existe en sites.yaml "
            f"(disponibles: {sorted(by_code)})."
        )
    known = catalog if catalog is not None else catalog_case_ids()
    if case_id not in known:
        close = difflib.get_close_matches(case_id, sorted(known), n=3)
        hint = f" ¿Quisiste decir: {', '.join(close)}?" if close else ""
        raise ConfigError(
            f"Case ID inexistente en el catálogo: {case_id!r}.{hint}"
        )
    return CaseSelection(case_id=case_id, site=site, site_code=code)


def resolve_run_site(
    case_id: str | None,
    site_option: str,
    site_env: str | None,
    site_option_explicit: bool,
    sites: dict | None = None,
) -> str:
    """Sitio efectivo de la corrida considerando el Case ID.

    Sin Case ID: gana MAVI_ECOM_SITE > --site (comportamiento previo).
    Con Case ID: el sitio se deriva del ID; un --site o MAVI_ECOM_SITE
    explícito que contradiga la marca del ID es error explícito.
    """
    if not case_id:
        return site_env or site_option
    selection = parse_case_id(case_id, sites=sites)
    explicit = site_env or (site_option if site_option_explicit else None)
    if explicit and explicit != selection.site:
        raise ConfigError(
            f"Conflicto: --case-id {selection.case_id} pertenece a "
            f"'{selection.site}', pero el sitio explícito es '{explicit}'."
        )
    return selection.site
