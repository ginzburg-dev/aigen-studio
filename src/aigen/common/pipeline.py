from typing import Any

import aigen.nodes  # noqa: F401  # Ensure node decorators populate NODE_REGISTRY.

from aigen.common.node_registry import NODE_REGISTRY


def is_node_registered(node: str) -> bool:
    return node in NODE_REGISTRY


def process_actions(context: dict[str, Any], instructions: list[dict]) -> None:
    for action in instructions:
        node_name = action.get("node")
        if not node_name or not is_node_registered(node_name):
            raise ValueError(f"Node '{node_name}' is not registered.")
        params = action.get("params", {})
        node = NODE_REGISTRY[node_name](params)
        node.run(context)
