from typing import Annotated
from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from src.admin.schemas import CreateAdminUserFormValidate
from src.admin.services import (
    admin_request_password_reset_service, 
    admin_user_login_service, 
    create_new_admin_users, 
    delete_admin_user, 
    get_all_admin_users,
)
from src.core.dependecies import (
    check_htmx_request, 
    push_htmx_history, 
    require_authenticated_admin_user_session, 
    require_superuser,
)
from src.core.jinja2 import render_template
from src.models import AdminUser
from src.site.routes.schemas import PageVariable


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
        context={"user": adminuser, 'pageVariable': PageVariable(active_nav='DASHBOARD')},
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
            template_name="site/pages/admin/admin_dashboard.html",
            context={'user': user, 'pageVariable': PageVariable(active_nav='DASHBOARD')}
        )

    return RedirectResponse(url="/admin/dashboard/")


@router.get(
    "/logout/", 
    response_class=HTMLResponse,
    dependencies=[Depends(push_htmx_history)],
)
def logout_success(
    request: Request,
    response: Response,
    is_htmx: Annotated[bool, Depends(check_htmx_request)],
) -> HTMLResponse:
    """Perform user logout."""
    if is_htmx:
        return render_template(
            request=request, 
            response=response,
            headers={'HX-Retarget': 'body', 'HX-Push-Url': '/', 'HX-Redirect': '/'},
            template_name="site/pages/landing.html",
        )

    return RedirectResponse(url="/")


@router.get("/users/", response_class=HTMLResponse)
def admin_user_list(
    request: Request,
    response: Response,
    user: Annotated[AdminUser, Depends(require_superuser)],
    users: Annotated[list[AdminUser], Depends(get_all_admin_users)]
) -> HTMLResponse:
    """Render the lists of all admin users """
    return render_template(
        request=request,
        response=response,
        template_name="site/pages/admin/create_admin.html",
        context={
            "user": user,
            "users": users,
            'pageVariable': PageVariable(active_nav='ADMIN_USERS')
        },
    )


@router.post("/users/", response_class=HTMLResponse)
def create_new_admin_user_form(
    request: Request,
    response: Response,
    user: Annotated[AdminUser, Depends(require_superuser)],
    new_user: Annotated[AdminUser, Depends(create_new_admin_users)],
    users: Annotated[list[AdminUser], Depends(get_all_admin_users)]
) -> HTMLResponse:
    """Add a new admin user """
    return render_template(
        request=request,
        response=response,
        template_name="site/pages/admin/create_admin.html",
        headers={'HX-Retarget': 'body'},
        context={
            "user": user,
            "users": users,
            'pageVariable': PageVariable(active_nav='ADMIN_USERS')
        },
    )


@router.patch("/users/validate/", response_class=HTMLResponse)
def validate_signup_form(
    request: Request,
    response: Response,
    data: Annotated[CreateAdminUserFormValidate, Form()]
) -> HTMLResponse:
    """Validate user signup form."""
    return HTMLResponse('')


@router.delete("/users/{user_id}/", response_class=HTMLResponse)
def delete_admin_user_form(
    request: Request,
    response: Response,
    user: Annotated[AdminUser, Depends(require_superuser)],
    _: Annotated[AdminUser, Depends(delete_admin_user)],
    users: Annotated[list[AdminUser], Depends(get_all_admin_users)]
) -> HTMLResponse:
    """Add a new admin user """
    return render_template(
        request=request,
        response=response,
        template_name="site/pages/admin/create_admin.html",
        headers={'HX-Retarget': 'body'},
        context={
            "user": user,
            "users": users,
            'pageVariable': PageVariable(active_nav='ADMIN_USERS')
        },
    )


@router.get("/materials/", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    response: Response,
    adminuser: Annotated[AdminUser, Depends(require_authenticated_admin_user_session)]
) -> HTMLResponse:
    """Render the admin material page"""
    return render_template(
        request=request,
        response=response,
        template_name="site/pages/admin/materials.html",
        context={"user": adminuser, 'pageVariable': PageVariable(active_nav='MATERIAL')},
    )


@router.get("/reccommendation/", response_class=HTMLResponse)
def admin_recommendation(
    request: Request,
    response: Response,
    adminuser: Annotated[AdminUser, Depends(require_authenticated_admin_user_session)]
) -> HTMLResponse:
    """Render the reccommendation page"""
    return render_template(
        request=request,
        response=response,
        template_name="site/pages/admin/reccommendation.html",
        context={"user": adminuser, 'pageVariable': PageVariable(active_nav='RECOMMENDATION')},
    )
