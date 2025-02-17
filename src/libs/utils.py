from typing import Literal


def parse_html_form_field_error(
    error_level: Literal['info', 'warning', 'error'],
    message: str,
) -> str:
    """Render error message."""
    error_classes = {
        'info': 'text-info',
        'warning': 'text-warning',
        'error': 'text-danger',
    }

    return f'<span class="{error_classes[error_level]}">{message}</span>'


def parse_html_form_error(
    error_level: Literal['info', 'warning', 'error'],
    message: str,
) -> str:
    """Render a generic error message."""
    error_classes = {
        'info': 'alert-info',
        'warning': 'alert-warning',
        'error': 'alert-danger',
    }

    return f"""
    <div class="alert {error_classes[error_level]} alert-dismissible" role="alert">
    {message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
    """


def parse_html_toast_message(
    error_level: Literal['info', 'warning', 'error'],
    message: str,
    title: str,
) -> str:
    """Render html toast message."""
    error_classes = {
        'info': 'bg-info',
        'warning': 'bg-warning',
        'error': 'bg-danger',
    }

    return f"""
        <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
              <span class="rounded me-2 {error_classes[error_level]} p-2"></span>
              <strong class="me-auto">{title}</strong>
              <small class="text-body-secondary">11 mins ago</small>
              <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">{message}</div>
        </div>
    """
