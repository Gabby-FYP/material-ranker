from typing import Annotated
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse

from src.admin.services import admin_request_password_reset_service, admin_user_login_service
from src.core.dependecies import check_htmx_request, push_htmx_history, require_authenticated_admin_user_session
from src.core.jinja2 import render_template
from src.models import AdminUser


router = APIRouter()


@router.get("/dashboard/", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    response: Response,
    adminuser: Annotated[AdminUser, Depends(require_authenticated_admin_user_session)]
) -> HTMLResponse:
    """Render the admin dashboard"""
    return render_template(
        request=request,
        response=response,
        template_name="site/pages/admin/admin_dashboard.html",
        context={"user": adminuser}
    )


@router.get(
    "/reset-password/",
    response_class=HTMLResponse,
    dependencies=[Depends(push_htmx_history)],
)
def admin_password_reset_page(
    request: Request,
    response: Response,
    is_htmx: Annotated[bool, Depends(check_htmx_request)],
) -> HTMLResponse:
    """Render admin password reset page """
    if is_htmx:
        return render_template(
            request=request,
            response=response,
            template_name="site/pages/auth/fragments/admin_reset_password.html",
        )

    return render_template(
        request=request,
        response=response,
        template_name='site/pages/auth/password-reset.html'
    )
    

@router.post(
    "/reset-password/", 
    response_class=HTMLResponse,
)
def paswword_reset_form(
    request: Request,
    response: Response,
    is_htmx: Annotated[bool, Depends(check_htmx_request)],
    _: Annotated[AdminUser, Depends(admin_request_password_reset_service)]
) -> HTMLResponse:
    """Request password reset."""
    if is_htmx:
        return render_template(
            request=request, 
            response=response,
            headers={'HX-Retarget': 'body', 'HX-Push-Url': '/admin/reset-password/sent/'},
            template_name="site/pages/auth/password_reset_email_sent.html",
        )

    return RedirectResponse(url="/admin/reset-password/sent/")


@router.get(
    "/reset-password/sent/", 
    response_class=HTMLResponse,
    dependencies=[Depends(push_htmx_history)],
)
def paswword_reset_form_success(
    request: Request,
    response: Response,
    is_htmx: Annotated[bool, Depends(check_htmx_request)],
) -> HTMLResponse:
    """Perform user signup."""
    return render_template(
        request=request, 
        response=response,
        headers={'HX-Retarget': 'body'},
        template_name="site/pages/auth/password_reset_email_sent.html"
    )


@router.get(
    "/login/",
    dependencies=[Depends(push_htmx_history)],
    response_class=HTMLResponse
)
def admin_login_page(
    request: Request,
    response: Response,
    is_htmx: Annotated[bool, Depends(check_htmx_request)],
)  -> HTMLResponse:
    """Render login page."""
    if is_htmx:
        return render_template(
            request=request,
            response=response,
            template_name="site/pages/auth/fragments/admin_login.html",
        )

    return render_template(
        request=request,
        response=response,
        template_name="site/pages/auth/admin_login.html"
    )


@router.post("/login/", response_class=HTMLResponse)
def admin_login_form(
    request: Request,
    response: Response,
    is_htmx: Annotated[bool, Depends(check_htmx_request)],
    user: Annotated[AdminUser, Depends(admin_user_login_service)],
) -> HTMLResponse:
    """Process admin user login form."""
    if is_htmx:
        return render_template(
            request=request,
            response=response,
            headers={'HX-Retarget': 'body', 'HX-Push-Url': '/admin/dashboard/', 'HX-Redirect': '/admin/dashboard/'},
            template_name="site/pages/admin/admin_dashboard.html"
        )
    return RedirectResponse(url="/admin/dashboard/")

