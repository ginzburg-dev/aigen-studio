from typing import Any

from aigen.common.node import Node

class SetVariableNode(Node):
    def __init__(self, params: dict[str, Any]) -> None:
        super().__init__("SetVariable", params)

    def run(self, context: dict[str, Any]) -> None:
        params = self.format_params(context)
        name = params.get("name")
        value = params.get("value", "")
        if not name:
            raise ValueError("Incorrect name. Name cannot be empty.")
        context[name] = value
