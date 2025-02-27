from typing import Annotated, Any
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse

from src.core.dependecies import check_htmx_request, push_htmx_history, require_admin_or_user_access, require_authenticated_user_session
from src.core.jinja2 import render_template
from src.models import Material, User
from src.site.routes.schemas import PageVariable
from src.material.schemas import MaterailRecommendation
from src.material.services import create_material_service, user_material_list_service, user_material_recommendation_list


router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(push_htmx_history)], 
    response_class=HTMLResponse
)
def cource_materials(
    request: Request,
    response: Response,
    user: Annotated[User, Depends(require_authenticated_user_session)],
    materials: Annotated[list[Material], Depends(user_material_list_service)],
) -> HTMLResponse:
    """Render list cource materials page."""
    return render_template(
        request=request,
        response=response,
        template_name="site/pages/user/cource_materials.html",
        context={
            "user": user, 
            "materials": materials,
            "pageVariable": PageVariable(active_nav='DASHBOARD')
        },
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
    user: Annotated[User, Depends(require_authenticated_user_session)],
    user_recommedations:  Annotated[list[MaterailRecommendation], Depends(user_material_recommendation_list)]
) -> HTMLResponse:
    """Render recommendation_history page."""
    return render_template(
        request=request,
        response=response,
        template_name="site/pages/user/reccommendations.html",
        context={
            "user": user, 
            'recommendations': user_recommedations,
            "pageVariable": PageVariable(active_nav='RECOMMENDATION'),
        },
    )


@router.post("/reccommendation/", response_class=HTMLResponse) 
def create_a_material_recommendation(
    request: Request,
    response:  Response,
    is_htmx: Annotated[bool, Depends(check_htmx_request)],
    user: Annotated[User, Depends(require_authenticated_user_session)],
    new_recommendation:  Annotated[Material, Depends(create_material_service)],
    user_recommedations:  Annotated[list[MaterailRecommendation], Depends(user_material_recommendation_list)]
) -> HTMLResponse:
    """Submit a material recommendation."""
    if is_htmx:
        return render_template(
            request=request,
            response=response,
            headers={'HX-Retarget': 'body', 'HX-Redirect': '/materials/reccommendation/'},
            template_name="site/pages/user/reccommendations.html",
            context={
                'user': user,
                'recommendations': user_recommedations, 
                'pageVariable': PageVariable(active_nav='RECOMMENDATION')
            }
        )  

    return render_template(
        request=request,
        response=response,
        template_name="site/pages/user/reccommendations.html",
        context={
            "user": user,
            'recommendations': user_recommedations, 
            "pageVariable": PageVariable(active_nav='RECOMMENDATION')
        },
    )
 

@router.get(
    "/rate-materials/",
    response_class=HTMLResponse,
    dependencies=[Depends(push_htmx_history)],
)
def rate_materials_page(
    request: Request,
    response: Response,
    is_htmx: Annotated[bool, Depends(check_htmx_request)],
    user: Annotated[User, Depends(require_authenticated_user_session)]
) -> HTMLResponse:
    """Render rate materials page"""
    return render_template(
        request=request,
        response=response,
        template_name="site/pages/user/rate_material.html",
        context={"user": user, "pageVariable": PageVariable(active_nav='DASHBOARD')},
    )

