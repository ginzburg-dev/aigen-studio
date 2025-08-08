from aigen.nodes.gpt_chat_node import GPTChatNode
from aigen.nodes.set_variable_node import SetVariableNode
from aigen.nodes.copy_variable_node import CopyVariableNode
from aigen.nodes.print_variable_node import PrintVariableNode
from aigen.nodes.save_file_node import SaveFileNode
from aigen.nodes.read_file_node import ReadFileNode
from typing import Any, Dict, List, Union

NODE_REGISTRY = {
    'SetVariable': SetVariableNode,
    'CopyVariable': CopyVariableNode,
    'PrintVariable': PrintVariableNode,
    'ReadFile': ReadFileNode,
    'SaveFile': SaveFileNode,
    'GPTChat': GPTChatNode,
    #'LoadTextFile': LoadTextFileNode,
    #'SaveTextFile': SaveTextFileNode,
    #'MergeBuffers': MergeBuffersNode,
    # add new nodes here
}

def is_node_registered(node: str) -> bool:
    return node in NODE_REGISTRY

def process_actions(context, instructions):
    context: Dict = {}
    for action in instructions:
        node_name = action['node']
        params = action['params']
        if is_node_registered(node_name):
            node = NODE_REGISTRY[node_name](params)
            node.run(context)
        else:
            raise ValueError(f"Node '{node_name}' does not exists!")
