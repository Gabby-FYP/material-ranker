import sentry_sdk
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.core.config import settings
from src.urls import routes
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse
from src.libs.utils import parse_html_form_field_error, parse_html_form_error, parse_html_toast_message
from src.libs.exceptions import BadRequestError, ServiceError
from sqlalchemy_file.storage import StorageManager


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# mount static files
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
if settings.file_storage_container:
    try:
        StorageManager.add_storage(
            settings.FILE_STORAGE_CONTAINER_NAME, settings.file_storage_container
        )
    except RuntimeError:
        pass


@app.exception_handler(RequestValidationError)
def form_field_exception_handler(request: Request, exc: RequestValidationError):
    """Handle form error."""
    messages = [
        parse_html_form_field_error(
            error_level='error',
            message=f"{error['msg']}",
        )
        for error in exc.errors()
    ]

    return HTMLResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=f'{''.join(messages)}',
    )


@app.exception_handler(BadRequestError)
def bad_request_exception_handler(request: Request, exc: BadRequestError):
    """Handle bad request error."""
    return HTMLResponse(
        status_code=exc.status_code,
        content=parse_html_form_error(error_level='error', message=exc.detail)
    )


@app.exception_handler(ServiceError)
def service_exception_handler(request: Request, exc: ServiceError):
    """Handles service exceptions."""
    return HTMLResponse(
        status_code=exc.status_code,
        headers={'HX-Retarget': '#server-error-toast', 'HX-Reswap': 'beforeend'},
        content=parse_html_toast_message(
            error_level='error', 
            message=exc.detail, 
            title=exc.title,
        )
    )


app.include_router(routes)
