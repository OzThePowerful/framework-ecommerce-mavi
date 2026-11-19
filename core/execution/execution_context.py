"""Contexto de ejecución inmutable compartido por todas las capas.

Las capas funcionales (pages, workflows, tests) reciben este contexto ya
construido; nunca resuelven URLs, ambientes ni sitios por su cuenta.
"""

from dataclasses import dataclass


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
