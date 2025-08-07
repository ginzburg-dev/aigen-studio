from aigen.gpt_prompt import GPTPrompt

def test_gpt_prompt_init():
    prompt = GPTPrompt(text="test")
    print(prompt)
