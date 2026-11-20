"""Contexto de ejecución inmutable compartido por todas las capas.

Las capas funcionales (pages, workflows, tests) reciben este contexto ya
construido; nunca resuelven URLs, ambientes ni sitios por su cuenta.
"""

from dataclasses import dataclass

from core.config.config_loader import load_execution_profile
from core.config.site_config import resolve_site


@dataclass(frozen=True)
class ExecutionContext:
    project: str
    site: str
    site_code: str
    environment: str
    base_url: str
    checkout_url_pattern: str
    browser: str
    headless: bool
    case_id: str | None
    run_id: str
    navigation_timeout: int
    action_timeout: int
    expect_timeout: int

    @classmethod
    def build(
        cls,
        site: str,
        environment: str,
        profile_name: str,
        case_id: str | None,
        run_id: str,
    ) -> "ExecutionContext":
        """Construye el contexto resolviendo perfil y sitio desde config/.

        Punto único de construcción: la misma resolución aplica para la
        fixture de pytest y para cualquier consumidor futuro (Bridge, CLI).
        """
        profile = load_execution_profile(profile_name)
        site_config = resolve_site(site, environment)
        return cls(
            project="ecommerce",
            site=site_config.site,
            site_code=site_config.code,
            environment=site_config.environment,
            base_url=site_config.base_url,
            checkout_url_pattern=site_config.checkout_url_pattern,
            browser=profile["browser"],
            headless=bool(profile["headless"]),
            case_id=case_id,
            run_id=run_id,
            navigation_timeout=int(profile["navigation_timeout_ms"]),
            action_timeout=int(profile["action_timeout_ms"]),
            expect_timeout=int(profile["expect_timeout_ms"]),
        )
