from typing import Annotated
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse

from src.core.dependecies import check_htmx_request, push_htmx_history, require_authenticated_user_session
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

@router.get(
    "/reccommendation_history/", 
    response_class=HTMLResponse,
    dependencies=[Depends(push_htmx_history)],
)
def reccommendation_history_page(
    request: Request,
    response: Response,
    is_htmx: Annotated[bool, Depends(check_htmx_request)],
) -> HTMLResponse:
    """Render recommendation_history page."""
    if is_htmx:
        return render_template(
            request=request,
            response=response,
            template_name="site/pages/user/reccommendation_history.html",
        )

    return render_template(
        request=request,
        response=response,
        template_name="site/pages/user/reccommendation_history.html"
    )



@router.get(
    "/recommendation/", 
    response_class=HTMLResponse,
    dependencies=[Depends(push_htmx_history)],
)
def recommendation_page(
    request: Request,
    response: Response,
    is_htmx: Annotated[bool, Depends(check_htmx_request)],
) -> HTMLResponse:
    """Render recommendation page."""
    if is_htmx:
        return render_template(
            request=request,
            response=response,
            template_name="site/pages/user/recommendation.html",
        )

    return render_template(
        request=request,
        response=response,
        template_name="site/pages/user/recommendation.html"
    )



