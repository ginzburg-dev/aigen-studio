import pytest
import yaml

from aigen.nodes.gpt_chat import GPTChatNode

pytestmark = pytest.mark.unit


class StubOpenAIClient:
    last_content = None
    last_kwargs = None

    def __init__(
        self, model: str | None = None, max_tokens: int | None = None, **kwargs
    ) -> None:
        self.model = model
        self.max_tokens = max_tokens

    def generate(self, content, **kwargs):
        StubOpenAIClient.last_content = content
        StubOpenAIClient.last_kwargs = kwargs
        return "stub-response"


def test_gpt_chat_node_updates_context_history(monkeypatch):
    monkeypatch.setattr("aigen.nodes.gpt_chat.OpenAIClient", StubOpenAIClient)

    params = {
        "prompt": [{"type": "text", "content": "hello"}],
        "chat_history": "chat_buffer",
        "output": "answer",
        "max_tokens": 64,
        "model": "gpt-4o-mini",
    }
    context = {}

    node = GPTChatNode(params)
    node.run(context)

    print("response:", context["answer"])
    print("history:", context["chat_buffer"])

    assert context["answer"] == "stub-response"
    assert "chat_buffer" in context
    assert len(context["chat_buffer"]) == 2
    assert context["chat_buffer"][0]["role"] == "user"
    assert context["chat_buffer"][1]["role"] == "assistant"


def test_gpt_chat_node_reuses_file_history_with_image_message(monkeypatch, tmp_path):
    monkeypatch.setattr("aigen.nodes.gpt_chat.OpenAIClient", StubOpenAIClient)

    history_file = tmp_path / "history.yaml"
    old_history = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "describe image"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "data:image/png;base64,AAAA",
                        "detail": "high",
                    },
                },
            ],
        },
        {"role": "assistant", "content": "old answer"},
    ]
    history_file.write_text(yaml.safe_dump(old_history), encoding="utf-8")

    params = {
        "prompt": [{"type": "text", "content": "next turn"}],
        "chat_history": str(history_file),
        "output": "answer",
    }
    context = {}

    node = GPTChatNode(params)
    node.run(context)

    print("response:", context["answer"])
    print("sent_to_client:", StubOpenAIClient.last_content)

    assert context["answer"] == "stub-response"
    assert StubOpenAIClient.last_content is not None
    assert StubOpenAIClient.last_content[0]["content"][1]["type"] == "image_url"

    saved_history = yaml.safe_load(history_file.read_text(encoding="utf-8"))
    assert len(saved_history) == 4
    assert saved_history[-1]["role"] == "assistant"


def test_gpt_chat_node_skips_empty_image_list(monkeypatch):
    monkeypatch.setattr("aigen.nodes.gpt_chat.OpenAIClient", StubOpenAIClient)

    params = {
        "prompt": [
            {"type": "text", "content": "hello"},
            {"type": "image", "content": "images", "detailed": True},
        ],
        "chat_history": "chat_buffer",
        "output": "answer",
    }
    context = {"images": []}

    node = GPTChatNode(params)
    node.run(context)

    assert context["answer"] == "stub-response"
    sent = StubOpenAIClient.last_content
    assert sent is not None
    first_msg = sent[0]
    assert first_msg["role"] == "user"
    assert first_msg["content"] == [{"type": "text", "text": "hello"}]


def test_gpt_chat_node_resolves_deferred_template_text(monkeypatch):
    monkeypatch.setattr("aigen.nodes.gpt_chat.OpenAIClient", StubOpenAIClient)

    params = {
        "prompt": [{"type": "text", "content": "prompt_description"}],
        "chat_history": "chat_buffer",
        "output": "answer",
    }
    context = {
        "image_critique": "moody blue mountains at sunset",
        "prompt_description": "Using critique: ${image_critique}",
    }

    node = GPTChatNode(params)
    node.run(context)

    sent = StubOpenAIClient.last_content
    assert sent is not None
    first_msg = sent[0]
    assert first_msg["role"] == "user"
    assert first_msg["content"] == [
        {"type": "text", "text": "Using critique: moody blue mountains at sunset"}
    ]
