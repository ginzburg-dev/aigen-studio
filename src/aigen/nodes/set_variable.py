from typing import Any

import structlog

from aigen.common.node import Node
from aigen.common.node_registry import register_node

LOGGER = structlog.get_logger(__name__)


@register_node("SetVariable")
class SetVariableNode(Node):
    def __init__(self, params: dict[str, Any]) -> None:
        super().__init__(params)

    def run(self, context: dict[str, Any]) -> None:
        params = self.format_params(context)
        name = params.get("name")
        value = params.get("value", "")
        if not name:
            raise ValueError("Incorrect name. Name cannot be empty.")
        context[name] = value
        LOGGER.info("Set variable", name=name, value=value)
