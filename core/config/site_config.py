"""Resolución única de sitio + ambiente desde sites.yaml / environments.yaml."""

from dataclasses import dataclass

from core.config.config_loader import load_environments, load_sites
from core.execution.execution_errors import (
    ConfigError,
    UnknownEnvironmentError,
    UnknownSiteError,
)


@dataclass(frozen=True)
class SiteConfig:
    site: str
    code: str
    environment: str
    base_url: str
    checkout_url_pattern: str


def resolve_site(
    site: str,
    environment: str,
    sites: dict | None = None,
    environments: dict | None = None,
) -> SiteConfig:
    """Resuelve el SiteConfig o lanza error explícito.

    Validación en dos niveles: el ambiente debe estar declarado en
    environments.yaml y además existir para el sitio en sites.yaml.
    Nunca redirige silenciosamente a otro ambiente ni aplica defaults
    peligrosos: combinaciones desconocidas siempre fallan.
    """
    catalog = (sites or load_sites()).get("sites", {})
    entry = catalog.get(site)
    if entry is None:
        raise UnknownSiteError(
            f"Sitio '{site}' no soportado. Disponibles: {sorted(catalog)}"
        )
    code = entry.get("code")
    if not code:
        raise ConfigError(f"El sitio '{site}' no define 'code' en sites.yaml")
    declared = (environments or load_environments()).get("environments", {})
    if environment not in declared:
        raise UnknownEnvironmentError(
            f"Ambiente '{environment}' no declarado en environments.yaml. "
            f"Declarados: {sorted(declared)}"
        )
    site_environments = entry.get("environments", {})
    env_config = site_environments.get(environment)
    if env_config is None:
        raise UnknownEnvironmentError(
            f"Ambiente '{environment}' no existe para '{site}'. "
            f"Disponibles: {sorted(site_environments)}"
        )
    base_url = env_config.get("base_url")
    if not base_url:
        raise ConfigError(f"'{site}/{environment}' no define base_url")
    return SiteConfig(
        site=site,
        code=code,
        environment=environment,
        base_url=base_url,
        checkout_url_pattern=env_config.get("checkout_url_pattern", "**/checkout/**"),
    )
