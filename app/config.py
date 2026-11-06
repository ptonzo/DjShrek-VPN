from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "DjShrek VPN"
    app_env: str = "development"
    app_secret: str = "development-only-change-me"
    public_base_url: str = "http://localhost:8000"
    healthcheck_timeout_seconds: float = 3.0
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
