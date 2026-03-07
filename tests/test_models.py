from aigen.models import GPTModel

def test_gpt_model_validation():
    assert GPTModel.validate("gpt-4o") == True
    assert GPTModel.validate("gpt-4-turbo") == True
    assert GPTModel.validate("gpt-3.5-turbo") == True
    assert GPTModel.validate("invalid-model") == False
