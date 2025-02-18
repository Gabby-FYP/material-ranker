from typing import Annotated
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse

from src.core.dependecies import require_authenticated_user_session
from src.core.jinja2 import render_template
from src.models import User


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def cource_materials(
    request: Request,
    response: Response,
    user: Annotated[User, Depends(require_authenticated_user_session)]
) -> HTMLResponse:
    """Render list cource materials page."""
    return render_template(
        request=request,
        response=response,
        template_name="site/pages/user/cource_materials.html",
        context={"user": user},
    )
