from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    port: int = 8000
    environment: str = "production"
    llm_provider: str = "google"
    gemini_api_key: str = ""
    openai_api_key: str = ""
    api_domain: str = ""
    state_db_path: str = "data/state_db.sqlite"
    get_bpm_history_endpoint: str = "/api/get_bpm_history_data"

    # CORS
    backend_cors_origins: list[str] = ["*"]

    # AWS / Bedrock
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_session_token: str | None = None
    aws_region: str = "eu-west-1"
    aws_bedrock_model_id: str = "eu.amazon.nova-2-lite-v1:0"

    model_config = SettingsConfigDict(
        env_file=".env", 
        extra="ignore",
        env_prefix="",
        case_sensitive=False
    )


settings = Settings()
