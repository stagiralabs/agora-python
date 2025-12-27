from typing import TYPE_CHECKING

from ._client import AgoraClient

if TYPE_CHECKING:
    from ._client import AsyncAgoraClient


class SyncAPIResource:
    _client: AgoraClient

    def __init__(self, client: AgoraClient) -> None:
        self._client = client
        self._request = client._request
        self._get = client._get
        self._post = client._post
        self._delete = client._delete
        self._put = client._put


class AsyncAPIResource:
    _client: "AsyncAgoraClient"

    def __init__(self, client: "AsyncAgoraClient") -> None:
        self._client = client
        self._request = client._request
        self._get = client._get
        self._post = client._post
        self._delete = client._delete
        self._put = client._put
