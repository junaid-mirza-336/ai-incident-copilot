from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables or .env file."""

    llm_api_key: str = "sk-placeholder"
    llm_base_url: str = "http://127.0.0.1:31415/v1"
    llm_model: str = "auto"
    mock_mode: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
