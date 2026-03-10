from pathlib import Path
from typing import Any

import structlog

from aigen.common.file_handler import FileHandler
from aigen.common.node import Node
from aigen.common.node_registry import register_node

LOGGER = structlog.get_logger(__name__)


@register_node("ReadFile")
class ReadFileNode(Node):
    def __init__(self, params: dict[str, Any]) -> None:
        super().__init__(params)

    def run(self, context: dict[str, Any]) -> None:
        params = self.format_params(context)
        filepath = params.get("filepath") or params.get("file_path", "")
        output = params.get("output")

        if not output:
            raise ValueError("Output variable name cannot be empty.")

        if not Path(filepath).exists():
            raise ValueError("File not found.")

        data = FileHandler.read_text(filepath)
        context[output] = data
        LOGGER.info("Read file", filepath=filepath, output=output)
