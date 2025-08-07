import os
from aigen.gpt_chat_session import GPTChatSession
from aigen.mock_gpt_chat_session import MockGPTChatSession
from aigen.core.image_encoder import ImageEncoder
from aigen.gpt_role import DEFAULT_GPT_ROLE
from aigen.gpt_prompt import GPTPrompt

def test_gpt_chat_session_set_prompt():
    chat = GPTChatSession(api_key="api-key")
    chat.set_prompt(GPTPrompt(text="test"))
    assert chat.buffer.role == DEFAULT_GPT_ROLE
    assert chat.buffer.content[-1].get("text") == "test"

def test_gpt_chat_session_add_text():
    chat = GPTChatSession(api_key="api-key")
    chat.add_text("test")
    assert chat.buffer.role == DEFAULT_GPT_ROLE
    assert chat.buffer.content[-1].get("text") == "test"

def test_gpt_chat_session_add_image():
    chat = GPTChatSession(api_key="api-key")
    image_path = "././examples/image_samples/rabbit_pixel_art.png"
    mimic_type = ImageEncoder.get_mime_type(image_path)
    chat.add_image(image_path)
    assert chat.buffer.role == DEFAULT_GPT_ROLE
    assert chat.buffer.content[-1].get("image_url").get("detail") == "low"
    assert f"data:{mimic_type}" in chat.buffer.content[-1].get("image_url").get("url")

def test_gpt_chat_session_mock_chat():
    chat = MockGPTChatSession(api_key="api-key")
    chat.add_text("Send 1 test word to the chat")
    response = chat.chat(extra_prompt="Extra")
    assert response == "Example"
    assert len(chat.history.data) == 2
    assert len(chat.history.data[0]) == 2
    assert "Send 1" in chat.history.data[0].get("content")[0].get("text")
    assert "Extra" in chat.history.data[0].get("content")[1].get("text")
    print(chat.history)

def test_gpt_chat_session_mock_save_load_history():
    chat = MockGPTChatSession(api_key="api-key")
    chat.add_text("Save session")
    chat.chat()
    cache_name = "test_cache"
    chat.save_chat_history(cache_name)
    chat.load_chat_history(cache_name)
    cache_file_name = chat.get_cache_filename(cache_name)
    assert os.path.exists(cache_file_name)
    print(chat.history)

def test_gpt_chat_session_mock_load_history():
    chat = MockGPTChatSession(api_key="api-key")
    cache_name = "test_cache"
    chat.load_chat_history(cache_name)
    cache_file_name = chat.get_cache_filename(cache_name)
    assert os.path.exists(cache_file_name)
    chat.delete_cache_file(cache_name)
    assert not os.path.exists(cache_file_name)
    response = chat.chat("Does it make sense for you? :)", max_tokens=10)
    assert response
    print(chat.history)
