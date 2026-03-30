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

    model_config = SettingsConfigDict(
        env_file=".env", 
        extra="ignore",
        env_prefix="",
        case_sensitive=False
    )


settings = Settings()
