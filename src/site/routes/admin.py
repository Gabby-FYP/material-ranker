from typing import Annotated
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse

from src.core.dependecies import require_authenticated_admin_user_session
from src.core.jinja2 import render_template
from src.models import AdminUser


router = APIRouter()

@router.get("/", response_class=HTMLResponse)
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