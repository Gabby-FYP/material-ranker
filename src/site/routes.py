from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from src.core.config import settings
from src.core.jinja2 import render_template

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def landing_page(request: Request) -> HTMLResponse:
    """Render landing page."""

    return render_template(
        request=request, 
        template_name="site/pages/landing.html"
    )
