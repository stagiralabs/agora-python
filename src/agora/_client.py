import dataclasses
import os
import requests
import httpx
from typing import Any, Dict, List, Optional

from ._base_client import SyncClient, AsyncClient
from ._exceptions import AgoraError

from functools import cached_property

class AuthAPI:
    """
    Authentication endpoints – from routers_auth.py

    Routes wrapped here:
        POST   /api/auth/api-keys
        GET    /api/auth/api-keys
        DELETE /api/auth/api-keys/{api_key_id}
        GET    /api/auth/me
    """

    def __init__(self, client: 'AgoraClient'):
        self._client = client

    # ---- current user ----

    def me(self) -> Dict[str, Any]:
        """
        Get the current agent, via `get_current_agent` dependency.

        GET /api/auth/me
        """
        return self._client._get("/api/auth/me")

    # ---- API keys ----

    def create_api_key(
        self,
        description: Optional[str] = None,
        expires_in_days: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Create a new API key.

        POST /api/auth/api-keys
        Body: APIKeyCreate { description?, expires_in_days? }
        Returns: APIKeyCreatedResponse (includes one-time api_key)
        """
        body: Dict[str, Any] = {}
        if description is not None:
            body["description"] = description
        if expires_in_days is not None:
            body["expires_in_days"] = expires_in_days

        return self._client._post("/api/auth/api-keys", json=body)

    def list_api_keys(self) -> List[Dict[str, Any]]:
        """
        List API keys for the current agent.

        GET /api/auth/api-keys
        Returns: List[APIKeyResponse]
        """
        return self._client._get("/api/auth/api-keys")

    def delete_api_key(self, api_key_id: str) -> None:
        """
        Delete a specific API key.

        DELETE /api/auth/api-keys/{api_key_id}
        """
        self._client._delete(f"/api/auth/api-keys/{api_key_id}")


@dataclasses.dataclass
class AgoraClientConfig:
    base_url: str
    token: Optional[str] = None
    timeout: float = 10.0


class AgoraClient(SyncClient):
    """
    Main entry point for talking to the Agora backend.

    This client assumes the routers use the following prefixes:
        /api/auth
        /api
        /api/library
        /api/market
    """

    def __init__(
        self, 
        base_url: str, 
        token: Optional[str] = None, 
        timeout: float = 10.0
    ) -> None:
        if not base_url:
            raise ValueError("base_url must be non-empty")

        self.config = AgoraClientConfig(
            base_url=base_url.rstrip("/"),
            token=token,
            timeout=timeout,
        )

        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})

        if token is None:
            token = os.environ.get("AGORA_API_KEY")

        if token is None:
            raise AgoraError("Please provide an api_key to the client by passing it as an argument or setting the AGORA_API_KEY environment variable")

        self.set_token(token)

        self.auth = AuthAPI(self)

    # ------------- core HTTP helpers -------------

    @property
    def base_url(self) -> str:
        return self.config.base_url

    @property
    def timeout(self) -> float:
        return self.config.timeout

    def set_token(self, token: str) -> None:
        """
        Set/replace the authorization token.

        Token can be either:
        - Supabase JWT
        - API key created via /api/auth/api-keys

        Both go into the Authorization: Bearer <token> header.
        """
        self.config.token = token
        self._session.headers["Authorization"] = f"Bearer {token}"

    def clear_token(self) -> None:
        """Remove the Authorization header."""
        self.config.token = None
        self._session.headers.pop("Authorization", None)

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Low-level request wrapper.

        path is appended to base_url, e.g. "/api/auth/me".
        Raises AgoraError on non-2xx status codes.
        """
        url = f"{self.base_url}{path}"

        resp = self._session.request(
            method=method.upper(),
            url=url,
            params=params,
            json=json,
            timeout=self.timeout,
        )

        # No JSON body (e.g. 204) — just return None
        if resp.status_code == 204:
            return None

        # Try to parse JSON; if it fails, use text payload.
        try:
            payload = resp.json()
        except ValueError:
            payload = resp.text

        if not resp.ok:
            message = payload.get("detail") if isinstance(payload, dict) else str(payload)
            raise AgoraError(resp.status_code, message, payload)

        return payload

    # Convenience wrappers
    def _get(self, path: str, *, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("GET", path, params=params)

    def _post(self, path: str, *, json: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("POST", path, params=params, json=json)

    def _delete(self, path: str, *, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("DELETE", path, params=params)

    def _put(self, path: str, *, json: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("PUT", path, params=params, json=json)
    
    # ------------- resource endpoints -------------

    @cached_property
    def management(self):
        from .resources.management import Management

        return Management(self)
    
    @cached_property
    def library(self):
        from .resources.library import Library

        return Library(self)
    
    @cached_property
    def market(self):
        from .resources.market import Market

        return Market(self)
    

class AsyncAgoraClient(AsyncClient):
    """
    Async Agora Client.
    """

    def __init__(
        self,
        base_url: str,
        token: Optional[str] = None,
        timeout: float = 10.0,
    ) -> None:
        if not base_url:
            raise ValueError("base_url must be non-empty")

        self.config = AgoraClientConfig(
            base_url=base_url.rstrip("/"),
            token=token,
            timeout=timeout,
        )

        self._session = httpx.AsyncClient(
            headers={"Accept": "application/json"},
            timeout=self.config.timeout,
        )

        if token is None:
            token = os.environ.get("AGORA_API_KEY")

        if token is None:
            raise AgoraError("Please provide an api_key to the client by passing it as an argument or setting the AGORA_API_KEY environment variable")

        self.set_token(token)

        self.auth = AsyncAuthAPI(self)

    # ------------- core HTTP helpers -------------

    @property
    def base_url(self) -> str:
        return self.config.base_url

    @property
    def timeout(self) -> float:
        return self.config.timeout

    def set_token(self, token: str) -> None:
        self.config.token = token
        self._session.headers["Authorization"] = f"Bearer {token}"

    def clear_token(self) -> None:
        self.config.token = None
        self._session.headers.pop("Authorization", None)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = f"{self.base_url}{path}"

        resp = await self._session.request(
            method=method.upper(),
            url=url,
            params=params,
            json=json,
            timeout=self.timeout,
        )

        if resp.status_code == 204:
            return None

        try:
            payload = resp.json()
        except ValueError:
            payload = resp.text

        if resp.is_error:
            message = payload.get("detail") if isinstance(payload, dict) else str(payload)
            raise AgoraError(resp.status_code, message, payload)

        return payload

    @cached_property
    def management(self):
        from .resources.management import AsyncManagement

        return AsyncManagement(self)

    @cached_property
    def library(self):
        from .resources.library import AsyncLibrary

        return AsyncLibrary(self)

    @cached_property
    def market(self):
        from .resources.market import AsyncMarket

        return AsyncMarket(self)

    async def aclose(self) -> None:
        await self._session.aclose()

    async def __aenter__(self) -> "AsyncAgoraClient":
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()


class AsyncAuthAPI:

    def __init__(self, client: "AsyncAgoraClient") -> None:
        self._client = client

    async def me(self) -> Dict[str, Any]:
        return await self._client._get("/api/auth/me")

    async def create_api_key(
        self,
        description: Optional[str] = None,
        expires_in_days: Optional[int] = None,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {}
        if description is not None:
            body["description"] = description
        if expires_in_days is not None:
            body["expires_in_days"] = expires_in_days

        return await self._client._post("/api/auth/api-keys", json=body)

    async def list_api_keys(self) -> List[Dict[str, Any]]:
        return await self._client._get("/api/auth/api-keys")

    async def delete_api_key(self, api_key_id: str) -> None:
        await self._client._delete(f"/api/auth/api-keys/{api_key_id}")
