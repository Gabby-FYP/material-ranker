from fastapi import HTTPException


class BadRequestError(HTTPException):
    """Bad request exception."""


class ServiceError(HTTPException):
    """Service error exception."""

    def __init__(self, status_code, detail = None, headers = None, title = None):
        self.title = title or "Service Unavailable"
        super().__init__(status_code, detail, headers)
