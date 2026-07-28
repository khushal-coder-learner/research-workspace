from llama_index.llms.openrouter import OpenRouter
from app.core.config import settings

llm = OpenRouter(
    api_key = settings.openrouter_api_key,
    model = settings.generation_model
)