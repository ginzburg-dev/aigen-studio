from aigen.core.node_base import NodeBase
from aigen.gpt_chat_session import GPTChatSession
from aigen.gpt_prompt import GPTPrompt
from aigen.core.file_handler import FileHandler
from typing import Any, Dict, List, Optional, Union

class ReadFileNode(NodeBase):
    def __init__(self, params: Dict) -> None:
        super().__init__("ReadFile", params)
    
    def run(self, context: Dict):
        file_path = self.params.get('file_path', "")
        output = self.params.get('output', "")
        mode = self.params.get('mode', 'replace')

        if file_path == "":
            raise ValueError("Empty file_path!")
        
        data = FileHandler.read_text(file_path)
        if mode == 'append':
            if output not in context:
                context[output] = []
            context[output].append(data)
        else:
            context[output] = data
