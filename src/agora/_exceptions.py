from typing import Any

__all__ = [
    "AgoraError"
]

# TODO: make errors more expressive
class AgoraError(Exception):
    """Generic error raised for non-2xx responses from the Agora backend."""

    def __init__(self, status_code: int, message: str, payload: Any | None = None):
        super().__init__(f"[{status_code}] {message}")
        self.status_code = status_code
        self.message = message
        self.payload = payload