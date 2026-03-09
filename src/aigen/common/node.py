from abc import ABC, abstractmethod
from typing import Any

from aigen.common.utils import replace_vars


class Node(ABC):
    def __init__(self, name: str, params: dict[str, Any]) -> None:
        self._name: str = name
        self._params: dict[str, Any] = params.copy()
        
    @property
    def name(self) -> str:
        return self._name

    @property
    def params(self) -> dict[str, Any]:
        return self._params

    def format_params(self, context: dict[str, Any]) -> dict[str, Any]:
        return {
            key: self._format_value(value, context)
            for key, value in self._params.items()
        }

    def _format_value(self, value: Any, context: dict[str, Any]) -> Any:
        if isinstance(value, str):
            return replace_vars(value, context)
        if isinstance(value, list):
            return [self._format_value(item, context) for item in value]
        if isinstance(value, dict):
            return {
                key: self._format_value(item, context)
                for key, item in value.items()
            }
        return value

    @abstractmethod
    def run(self, context: dict[str, Any]) -> None: ...
