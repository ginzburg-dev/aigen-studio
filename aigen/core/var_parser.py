import re

def replace_vars(template: str, params: dict, pattern=r"\$\{(\w+)\}") -> str:
    """Replace ${var} in template with values from params."""
    def repl(match):
        var_name = match.group(1)
        return str(params.get(var_name, match.group(0)))
    return re.sub(pattern, repl, template)

def find_vars(template: str, pattern=r"\$\{(\w+)\}") -> list[str]:
    """Return a list of variable names found in the template."""
    return re.findall(pattern, template)
