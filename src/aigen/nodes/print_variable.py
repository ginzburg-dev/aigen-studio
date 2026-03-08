from typing import Any

from aigen.common.node import Node


class PrintVariableNode(Node):
    def __init__(self, params: dict[str, Any]) -> None:
        super().__init__("PrintVariable", params)

    def run(self, context: dict[str, Any]):
        input_var = self.params.get("input")
        if input_var is None:
            raise ValueError("Empty variable name.")
        if input_var not in context:
            raise ValueError("Variable name does not exist.")
        print(f"Variable Name: {input_var}\nData: {context[input_var]}")
