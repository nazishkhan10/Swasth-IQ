import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

# Find backend root directory containing .env
def find_env_file():
    curr = os.path.abspath(__file__)
    for _ in range(6):
        curr = os.path.dirname(curr)
        env_candidate = os.path.join(curr, ".env")
        if os.path.exists(env_candidate):
            return env_candidate
    return ".env"

env_path = find_env_file()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Medical Report Analyzer API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "med_report_analyzer_jwt_secret_key_production_grade_32_bytes_min_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    
    OPENAI_API_KEY: str = ""
    SARVAM_API_KEY: str = ""
    SARVAM_CHAT_API_KEY: str = ""
    GLM_API_KEY: str = ""

    # Phase 7 RAG Configuration
    RETRIEVAL_CANDIDATES: int = 100
    RERANK_TOP_K: int = 25
    FINAL_CONTEXT: int = 5
    RETRIEVAL_CACHE_TTL_SEC: int = 900

    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]

    model_config = SettingsConfigDict(
        env_file=env_path,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
