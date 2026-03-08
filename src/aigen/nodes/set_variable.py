from typing import Any

from aigen.common.node import Node

class SetVariableNode(Node):
    def __init__(self, name: str, value: str) -> None:
        super().__init__("SetVariable")
        self._name = name
        self._value = value
    
    def run(self, context: dict[str, Any]) -> None:
        if not self._name:
            raise ValueError("Incorrect name. Name cannot be empty.")
        context[self._name] = self._value
