from typing import Any

import structlog

from aigen.common.node import Node
from aigen.common.node_registry import register_node

LOGGER = structlog.get_logger(__name__)


@register_node("JsonToContext")
class JsonToContextNode(Node):
    def __init__(self, params: dict[str, Any]) -> None:
        super().__init__(params)

    def run(self, context: dict[str, Any]) -> None:
        params = self.format_params(context)
        input_var = params.get("input")

        if not input_var:
            raise ValueError("Input variable name cannot be empty.")
        if input_var not in context:
            raise ValueError(f"Input variable '{input_var}' does not exist in context.")

        payload = context[input_var]
        if not isinstance(payload, dict):
            raise ValueError(f"Input variable '{input_var}' must be a dict.")

        context.update(payload)
        LOGGER.info(
            "Merged JSON object into context",
            input=input_var,
            keys_count=len(payload),
        )
