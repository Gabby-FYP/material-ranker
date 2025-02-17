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
    headers: dict[str, str] | None = None,
) -> HTMLResponse:
    """Render a template."""
    context = context or {}
    headers = headers or {}
    headers.update(**dict(response.headers))
    context["request"] = request    
    return templates.TemplateResponse(
        template_name,
        context=context,
        headers=headers,
    )


def render_email_template(
    template_name: str,
    context: dict[str, Any],
) -> str:
    """Render email template."""
    return templates.get_template(template_name).render(**context)
