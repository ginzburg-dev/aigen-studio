from typing import Any

import structlog

from aigen.common.node import Node
from aigen.common.node_registry import register_node

LOGGER = structlog.get_logger(__name__)
BLUE = "\033[94m"
PURPLE = "\033[35m"
RESET = "\033[0m"


@register_node("PrintVariable")
class PrintVariableNode(Node):
    def __init__(self, params: dict[str, Any]) -> None:
        super().__init__(params)

    def run(self, context: dict[str, Any]):
        params = self.format_params(context)
        input_var = params.get("input")
        if input_var is None:
            raise ValueError("Empty variable name.")
        if input_var not in context:
            raise ValueError("Variable name does not exist.")
        print(
            f"Print variable: {BLUE}{input_var}{RESET}={PURPLE}{context[input_var]}{RESET}"
        )
