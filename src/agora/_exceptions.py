from typing import Any, Optional, Type, Union

__all__ = [
    "AgoraError",
    "AgoraHTTPError",
    "BadRequestError",
    "UnauthorizedError",
    "ForbiddenError",
    "NotFoundError",
    "ConflictError",
    "ValidationError",
    "RateLimitError",
    "ClientError",
    "ServerError",
    "exception_from_response",
]


class AgoraError(Exception):
    """Generic Agora SDK error."""

    def __init__(
        self,
        message: Union[str, int] = "",
        status_code: Optional[int] = None,
        payload: Any = None,
    ) -> None:
        # Backward compatible with legacy positional usage:
        # AgoraError(status_code, message, payload)
        if isinstance(message, int):
            status_code, message = message, status_code or ""

        self.message = str(message) if message is not None else ""
        self.status_code = status_code
        self.payload = payload
        super().__init__(self.message)


class AgoraHTTPError(AgoraError):
    """HTTP error raised for non-2xx responses from the Agora backend."""


class ClientError(AgoraHTTPError):
    """4xx error responses."""


class ServerError(AgoraHTTPError):
    """5xx error responses."""


class BadRequestError(ClientError):
    """400 Bad Request."""


class UnauthorizedError(ClientError):
    """401 Unauthorized."""


class ForbiddenError(ClientError):
    """403 Forbidden."""


class NotFoundError(ClientError):
    """404 Not Found."""


class ConflictError(ClientError):
    """409 Conflict."""


class ValidationError(ClientError):
    """422 Unprocessable Entity."""


class RateLimitError(ClientError):
    """429 Too Many Requests."""


def exception_from_response(
    status_code: int,
    message: str,
    payload: Any,
) -> AgoraHTTPError:
    exc_map: dict[int, Type[AgoraHTTPError]] = {
        400: BadRequestError,
        401: UnauthorizedError,
        403: ForbiddenError,
        404: NotFoundError,
        409: ConflictError,
        422: ValidationError,
        429: RateLimitError,
    }
    if status_code in exc_map:
        exc_cls = exc_map[status_code]
    elif 500 <= status_code <= 599:
        exc_cls = ServerError
    elif 400 <= status_code <= 499:
        exc_cls = ClientError
    else:
        exc_cls = AgoraHTTPError

    return exc_cls(message=message, status_code=status_code, payload=payload)
