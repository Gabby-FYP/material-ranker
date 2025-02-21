from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request, Response, Depends, Form
from src.core.dependecies import check_htmx_request, push_htmx_history
from src.core.jinja2 import render_template
from typing import Annotated

from src.models import AdminUser, User
from src.users.services import admin_request_password_reset_service, admin_user_login_service, request_password_reset_service, reset_password_service, user_login_service, user_signup_service, verify_user_email_service
from src.users.schemas import PasswordResetFormValidate, UserSignupFormValidate


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
    is_htmx: Annotated[bool, Depends(check_htmx_request)],
    user: Annotated[User, Depends(user_signup_service)]
) -> HTMLResponse:
    """Perform user signup."""
    if is_htmx:
        return render_template(
            request=request, 
            response=response,
            headers={'HX-Retarget': 'body', 'HX-Push-Url': '/signup/success/'},
            template_name="site/pages/auth/signup_successful.html",
        )

    return RedirectResponse(url="/signup/success/")

@router.patch(
    "/signup/validate/",
    response_class=HTMLResponse,
)
def validate_signup_form(
    request: Request,
    response: Response,
    data: Annotated[UserSignupFormValidate, Form()]
) -> HTMLResponse:
    """Validate user signup form."""
    return HTMLResponse('')



@router.get(
    "/signup/success/", 
    response_class=HTMLResponse,
    dependencies=[Depends(push_htmx_history)],
)
def signup_success(
    request: Request,
    response: Response,
    is_htmx: Annotated[bool, Depends(check_htmx_request)],
) -> HTMLResponse:
    """Perform user signup."""
    return render_template(
        request=request, 
        response=response,
        headers={'HX-Retarget': 'body'},
        template_name="site/pages/auth/signup_successful.html"
    )


@router.get("/verify-email/{email_token}/", response_class=HTMLResponse)
def email_verification_page(
    request: Request,
    response: Response,
    user: Annotated[User | None, Depends(verify_user_email_service)],
) -> HTMLResponse:
    """Verify a users email address."""
    return render_template(
        request=request, 
        response=response,
        context={'user': user},
        template_name="site/pages/auth/email_verified.html",
    )


@router.get(
    "/login/", 
    dependencies=[Depends(push_htmx_history)],
    response_class=HTMLResponse
)
def user_login_page(
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


@router.post("/login/", response_class=HTMLResponse)
def user_login_form(
    request: Request,
    response: Response,
    is_htmx: Annotated[bool, Depends(check_htmx_request)],
    user: Annotated[User, Depends(user_login_service)],
) -> HTMLResponse:
    """Process user login form."""
    if is_htmx:
        return render_template(
            request=request, 
            response=response,
            headers={'HX-Retarget': 'body', 'HX-Push-Url': '/materials/', 'HX-Redirect': '/materials/'},
            template_name="site/pages/user/cource_materials.html",
        )

    return RedirectResponse(url="/materials/")


@router.get(
    "/admin_login/", 
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


@router.post("/admin_login/", response_class=HTMLResponse)
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
            headers={'HX-Retarget': 'body', 'HX-Push-Url': '/admin_dashboard/', 'HX-Redirect': '/admin_dashboard/'},
            template_name="site/pages/admin/admin_dashboard.html"
        )
    return RedirectResponse(url="/admin_dashboard/")



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


@router.post("/reset-password/", response_class=HTMLResponse)
def paswword_reset_form(
    request: Request,
    response: Response,
    is_htmx: Annotated[bool, Depends(check_htmx_request)],
    _: Annotated[User, Depends(request_password_reset_service)]
) -> HTMLResponse:
    """Request password reset."""
    if is_htmx:
        return render_template(
            request=request, 
            response=response,
            headers={'HX-Retarget': 'body', 'HX-Push-Url': '/reset-password/sent/'},
            template_name="site/pages/auth/password_reset_email_sent.html",
        )

    return RedirectResponse(url="/reset-password/sent/")


@router.get(
        "/admin_reset_password/",
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


@router.post("/admin_reset_password/", response_class=HTMLResponse)
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
            headers={'HX-Retarget': 'body', 'HX-Push-Url': '/reset-password/sent/'},
            template_name="site/pages/auth/password_reset_email_sent.html",
        )

    return RedirectResponse(url="/reset-password/sent/")




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
    "/reset-password/set-password/{reset_token}", 
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

@router.patch(
    "/reset-password/set-password/{reset_token}", 
    response_class=HTMLResponse,
    dependencies=[Depends(push_htmx_history)],
)
def password_reset_set_password_form_validate(
    request: Request,
    response: Response,
    is_htmx: Annotated[bool, Depends(check_htmx_request)],
    data: Annotated[PasswordResetFormValidate, Form()]
) -> HTMLResponse:
    """Render password reset set password page."""
    return HTMLResponse('')

@router.post(
    "/reset-password/set-password/{reset_token}", 
    response_class=HTMLResponse,
    dependencies=[Depends(push_htmx_history)],
)
def password_reset_set_password_form(
    request: Request,
    response: Response,
    is_htmx: Annotated[bool, Depends(check_htmx_request)],
    _: Annotated[None, Depends(reset_password_service)],
) -> HTMLResponse:
    """Render password reset set password page."""
    if is_htmx:
        return render_template(
            request=request, 
            response=response,
            headers={'HX-Retarget': 'body', 'HX-Push-Url': '/login/'},
            template_name="site/pages/auth/login.html",
        )

    return RedirectResponse(url="/login/")
