from aigen.models import Role
from aigen.common.image_encoder import ImageEncoder
from aigen.common.prompt import Prompt


class OpenAIPrompt(Prompt):
    def __init__(
        self,
        role: str = Role.USER.value,
        text: str | None = None,
        image_path: str | None = None,
    ) -> None:
        super().__init__(role=role, text=text, image_path=image_path)

    def add_text(self, text: str) -> None:
        if not isinstance(text, str):
            raise TypeError("Text expects a str")
        self._content.append({"type": "text", "text": text})

    def add_image(self, image_path: str, detailed=True) -> None:
        base64_image = ImageEncoder.encode_image(image_path)
        mime_type = ImageEncoder.get_mime_type(image_path)

        details = "low"
        if detailed:
            details = "high"
        self._content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{base64_image}",
                    "detail": details,
                },
            }
        )
