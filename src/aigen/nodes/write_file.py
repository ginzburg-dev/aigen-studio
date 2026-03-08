from aigen.common.node_base import NodeBase
from aigen.gpt_chat_session import GPTChatSession
from aigen.gpt_prompt import GPTPrompt
from aigen.common.file_handler import FileHandler
from aigen.common.var_parser import replace_vars
from typing import Any, Dict, List, Optional, Union

class SaveFileNode(NodeBase):
    def __init__(self, input: str, filepath: str) -> None:
        super().__init__("SaveFile", {"file_path": filepath, "input": input })

    def run(self, context: Dict):
        file_path = self.params.get('file_path', "")
        file_path = replace_vars(file_path, context)
        input = self.params.get('input', "")
        input = replace_vars(input, context)

        if file_path == "":
            raise ValueError("Empty file_path!")
        if input not in context:
            raise ValueError("Variable input does not exist!")

        FileHandler.write_text(file_path, context[input])
