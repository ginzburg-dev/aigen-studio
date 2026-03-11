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
        raw_if_missing = params.get("if_missing", False)
        if isinstance(raw_if_missing, str):
            if_missing = raw_if_missing.strip().lower() in {"1", "true", "yes", "on"}
        else:
            if_missing = bool(raw_if_missing)

        if not name:
            raise ValueError("Incorrect name. Name cannot be empty.")
        if if_missing and name in context:
            LOGGER.info("Skip set variable (already exists)", name=name)
            return
        context[name] = value
        LOGGER.info("Set variable", name=name, value=str(value)[0:50] + " ...")
