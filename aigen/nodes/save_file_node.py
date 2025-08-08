from aigen.core.node_base import NodeBase
from aigen.gpt_chat_session import GPTChatSession
from aigen.gpt_prompt import GPTPrompt
from aigen.core.file_handler import FileHandler
from typing import Any, Dict, List, Optional, Union

class SaveFileNode(NodeBase):
    def __init__(self, params: Dict) -> None:
        super().__init__("SaveFile", params)
    
    def run(self, context: Dict):
        file_path = self.params.get('file_path', "")
        input = self.params.get('input', "")

        if file_path == "":
            raise ValueError("Empty file_path!")
        if input not in context:
            raise ValueError("Variable input does not exist!")
        
        FileHandler.wrtie_text(file_path, context[input])
