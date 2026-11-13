from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/styleagenda.db"
    session_secret: str = "local-dev-secret-change-before-deploy"
    session_https_only: bool = False
    model_config = SettingsConfigDict(env_file=".env", env_prefix="STYLEAGENDA_", extra="ignore")


settings = Settings()
Path("data").mkdir(exist_ok=True)
