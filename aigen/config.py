from pydantic import BaseModel, Field

class BaseConfig(BaseModel):
    gpt_secret_key: str = Field(alias="GPT_SECRET_KEY", default="")
