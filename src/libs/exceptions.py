from fastapi import HTTPException, status


class BadRequestError(HTTPException):
    """Bad request exception."""


class ServiceError(HTTPException):
    """Service error exception."""

    def __init__(self, status_code, detail = None, headers = None, title = None):
        self.title = title or "Service Unavailable"
        super().__init__(status_code, detail, headers)


class AuthenticationError(HTTPException):
    """Authentication error exception."""

    def __init__(self, status_code, detail = None, headers = None, title = None):
        super().__init__(status_code, detail, headers)
        self.title = title or "Authentication Error"
        self.status_code = status.HTTP_401_UNAUTHORIZED
