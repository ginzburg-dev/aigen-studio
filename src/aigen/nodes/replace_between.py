import re
import textwrap
from typing import Any

import structlog

from aigen.common.node import Node
from aigen.common.node_registry import register_node

LOGGER = structlog.get_logger(__name__)


@register_node("ReplaceBetween")
class ReplaceBetweenNode(Node):
    def __init__(self, params: dict[str, Any]) -> None:
        super().__init__(params)

    def run(self, context: dict[str, Any]) -> None:
        params = self.format_params(context)
        input_var = params.get("input")
        output_var = params.get("output") or input_var
        start_marker = params.get("start_marker")
        end_marker = params.get("end_marker")
        replacement_ref = params.get("replacement")

        if not input_var:
            raise ValueError("Input variable name cannot be empty.")
        if input_var not in context:
            raise ValueError(f"Input variable '{input_var}' does not exist in context.")
        if not output_var:
            raise ValueError("Output variable name cannot be empty.")
        if not start_marker or not end_marker:
            raise ValueError("start_marker and end_marker are required.")
        if replacement_ref is None:
            raise ValueError("replacement is required.")

        source_text = str(context[input_var])
        replacement_text = (
            str(context[replacement_ref])
            if isinstance(replacement_ref, str) and replacement_ref in context
            else str(replacement_ref)
        )

        start_index = source_text.find(start_marker)
        if start_index == -1:
            raise ValueError(f"start_marker not found: {start_marker}")
        replace_start = start_index + len(start_marker)

        end_index = source_text.find(end_marker, replace_start)
        if end_index == -1:
            raise ValueError(f"end_marker not found: {end_marker}")

        line_start = source_text.rfind("\n", 0, start_index) + 1
        marker_line_prefix = source_text[line_start:start_index]
        indent_match = re.match(r"[ \t]*", marker_line_prefix)
        indent = indent_match.group(0) if indent_match else ""

        fragment = textwrap.dedent(replacement_text.strip("\n"))
        indented_fragment = "\n".join(
            f"{indent}{line}" if line else "" for line in fragment.splitlines()
        )

        updated_text = (
            source_text[:replace_start]
            + "\n"
            + indented_fragment
            + "\n"
            + source_text[end_index:]
        )
        context[output_var] = updated_text
        LOGGER.info(
            "Replaced template section",
            input=input_var,
            output=output_var,
            start_marker=start_marker,
            end_marker=end_marker,
        )
