from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for backend (where .env lives)
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost:3306/stock_platform"

    # JWT Authentication
    JWT_SECRET_KEY: str = "stocklens-default-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # External Market Data Provider (FMP)
    FMP_API_KEY: str = ""
    FMP_BASE_URL: str = "https://financialmodelingprep.com"

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH) if ENV_PATH.exists() else ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
