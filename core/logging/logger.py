"""Logging estructurado con contexto de ejecución.

Todo log puede asociarse a run_id, case_id, site y environment cuando esa
información esté disponible. `print` está prohibido como diagnóstico.
"""

import logging
import logging.config

from core.config.config_loader import load_logging_config
from core.execution.execution_errors import ConfigError

_CONTEXT_FIELDS = ("run_id", "case_id", "site", "environment", "browser")
_DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s %(message)s"


class _ContextDefaultsFilter(logging.Filter):
    """Garantiza los campos de contexto aunque el record no los traiga."""

    def filter(self, record: logging.LogRecord) -> bool:
        for field_name in _CONTEXT_FIELDS:
            if not hasattr(record, field_name):
                setattr(record, field_name, "-")
        return True


def configure_logging() -> None:
    """Aplica config/logging.yaml o una configuración básica de respaldo."""
    try:
        config = load_logging_config()
    except ConfigError:
        config = None
    if config:
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=logging.INFO, format=_DEFAULT_FORMAT)
    context_filter = _ContextDefaultsFilter()
    for handler in logging.root.handlers:
        handler.addFilter(context_filter)


def get_logger(name: str, **context: str) -> logging.LoggerAdapter:
    """Logger con campos de contexto (run_id, site, environment, case_id)."""
    return logging.LoggerAdapter(logging.getLogger(name), extra=dict(context))
