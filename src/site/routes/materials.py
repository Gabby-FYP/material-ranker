from typing import Annotated
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse

from src.core.dependecies import check_htmx_request, push_htmx_history, require_authenticated_user_session
from src.core.jinja2 import render_template
from src.models import User
from src.site.routes.schemas import PageVariable


router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(push_htmx_history)], 
    response_class=HTMLResponse
)
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
        context={"user": user, "pageVariable": PageVariable(active_nav='DASHBOARD')},
    )


@router.get(
    "/reccommendation/", 
    response_class=HTMLResponse,
    dependencies=[Depends(push_htmx_history)],
)
def reccommendations_page(
    request: Request,
    response: Response,
    is_htmx: Annotated[bool, Depends(check_htmx_request)],
    user: Annotated[User, Depends(require_authenticated_user_session)]
) -> HTMLResponse:
    """Render recommendation_history page."""
    return render_template(
        request=request,
        response=response,
        template_name="site/pages/user/reccommendations.html",
        context={"user": user, "pageVariable": PageVariable(active_nav='RECOMMENDATION')},
    )
