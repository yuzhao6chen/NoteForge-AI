from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Read2Post"
    database_url: str = "sqlite:///./read2post.db"
    storage_dir: str = "storage"

    # LLM：这里虽然叫 openai，但实际表示 OpenAI-compatible 接口
    # DeepSeek / 千问 都可以填在这里
    llm_provider: str = "openai"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    # Search
    search_provider: str = "tavily"
    tavily_api_key: str = ""
    brave_api_key: str = ""

    # Writing quality gate
    min_review_score: int = 88

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
