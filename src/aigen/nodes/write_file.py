from aigen.common.node import Node
from aigen.common.file_handler import FileHandler
from typing import Dict


class SaveFileNode(Node):
    def __init__(self, input: str, filepath: str) -> None:
        super().__init__("SaveFile", {"file_path": filepath, "input": input})

    def run(self, context: Dict):
        params = self.format_params(context)
        file_path = params.get("file_path")
        input = params.get("input")

        if not file_path:
            raise ValueError("Empty file_path.")
        if not input or input not in context:
            raise ValueError("Variable input does not exist.")

        FileHandler.write_text(file_path, context[input])
