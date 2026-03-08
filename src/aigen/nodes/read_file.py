from pathlib import Path
from typing import Any

from aigen.common.node import Node
from aigen.common.file_handler import FileHandler


class ReadFileNode(Node):
    def __init__(self, params: dict[str, Any]) -> None:
        super().__init__("ReadFile", params)

    def run(self, context: dict[str, Any]) -> None:
        filepath = self.params.get("filepath", "")
        output = self.params.get("output")

        if not output:
            raise ValueError("Output variable name cannot be empty.")

        if not Path(filepath).exists():
            raise ValueError("File not found.")

        data = FileHandler.read_text(filepath)
        context[output] = data
