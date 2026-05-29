from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://mongodb:27017"
    MONGODB_DB: str = "healthai_recommendations"
    GEMINI_API_KEY: str = ""
    MOCK_AI: bool = False

    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://api:8000",
    ]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
