from aigen.core.image_encoder import ImageEncoder
from aigen.gpt_role import DEFAULT_GPT_ROLE
from aigen.core.prompt import Prompt
from typing import Any, Optional, List, Dict, Union

class GPTPrompt(Prompt):
    """Builds GPT prompts for text and images."""
    def __init__(
            self,
            *,
            role: Optional[str] = DEFAULT_GPT_ROLE, 
            text: Optional[str] = None, 
            image_path: Optional[str] = None
    ) -> None:
        super().__init__(role=role, text=text, image_path=image_path)
        
    def add_text(self, text: str) -> None:
        if not isinstance(text, str):
            raise TypeError("Text expects a str")
        self.content.append({"type": "text", "text": text})

    def add_image(self, image_path, detailed = False):
        base64_image = ImageEncoder.encode_image(image_path)
        mime_type = ImageEncoder.get_mime_type(image_path)

        details = "low"
        if detailed: 
            details = "high"
        self.content.append({
        "type": "image_url",
        "image_url": {
            "url": f"data:{mime_type};base64,{base64_image}",
            "detail": details
        }
    })

    def to_dict(self, role: Optional[str] = None, type_filter: Union[str, List[str], None] = None) -> Dict[str, Any]:
        """Compile prompt as a dict, optionally filtering by type.

        Args:
            role: The role to use ('user', 'system', etc.) or default.
            type_filter: str or list of str, e.g. 'text' or ['text', 'image'].
                        If None, include all types.
        """
        role_value = role if role is not None else self.role

        if type_filter == None:
            content = self.content
        else:
            if isinstance(type_filter, str):
                allowed = {type_filter}
            else:
                allowed = set(type_filter)
            content = [item for item in self.content if item.get("type") in allowed]

        return {"role": role_value, "content": self.content}
    
    def clear(self) -> None:
        self.role = DEFAULT_GPT_ROLE
        self.content = []
