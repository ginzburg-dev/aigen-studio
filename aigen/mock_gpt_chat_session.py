from aigen.gpt_chat_session import GPTChatSession
from aigen.gpt_prompt import GPTPrompt
from aigen.gpt_role import DEFAULT_GPT_ROLE, ROLE_GPT_ASSISTANT
from typing import Any, Optional, List, Dict

class MockGPTChatSession(GPTChatSession):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def chat(self, *args, **kwargs) -> Any:
        # Optionally, you can add an extra prompt for this turn
        extra_prompt = args[0] if args else kwargs.get("extra_prompt")
        if extra_prompt:
            # Set extra_prompt to the session's temporal buffer
            self.add_text(extra_prompt)
        # Move prompt buffer to history
        self._move_buffer_to_history()
        # Send all prompts (history) to model
        messages = self.history.data
        
        assistant_message = "Example"
        # Flush model's response to history
        self.history.add(GPTPrompt(role=ROLE_GPT_ASSISTANT, text=assistant_message))
        return assistant_message

    def _create_buffer(self) -> Any:
        return GPTPrompt()
