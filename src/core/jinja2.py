from typing import Any
from fastapi import Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.core.config import settings

templates = Jinja2Templates(directory=settings.TEMPLATE_DIR)


def render_template(
    request: Request,
    response: Response,
    template_name: str,
    context: dict[str, Any] | None = None,
) -> HTMLResponse:
    """Render a template."""
    context = context or {}
    context["request"] = request
    return templates.TemplateResponse(
        template_name, 
        {"request": request, "context": context},
        headers=response.headers,
    )
