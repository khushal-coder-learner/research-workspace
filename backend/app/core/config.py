from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Research Workspace"
    app_version: str = "0.1.0"
    debug: bool = True

    database_url: str = ""
    redis_url: str = ""

    google_api_key: str = ""
    openrouter_api_key: str = ""

    chunk_size: int= 512
    chunk_overlap: int = 64

    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embed_dimensions: int = 384

    generation_model: str = ""

    temperature: float = 1.0

    max_tokens: int = 512
    
    top_k: int = 5

    postgres_db: str = ""
    postgres_user: str = ""
    postgres_password: str = ""
    postgres_port: str = ""
    postgres_host: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()