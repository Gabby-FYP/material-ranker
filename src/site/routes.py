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


@router.get("/login/", response_class=HTMLResponse)
def login_page(request: Request)  -> HTMLResponse:
    """Render login page."""
    return render_template(
        request=request, 
        template_name="site/pages/auth/login.html"
    )


@router.get("/signup/", response_class=HTMLResponse)
def signup_page(request: Request) -> HTMLResponse:
    """Render signup page."""
    return render_template(
        request=request, 
        template_name="site/pages/auth/signup.html"
    )


@router.get("/reset-password/", response_class=HTMLResponse)
def paswword_reset_page(request: Request) -> HTMLResponse:
    """Render password reset page."""
    return render_template(
        request=request, 
        template_name="site/pages/auth/password-reset.html"
    )


@router.get("/reset-password/set-password/", response_class=HTMLResponse)
def password_reset_set_password_page(request: Request) -> HTMLResponse:
    """Render password reset set password page."""
    return render_template(
        request=request, 
        template_name="site/pages/auth/password-reset-set-password.html"
    )
