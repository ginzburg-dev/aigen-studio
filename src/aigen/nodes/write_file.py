from typing import Any

import structlog

from aigen.common.file_handler import FileHandler
from aigen.common.node import Node
from aigen.common.node_registry import register_node

LOGGER = structlog.get_logger(__name__)


@register_node("WriteFile")
class WriteFileNode(Node):
    def __init__(self, params: dict[str, Any]) -> None:
        super().__init__(params)

    def run(self, context: dict[str, Any]):
        params = self.format_params(context)
        file_path = params.get("file_path")
        input = params.get("input")

        if not file_path:
            raise ValueError("Empty file_path.")
        if not input or input not in context:
            raise ValueError("Variable input does not exist.")

        FileHandler.write_text(file_path, context[input])
        LOGGER.info("Write file", filepath=file_path, input=input)
