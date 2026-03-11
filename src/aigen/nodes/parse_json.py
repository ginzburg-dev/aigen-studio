import json
import re
from typing import Any

import structlog

from aigen.common.node import Node
from aigen.common.node_registry import register_node

LOGGER = structlog.get_logger(__name__)


@register_node("ParseJSON")
class ParseJSONNode(Node):
    def __init__(self, params: dict[str, Any]) -> None:
        super().__init__(params)

    def _parse_json_payload(self, payload: str) -> dict[str, Any]:
        text = payload.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\s*```$", "", text)

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start == -1 or end <= start:
                raise
            data = json.loads(text[start : end + 1])

        if not isinstance(data, dict):
            raise ValueError("JSON payload must be an object.")
        return data

    def run(self, context: dict[str, Any]) -> None:
        params = self.format_params(context)
        input_var = params.get("input")
        output_var = params.get("output")
        normalize_keys = bool(params.get("normalize_keys", True))

        if not input_var:
            raise ValueError("Input variable name cannot be empty.")
        if input_var not in context:
            raise ValueError(f"Input variable '{input_var}' does not exist in context.")
        if not output_var:
            output_var = f"{input_var}_obj"

        data = self._parse_json_payload(str(context[input_var]))
        parsed: dict[str, Any] = {}
        for key, value in data.items():
            normalized_key = (
                key.strip().lower().replace("-", "_").replace(" ", "_")
                if normalize_keys
                else key
            )
            parsed[normalized_key] = value

        context[str(output_var)] = parsed

        LOGGER.info(
            "Parsed JSON object",
            input=input_var,
            output=str(output_var),
            keys_count=len(parsed),
        )
