from aigen.prompt.openai import OpenAIPrompt


def test_gpt_prompt_init():
    prompt = OpenAIPrompt(text="test", role="user")
    print(prompt)
