import sentry_sdk
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.core.config import settings
from src.urls import routes


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# mount static files
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

app.include_router(routes)
