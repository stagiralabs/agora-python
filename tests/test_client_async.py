import asyncio
from typing import Any, Dict

import pytest

from agora import AsyncAgoraClient
from agora._exceptions import UnauthorizedError


class DummyAsyncResponse:
    def __init__(self, status_code: int, payload: Any, is_error: bool = False) -> None:
        self.status_code = status_code
        self._payload = payload
        self.is_error = is_error
        self.text = str(payload)

    def json(self) -> Any:
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


def test_async_request_maps_unauthorized(monkeypatch) -> None:
    client = AsyncAgoraClient(base_url="http://example.test", token="token")

    async def fake_request(**kwargs: Dict[str, Any]) -> DummyAsyncResponse:
        return DummyAsyncResponse(401, {"detail": "bad token"}, is_error=True)

    monkeypatch.setattr(client._session, "request", fake_request)
    with pytest.raises(UnauthorizedError):
        asyncio.run(client._request("GET", "/api/auth/me"))

    asyncio.run(client.aclose())


def test_async_set_and_clear_token() -> None:
    client = AsyncAgoraClient(base_url="http://example.test", token="token")
    assert client._session.headers["Authorization"] == "Bearer token"

    client.set_token("next")
    assert client._session.headers["Authorization"] == "Bearer next"

    client.clear_token()
    assert "Authorization" not in client._session.headers

    asyncio.run(client.aclose())
