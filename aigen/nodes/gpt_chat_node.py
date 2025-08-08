from aigen.core.node_base import NodeBase
from aigen.gpt_chat_session import GPTChatSession
from aigen.gpt_prompt import GPTPrompt
from aigen.core.file_handler import FileHandler
from typing import Any, Dict, List, Optional, Union

class GPTChatNode(NodeBase):
    def __init__(self, params: Dict) -> None:
        super().__init__("GPTChat", params)
    
    def run(self, context: Dict):
        api_key = context['api-key'] if self.params.get('api-key' 'no-api-key') in context else self.params.get('api-key', 'no-api-key')
        input = self.params.get('input', 'gptbuffer')
        output = self.params.get('output', 'gptbuffer')
        mode = self.params.get('mode', 'replace')
        max_tokens = self.params.get('max_tokens', 256)
        prompt = self.params.get('prompt', [])

        chat = GPTChatSession(api_key=api_key)
        chat.history.add(context.get(input, []))

        for item in prompt:
            type = item.get('type')
            content = item.get('content')
            if type == "image":
                detailed: bool = item.get('detailed', True)
                if isinstance(content, str):
                    images = FileHandler.expand_images(content)
                elif isinstance(content, list):
                    for i in content:
                        if isinstance(i, str):
                            images = FileHandler.expand_images(content)
                        else:
                            raise ValueError("Image files not found!")
                for i in images:
                    chat.add_image(i, detailed=detailed)
            if type == "text":
                if isinstance(content, str):
                    chat.add_text(content)
                elif isinstance(content, list):
                    for i in content:
                        if isinstance(i, str):
                            chat.add_text(i)
                        else:
                            raise ValueError("Wrong content format!")
                else:
                    raise ValueError("Wrong content format!")
        chat.chat(max_tokens=max_tokens)

        if mode == 'append':
            if output not in context:
                context[output] = []
            context[output].extend(chat.history.data)
        else:
            context[output] = chat.history.data

