"""Contrato de proveedores de datos (YAML hoy, Excel mañana)."""

from abc import ABC, abstractmethod
from typing import Any


class BaseDataProvider(ABC):
    """Interfaz única; los consumidores no conocen rutas ni formatos."""

    @abstractmethod
    def get_dataset(self, name: str) -> Any:
        """Devuelve el dataset completo por nombre lógico."""

    @abstractmethod
    def get_record(self, dataset: str, key: str) -> Any:
        """Devuelve un registro concreto dentro del dataset."""
