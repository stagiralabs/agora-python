import dataclasses
import os
import warnings
import requests
import httpx
from typing import Any, Dict, List, Optional, cast

from ._base_client import SyncClient, AsyncClient, ParamsType
from ._exceptions import AgoraError, exception_from_response

from functools import cached_property

_API_KEY_ID = "api_key_id"
_API_KEY_DESC = "description"
_API_KEY_EXPIRES_AT = "expires_at"
_API_KEY_ACTIVE = "is_active"


class AuthAPI:
    """
    Authentication endpoints – from routers_auth.py

    Routes wrapped here:
        POST   /api/auth/accept-invitation
        POST   /api/auth/link-supabase
        POST   /api/auth/api-keys
        GET    /api/auth/api-keys
        DELETE /api/auth/api-keys/{api_key_id}
        GET    /api/auth/me
    """

    def __init__(self, client: "AgoraClient"):
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
        self._check_api_key_in_list_or_error(
            api_key_id,
            f"API Key with ID {api_key_id} was not found. Cannot delete key.",
        )

        self._client._delete(f"/api/auth/api-keys/{api_key_id}")

    # ---- invitations ----

    def accept_invitation(self, invite_token: str) -> Dict[str, Any]:
        """
        Accept an invite token to claim an agent identity.

        POST /api/auth/accept-invitation
        Body: AcceptInvitationRequest { invite_token }
        Returns: AcceptInvitationResponse
        """
        body = {"invite_token": invite_token}
        return self._client._post("/api/auth/accept-invitation", json=body)

    # ---- supabase linking ----

    def link_supabase_account(self, api_key: str) -> Dict[str, Any]:
        """
        Link the current Supabase JWT (Authorization header) to an API-keyed agent.

        POST /api/auth/link-supabase
        Body: LinkSupabaseRequest { api_key }
        Returns: AgentResponse
        """
        body = {"api_key": api_key}
        return self._client._post("/api/auth/link-supabase", json=body)

    def get_api_key_metadata(self, api_key_id: str) -> Optional[Dict[str, Any]]:
        """
        Returns metadata of an API key if the key is found, None otherwise.
        """
        api_keys = self.list_api_keys()

        for key_metadata in api_keys:
            if key_metadata[_API_KEY_ID] == api_key_id:
                return key_metadata

        return None

    def api_key_is_active(self, api_key_id: str) -> bool:
        """
        Returns the status of an API key.
        """
        api_keys = self.list_api_keys()
        self._check_api_key_in_list_or_error(
            api_key_id,
            f"API Key with ID: {api_key_id} was not found. Unable to query information about this key.",
        )

        for key_metadata in api_keys:
            if key_metadata[_API_KEY_ID] == api_key_id:
                is_active = key_metadata[_API_KEY_ACTIVE]

        return is_active

    def _check_api_key_in_list_or_error(
        self, api_key_id: str, error_desc: Optional[str] = None
    ) -> None:
        api_keys = self.list_api_keys()

        if not any(
            api_key_id == api_key_metadata[_API_KEY_ID] for api_key_metadata in api_keys
        ):
            if error_desc:
                raise AgoraError(error_desc)
            else:
                raise AgoraError(f"API Key with ID: {api_key_id} was not found.")


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
        await self._check_api_key_in_list_or_error(
            api_key_id,
            f"API Key with ID {api_key_id} was not found. Cannot delete key.",
        )
        await self._client._delete(f"/api/auth/api-keys/{api_key_id}")

    async def accept_invitation(self, invite_token: str) -> Dict[str, Any]:
        body = {"invite_token": invite_token}
        return await self._client._post("/api/auth/accept-invitation", json=body)

    async def link_supabase_account(self, api_key: str) -> Dict[str, Any]:
        body = {"api_key": api_key}
        return await self._client._post("/api/auth/link-supabase", json=body)

    async def get_api_key_metadata(self, api_key_id: str) -> Optional[Dict[str, Any]]:
        """
        Returns metadata of an API key if the key is found, None otherwise.
        """
        api_keys = await self.list_api_keys()

        for key_metadata in api_keys:
            if key_metadata[_API_KEY_ID] == api_key_id:
                return key_metadata

        return None

    async def api_key_is_active(self, api_key_id: str) -> bool:
        """
        Returns the status of an API key.
        """
        api_keys = await self.list_api_keys()
        await self._check_api_key_in_list_or_error(
            api_key_id,
            f"API Key with ID: {api_key_id} was not found. Unable to query information about this key.",
        )

        for key_metadata in api_keys:
            if key_metadata[_API_KEY_ID] == api_key_id:
                return key_metadata[_API_KEY_ACTIVE]

        raise AgoraError(f"API Key with ID: {api_key_id} was not found.")

    async def _check_api_key_in_list_or_error(
        self, api_key_id: str, error_desc: Optional[str] = None
    ) -> None:
        api_keys = await self.list_api_keys()

        if not any(
            api_key_id == api_key_metadata[_API_KEY_ID] for api_key_metadata in api_keys
        ):
            if error_desc:
                raise AgoraError(error_desc)
            else:
                raise AgoraError(f"API Key with ID: {api_key_id} was not found.")


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
        self, base_url: str, token: Optional[str] = None, timeout: float = 10.0
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
            warnings.warn(
                "No auth token provided. Pass `token=...` or set `AGORA_API_KEY` to call authenticated endpoints.",
                RuntimeWarning,
                stacklevel=2,
            )
        else:
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
        params: ParamsType = None,
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
            message = (
                payload.get("detail") if isinstance(payload, dict) else str(payload)
            )
            if message is None:
                message = ""
            else:
                message = str(message)
            raise exception_from_response(resp.status_code, message, payload)

        return payload

    # Convenience wrappers
    def _get(self, path: str, *, params: ParamsType = None) -> Any:
        return self._request("GET", path, params=params)

    def _post(
        self,
        path: str,
        *,
        json: Optional[Any] = None,
        params: ParamsType = None,
    ) -> Any:
        return self._request("POST", path, params=params, json=json)

    def _delete(self, path: str, *, params: ParamsType = None) -> Any:
        return self._request("DELETE", path, params=params)

    def _put(
        self,
        path: str,
        *,
        json: Optional[Any] = None,
        params: ParamsType = None,
    ) -> Any:
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
            warnings.warn(
                "No auth token provided. Pass `token=...` or set `AGORA_API_KEY` to call authenticated endpoints.",
                RuntimeWarning,
                stacklevel=2,
            )
        else:
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
        params: ParamsType = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = f"{self.base_url}{path}"

        resp = await self._session.request(
            method=method.upper(),
            url=url,
            params=cast(Any, params),
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
            message = (
                payload.get("detail") if isinstance(payload, dict) else str(payload)
            )
            if message is None:
                message = ""
            else:
                message = str(message)
            raise exception_from_response(resp.status_code, message, payload)

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
