from aigen.core.node_base import NodeBase
from aigen.gpt_chat_session import GPTChatSession
from aigen.gpt_prompt import GPTPrompt
from aigen.core.file_handler import FileHandler
from typing import Any, Dict, List, Optional, Union

class CopyVariableNode(NodeBase):
    def __init__(self, params: Dict) -> None:
        super().__init__("CopyBuffer", params)
    
    def run(self, context: Dict) -> None:
        input = self.params.get('input', "")
        output = self.params.get('output', "")
        mode = self.params.get('mode', 'replace')
        
        if input == "":
            raise ValueError("Empty input value!")
        if input not in context:
            raise ValueError("Input is not exist!")
        if output == "":
            raise ValueError("Empty output value!")

        if mode == 'append':
            if output not in context:
                context[output] = []
            context[output].append(context[input])
        else:
            context[output] = context[input]

# copy lists dicts
