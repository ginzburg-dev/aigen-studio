from typing import Any

from aigen.common.node import Node

import structlog

LOGGER = structlog.get_logger(__name__)


class CopyVariableNode(Node):
    def __init__(self, params: dict[str, Any]) -> None:
        super().__init__("Copy", params)

    def run(self, context: dict[str, Any]) -> None:
        input = self.params.get("input")
        output = self.params.get("output")

        if not input:
            raise ValueError("Input variable name cannot be empty.")
        if not output:
            raise ValueError("Output variable name cannot be empty.")
        if input not in context:
            raise ValueError(f"Input variable '{input}' does not exist in context.")

        context[output] = context[input]
        LOGGER.info(f"Copied variable '{input}' to '{output}'")
