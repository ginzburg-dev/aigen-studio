from typing import Type

from aigen.common.node import Node

NODE_REGISTRY = {}


def register_node(name: str):
    def decorator(cls: Type[Node]) -> Type[Node]:
        if name in NODE_REGISTRY:
            msg = f"Node '{name}' already registered."
            raise ValueError(msg)
        NODE_REGISTRY[name] = cls
        return cls

    return decorator
