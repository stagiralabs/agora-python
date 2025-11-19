from .._client import AgoraClient

class SyncAPIResource:
    _client: AgoraClient

    def __init__(self, client: AgoraClient) -> None:
        self._client = client
        self._delete = client.delete
        self._get = client.get
        self._post = client.post
        self._put = client.put
        self._request = client._request

class AsyncAPIResource:
    pass