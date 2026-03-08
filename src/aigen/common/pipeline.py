from aigen.nodes.gpt_chat import GPTChatNode
from aigen.nodes.set_variable import SetVariableNode
from aigen.nodes.copy_variable import CopyVariableNode
from aigen.nodes.print_variable import PrintVariableNode
from aigen.nodes.write_file import SaveFileNode
from aigen.nodes.read_file import ReadFileNode
from typing import Any

NODE_REGISTRY = {
    "SetVariable": SetVariableNode,
    "CopyVariable": CopyVariableNode,
    "PrintVariable": PrintVariableNode,
    "ReadFile": ReadFileNode,
    "SaveFile": SaveFileNode,
    "GPTChat": GPTChatNode,
    #'LoadTextFile': LoadTextFileNode,
    #'SaveTextFile': SaveTextFileNode,
    #'MergeBuffers': MergeBuffersNode,
    # add new nodes here
}


def is_node_registered(node: str) -> bool:
    return node in NODE_REGISTRY


def process_actions(context: dict[str, Any], instructions: list[dict]) -> None:
    for action in instructions:
        node_name = action["node"]
        params = action["params"]
        if is_node_registered(node_name):
            node = NODE_REGISTRY[node_name](params)
            node.run(context)
        else:
            raise ValueError(f"Node '{node_name}' does not exists!")
