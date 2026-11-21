from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables or .env file."""

    freellmapi_api_key: str = "sk-placeholder"
    freellmapi_base_url: str = "http://127.0.0.1:31415/v1"
    default_model: str = "auto"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
