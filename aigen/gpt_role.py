# Individual GPT role IDs
ROLE_GPT_USER = "user"
ROLE_GPT_SYSTEM = "system"
ROLE_GPT_ASSISTANT = "assistant"

# Default role
DEFAULT_GPT_ROLE = ROLE_GPT_USER

# List of available GPT roles
AVAILABLE_GPT_ROLES = [
    ROLE_GPT_USER, 
    ROLE_GPT_SYSTEM, 
    ROLE_GPT_ASSISTANT
]

# Optionally, a mapping for model families
ROLE_FAMILIES = {
    "gpt": [    ROLE_GPT_USER, ROLE_GPT_SYSTEM, ROLE_GPT_ASSISTANT],
}

def validate_role(role_name: str) -> bool:
    return role_name in AVAILABLE_GPT_ROLES
