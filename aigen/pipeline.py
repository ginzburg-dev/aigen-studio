from aigen.nodes.gpt_chat_node import GPTChatNode
from aigen.nodes.load_text import LoadTextFileNode
from aigen.nodes.save_text import SaveTextFileNode
from aigen.nodes.merge_buffers import MergeBuffersNode

NODE_REGISTRY = {
    'GPTChat': GPTChatNode,
    'LoadTextFile': LoadTextFileNode,
    'SaveTextFile': SaveTextFileNode,
    'MergeBuffers': MergeBuffersNode,
    # add new nodes here
}
