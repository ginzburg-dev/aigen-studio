import json
import re


def replace_vars(template: str, params: dict, pattern=r"\$\{(\w+)\}") -> str:
    """Replace ${var} in template with values from params."""

    def repl(match):
        var_name = match.group(1)
        if var_name not in params:
            return match.group(0)

        value = params[var_name]
        if isinstance(value, (list, dict)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    return re.sub(pattern, repl, template)


def find_vars(template: str, pattern=r"\$\{(\w+)\}") -> list[str]:
    """Return a list of variable names found in the template."""
    return re.findall(pattern, template)


def format_string(template: str, params: dict) -> str:
    """Format the template string with the given parameters."""
    return template.format(**params)
