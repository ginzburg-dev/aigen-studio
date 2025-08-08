from aigen.core.node_base import NodeBase
from aigen.gpt_chat_session import GPTChatSession
from aigen.gpt_prompt import GPTPrompt
from aigen.core.file_handler import FileHandler
from typing import Any, Dict, List, Optional, Union

class SetVariableNode(NodeBase):
    def __init__(self, params: Dict) -> None:
        super().__init__("SetVariable", params)
    
    def run(self, context: Dict):
        name = self.params.get('name', "")
        value = self.params.get('value', "")
        mode = self.params.get('mode', 'replace')
        
        if name == "":
            raise ValueError("Incorrect name!")
        if value == "":
            raise ValueError("Incorrect value!")

        if mode == 'append':
            if name not in context:
                context[name] = []
            context[name].append(value)
        else:
            context[name] = value
