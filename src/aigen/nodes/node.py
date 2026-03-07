from abc import ABC, abstractmethod
from typing import Any

class Node(ABC):
    def __init__(self, name: str, **params) -> None:
        self.name: str = name
        self.params: dict[str, Any] = params

    @abstractmethod
    def run(self, context: dict[str, Any]) -> None:
        ...
