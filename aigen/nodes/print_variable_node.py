from aigen.core.node_base import NodeBase
from aigen.gpt_chat_session import GPTChatSession
from aigen.gpt_prompt import GPTPrompt
from aigen.core.file_handler import FileHandler
from typing import Any, Dict, List, Optional, Union

class PrintVariableNode(NodeBase):
    def __init__(self, params: Dict) -> None:
        super().__init__("PrintVariable", params)
    
    def run(self, context: Dict):
        name = self.params.get('name', "")

        if name == "":
            raise ValueError("Empty variable name!")
        if name not in context:
            raise ValueError("Variable name does not exist!")
        
        print(f"variable name: {name}\ndata: {context[name]}")
