from typing import Any

from aigen.common.node import Node
from aigen.common.node_registry import register_node

import structlog

LOGGER = structlog.get_logger(__name__)


@register_node("CopyVariable")
class CopyVariableNode(Node):
    def __init__(self, params: dict[str, Any]) -> None:
        super().__init__(params)

    def run(self, context: dict[str, Any]) -> None:
        params = self.format_params(context)
        source = params.get("input")
        target = params.get("output")

        if not source:
            raise ValueError("Input variable name cannot be empty.")
        if not target:
            raise ValueError("Output variable name cannot be empty.")
        if source not in context:
            raise ValueError(f"Input variable '{source}' does not exist in context.")

        context[target] = context[source]
        LOGGER.info(f"Copied variable '{source}' to '{target}'")
