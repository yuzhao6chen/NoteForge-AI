from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "NoteForge-AI"
    database_url: str = "sqlite:///./noteforge.db"
    storage_dir: str = "storage"

    # The provider name is "openai" because this project uses
    # OpenAI-compatible Chat Completions APIs such as OpenAI, DeepSeek, or Qwen.
    llm_provider: str = "openai"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.deepseek.com"
    openai_model: str = "deepseek-v4-flash"
    llm_model_options: str = ""
    llm_request_timeout: int = 180

    # Search
    search_provider: str = "tavily"
    tavily_api_key: str = ""
    brave_api_key: str = ""

    # Writing quality gate
    min_review_score: int = 88

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
