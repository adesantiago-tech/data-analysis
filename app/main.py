from fastapi import FastAPI
from app.api.endpoints import router as files_router


from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

app.include_router(files_router, prefix=settings.API_V1_STR)

@app.get(f"{settings.API_V1_STR}/health", tags=["health"])
async def health_check():
    """
    Healthcheck endpoint para saber si la API está viva.
    """
    return {"status": "ok"}
