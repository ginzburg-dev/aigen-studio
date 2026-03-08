from abc import ABC, abstractmethod
from typing import Any

class Node(ABC):
    def __init__(self, name: str, params: dict[str, Any]) -> None:
        self._name: str = name
        self._params: dict[str, Any] = params

    @property
    def name(self) -> str:
        return self._name

    @property
    def params(self) -> dict[str, Any]:
        return self._params

    @abstractmethod
    def run(self, context: dict[str, Any]) -> None:
        ...
