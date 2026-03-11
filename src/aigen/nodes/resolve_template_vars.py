from typing import Any

import structlog

from aigen.common.node import Node
from aigen.common.node_registry import register_node
from aigen.common.utils import find_vars, replace_vars

LOGGER = structlog.get_logger(__name__)


@register_node("ResolveTemplateVars")
class ResolveTemplateVars(Node):
    def __init__(self, params: dict[str, Any]) -> None:
        super().__init__(params)

    def run(self, context: dict[str, Any]) -> None:
        params = self.format_params(context)
        input_var = params.get("input")
        output_var = params.get("output")
        strict = bool(params.get("strict", False))

        if not input_var:
            raise ValueError("Input variable name cannot be empty.")
        if input_var not in context:
            raise ValueError(f"Input variable '{input_var}' does not exist in context.")
        if not output_var:
            raise ValueError("Output variable name cannot be empty.")

        template_text = str(context[input_var])
        rendered_text = replace_vars(template_text, context)
        unresolved = find_vars(rendered_text)
        if strict and unresolved:
            unresolved_vars = ", ".join(sorted(set(unresolved)))
            raise ValueError(f"Unresolved template variables: {unresolved_vars}")

        context[output_var] = rendered_text
        LOGGER.info(
            "Rendered template",
            input=input_var,
            output=output_var,
            unresolved_count=len(set(unresolved)),
        )
