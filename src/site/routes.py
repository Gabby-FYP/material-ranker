from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import sentry_sdk
from fastapi import FastAPI, Request, Response, Depends, Form
from fastapi.staticfiles import StaticFiles
from src.core.config import settings
from src.core.dependecies import check_htmx_request, push_htmx_history
from src.core.jinja2 import render_template
from typing import Annotated

from src.users.models import User
from src.users.services import user_signup_service
from src.users.schemas import UserSignupForm, UserSignupFormValidate



router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def landing_page(
    request: Request,
    response: Response,
) -> HTMLResponse:
    """Render landing page."""
    return render_template(
        request=request,
        response=response,
        template_name="site/pages/landing.html"
    )


@router.get(
    "/login/", 
    dependencies=[Depends(push_htmx_history)],
    response_class=HTMLResponse
)
def login_page(
    request: Request,
    response: Response,
    is_htmx: Annotated[bool, Depends(check_htmx_request)],
)  -> HTMLResponse:
    """Render login page."""
    if is_htmx:
        return render_template(
            request=request,
            response=response,
            template_name="site/pages/auth/fragments/login.html",
        )

    return render_template(
        request=request,
        response=response,
        template_name="site/pages/auth/login.html"
    )


@router.get(
    "/signup/", 
    response_class=HTMLResponse,
    dependencies=[Depends(push_htmx_history)],
)
def signup_page(
    request: Request,
    response: Response,
    is_htmx: Annotated[bool, Depends(check_htmx_request)],
) -> HTMLResponse:
    """Render signup page."""
    if is_htmx:
        return render_template(
            request=request,
            response=response,
            template_name="site/pages/auth/fragments/signup.html",
        )

    return render_template(
        request=request, 
        response=response,
        template_name="site/pages/auth/signup.html"
    )


@router.post("/signup/", response_class=HTMLResponse)
def signup_form(
    request: Request,
    response: Response,
    data: Annotated[User, Depends(user_signup_service)]
) -> HTMLResponse:
    """Perform user signup."""
    return HTMLResponse('')


@router.patch(
    "/signup/validate/",
    response_class=HTMLResponse,
)
def signup_form(
    request: Request,
    response: Response,
    data: Annotated[UserSignupFormValidate, Form()]
) -> HTMLResponse:
    """Perform user signup."""
    return HTMLResponse('')


@router.get(
    "/reset-password/", 
    response_class=HTMLResponse,
    dependencies=[Depends(push_htmx_history)],
)
def paswword_reset_page(
    request: Request,
    response: Response,
    is_htmx: Annotated[bool, Depends(check_htmx_request)],
) -> HTMLResponse:
    """Render password reset page."""
    if is_htmx:
        return render_template(
            request=request,
            response=response,
            template_name="site/pages/auth/fragments/password-reset.html",
        )

    return render_template(
        request=request,
        response=response,
        template_name="site/pages/auth/password-reset.html"
    )


@router.get(
    "/reset-password/set-password/", 
    response_class=HTMLResponse,
    dependencies=[Depends(push_htmx_history)],
)
def password_reset_set_password_page(
    request: Request,
    response: Response,
    is_htmx: Annotated[bool, Depends(check_htmx_request)],
) -> HTMLResponse:
    """Render password reset set password page."""
    if is_htmx:
        return render_template(
            request=request,
            response=response,
            template_name="site/pages/auth/fragments/password-reset-set-password.html",
        )

    return render_template(
        request=request,
        response=response,
        template_name="site/pages/auth/password-reset-set-password.html"
    )
