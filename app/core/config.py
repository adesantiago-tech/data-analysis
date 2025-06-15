from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    # Configuración general
    PROJECT_NAME: str = "Data Analysis API"
    API_V1_STR: str = "/api/v1"

    # MinIO / S3
    MINIO_ENDPOINT: str = Field(default="localhost:9000")   # <-- CAMBIADO
    MINIO_ACCESS_KEY: str = Field(default="minioadmin")
    MINIO_SECRET_KEY: str = Field(default="minioadmin")
    MINIO_BUCKET: str = Field(default="data-files")

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")


    # Otras settings
    MAX_FILE_SIZE_MB: int = 50

    class Config:
        env_file = ".env"

settings = Settings()
