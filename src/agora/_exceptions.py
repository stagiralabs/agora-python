from typing import Any

__all__ = [
    "AgoraError"
]

# TODO: make errors more expressive
class AgoraError(Exception):
    """Generic error raised for non-2xx responses from the Agora backend."""
    pass