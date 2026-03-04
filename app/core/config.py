from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "RentUp"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database (MongoDB Atlas)
    MONGODB_URL: str = Field(
        default="mongodb+srv://localhost:27017"
    )
    MONGODB_DB_NAME: str = "rentup"

    # Security
    SECRET_KEY: str = "change-this-to-a-random-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
