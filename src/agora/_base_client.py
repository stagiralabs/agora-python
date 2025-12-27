import abc
from typing import Any, Dict, Optional, Sequence, Tuple, Union

ParamsType = Optional[Union[Dict[str, Any], Sequence[Tuple[str, Any]]]]


class SyncClient(abc.ABC):
    """
    Minimal interface for synchronous clients.

    Subclasses implement `_request`, these helpers wrap common HTTP verbs.
    """

    @abc.abstractmethod
    def _request(
        self,
        method: str,
        path: str,
        *,
        params: ParamsType = None,
        json: Optional[Any] = None,
    ) -> Any:
        raise NotImplementedError

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


class AsyncClient(abc.ABC):
    """
    Minimal interface for async clients.

    Subclasses implement `_request`, helpers wrap common HTTP verbs.
    """

    @abc.abstractmethod
    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: ParamsType = None,
        json: Optional[Any] = None,
    ) -> Any:
        raise NotImplementedError

    async def _get(self, path: str, *, params: ParamsType = None) -> Any:
        return await self._request("GET", path, params=params)

    async def _post(
        self,
        path: str,
        *,
        json: Optional[Any] = None,
        params: ParamsType = None,
    ) -> Any:
        return await self._request("POST", path, params=params, json=json)

    async def _delete(self, path: str, *, params: ParamsType = None) -> Any:
        return await self._request("DELETE", path, params=params)

    async def _put(
        self,
        path: str,
        *,
        json: Optional[Any] = None,
        params: ParamsType = None,
    ) -> Any:
        return await self._request("PUT", path, params=params, json=json)
