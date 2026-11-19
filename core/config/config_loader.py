"""Punto único de carga de la configuración YAML del framework."""

from pathlib import Path

import yaml

from core.execution.execution_errors import ConfigError, UnknownProfileError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"


def _load_yaml(path: Path) -> dict:
    if not path.is_file():
        raise ConfigError(f"Archivo de configuración inexistente: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"YAML inválido en {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"El archivo {path} no contiene un mapeo YAML válido")
    return data


def load_sites() -> dict:
    return _load_yaml(CONFIG_DIR / "sites.yaml")


def load_environments() -> dict:
    return _load_yaml(CONFIG_DIR / "environments.yaml")


def load_execution_profile(name: str) -> dict:
    profiles = _load_yaml(CONFIG_DIR / "execution_profiles.yaml").get("profiles", {})
    profile = profiles.get(name)
    if profile is None:
        raise UnknownProfileError(
            f"Perfil '{name}' no existe. Disponibles: {sorted(profiles)}"
        )
    return profile


def load_logging_config() -> dict:
    return _load_yaml(CONFIG_DIR / "logging.yaml")
