from typing import Any, Dict

import pytest

from agora import AgoraClient
from agora._exceptions import (
    UnauthorizedError,
    ServerError,
)


class DummyResponse:
    def __init__(self, status_code: int, payload: Any, ok: bool = True) -> None:
        self.status_code = status_code
        self._payload = payload
        self.ok = ok
        self.text = str(payload)

    def json(self) -> Any:
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


def test_request_returns_payload(monkeypatch) -> None:
    client = AgoraClient(base_url="http://example.test", token="token")

    def fake_request(**kwargs: Dict[str, Any]) -> DummyResponse:
        return DummyResponse(200, {"ok": True}, ok=True)

    monkeypatch.setattr(client._session, "request", fake_request)
    assert client._request("GET", "/api/ping") == {"ok": True}


def test_request_handles_204(monkeypatch) -> None:
    client = AgoraClient(base_url="http://example.test", token="token")

    def fake_request(**kwargs: Dict[str, Any]) -> DummyResponse:
        return DummyResponse(204, None, ok=True)

    monkeypatch.setattr(client._session, "request", fake_request)
    assert client._request("GET", "/api/empty") is None


def test_request_maps_unauthorized(monkeypatch) -> None:
    client = AgoraClient(base_url="http://example.test", token="token")

    def fake_request(**kwargs: Dict[str, Any]) -> DummyResponse:
        return DummyResponse(401, {"detail": "bad token"}, ok=False)

    monkeypatch.setattr(client._session, "request", fake_request)
    with pytest.raises(UnauthorizedError) as exc_info:
        client._request("GET", "/api/auth/me")

    assert exc_info.value.status_code == 401
    assert exc_info.value.message == "bad token"


def test_request_maps_server_error_with_text_payload(monkeypatch) -> None:
    client = AgoraClient(base_url="http://example.test", token="token")

    def fake_request(**kwargs: Dict[str, Any]) -> DummyResponse:
        return DummyResponse(500, ValueError("no json"), ok=False)

    monkeypatch.setattr(client._session, "request", fake_request)
    with pytest.raises(ServerError) as exc_info:
        client._request("GET", "/api/boom")

    assert exc_info.value.status_code == 500
    assert "no json" in exc_info.value.message


def test_set_and_clear_token() -> None:
    client = AgoraClient(base_url="http://example.test", token="token")
    assert client._session.headers["Authorization"] == "Bearer token"

    client.set_token("next")
    assert client._session.headers["Authorization"] == "Bearer next"

    client.clear_token()
    assert "Authorization" not in client._session.headers
