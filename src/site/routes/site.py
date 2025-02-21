from src.core.jinja2 import render_template
from fastapi import Request, Response
from fastapi.responses import HTMLResponse
from fastapi import APIRouter


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