import warnings

from .._client import AgoraClient
from .._paths import library_path
from .._resource import SyncAPIResource, AsyncAPIResource

from typing import Any, Dict, List, Optional


def _library_params(
    *,
    project_id: Optional[str],
    repo_url: Optional[str],
    repo_rev: Optional[str],
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    if project_id:
        params["project_id"] = project_id
        if repo_url or repo_rev:
            warnings.warn(
                "repo_url/repo_rev are deprecated; use project_id instead.",
                DeprecationWarning,
                stacklevel=3,
            )
        return params
    if repo_url or repo_rev:
        warnings.warn(
            "repo_url/repo_rev are deprecated; use project_id instead.",
            DeprecationWarning,
            stacklevel=3,
        )
        if repo_url:
            params["repo_url"] = repo_url
        if repo_rev:
            params["repo_rev"] = repo_rev
        return params
    raise ValueError("project_id is required for this endpoint.")


class Library(SyncAPIResource):
    """
    Library mechanics proxy – from routers_library.py

    Routes wrapped here:
        GET  /api/library/health
        GET  /api/library/library
        GET  /api/library/repo_files
        GET  /api/library/library_file
        GET  /api/library/search
        GET  /api/library/search_all_repos
        GET  /api/library/target_file
        GET  /api/library/target_content
        POST /api/library/add_contribution
    """

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Escape hatch for calling library endpoints that aren't wrapped yet.

        `path` is relative to `/api/library` (e.g. `"/health"` or `"health"`).
        You can also pass a fully-qualified API path like `"/api/library/health"`.
        """
        if path.startswith("/api/"):
            return self._request(method, path, params=params, json=json)
        return self._request(method, library_path(path), params=params, json=json)

    def health(self) -> Dict[str, Any]:
        """GET /api/library/health"""
        return self._get(library_path("health"))

    def list_files(
        self,
        repo_url: Optional[str] = None,
        repo_rev: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all files in the library.

        GET /api/library/library
        Query: project_id (preferred), repo_url?, repo_rev?
        """
        params = _library_params(
            project_id=project_id, repo_url=repo_url, repo_rev=repo_rev
        )
        return self._get(library_path("library"), params=params)

    def list_repo_files(
        self,
        repo_url: Optional[str] = None,
        repo_rev: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all files in the repository (not just Library/).

        GET /api/library/repo_files
        Query: project_id (preferred), repo_url?, repo_rev?
        """
        params = _library_params(
            project_id=project_id, repo_url=repo_url, repo_rev=repo_rev
        )
        return self._get(library_path("repo_files"), params=params)

    def get_file(
        self,
        file_name: str,
        repo_url: Optional[str] = None,
        repo_rev: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get a specific file in the library.

        GET /api/library/library_file
        Query: file_name, project_id (preferred), repo_url?, repo_rev?
        """
        params = {"file_name": file_name}
        params.update(
            _library_params(project_id=project_id, repo_url=repo_url, repo_rev=repo_rev)
        )
        return self._get(library_path("library_file"), params=params)

    def search(
        self,
        query: str,
        k: int = 10,
        repo_url: Optional[str] = None,
        repo_rev: Optional[str] = None,
        search_mode: str = "syntactic",
        project_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search the library for code declarations.

        GET /api/library/search
        Query: query, k, search_mode, project_id (preferred), repo_url?, repo_rev?
        """
        params: Dict[str, Any] = {"query": query, "k": k, "search_mode": search_mode}
        params.update(
            _library_params(project_id=project_id, repo_url=repo_url, repo_rev=repo_rev)
        )
        return self._get(library_path("search"), params=params)

    def search_all_repos(
        self,
        query: str,
        k: int = 10,
        search_mode: str = "syntactic",
    ) -> List[Dict[str, Any]]:
        """
        Search across all cached repositories.

        GET /api/library/search_all_repos
        Query: query, k, search_mode
        """
        params: Dict[str, Any] = {"query": query, "k": k, "search_mode": search_mode}
        return self._get(library_path("search_all_repos"), params=params)

    def get_target_file(
        self,
        target_id: str,
    ) -> Dict[str, Any]:
        """
        Get the file backing a given target.

        GET /api/library/target_file
        Query: target_id
        """
        return self._get(library_path("target_file"), params={"target_id": target_id})

    def get_target_content(
        self,
        target_id: str,
    ) -> Dict[str, Any]:
        """
        Get the declaration content for a given target.

        GET /api/library/target_content
        Query: target_id
        """
        return self._get(
            library_path("target_content"), params={"target_id": target_id}
        )

    def add_contribution(
        self,
        name: str,
        file_content: str,
        repo_url: Optional[str] = None,
        repo_rev: Optional[str] = None,
        ephemeral: Optional[bool] = False,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Add a contribution to the library.

        POST /api/library/add_contribution
        Body: AddContributionRequest {
            name: str,
            file_content: str,
            project_id?: str,
            repo_url?: str,
            repo_rev?: str,
            ephemeral?: bool,
        }
        """
        body: Dict[str, Any] = {
            "name": name,
            "file_content": file_content,
        }
        body.update(
            _library_params(project_id=project_id, repo_url=repo_url, repo_rev=repo_rev)
        )
        if ephemeral is not None:
            body["ephemeral"] = ephemeral

        return self._post(library_path("add_contribution"), json=body)


class AsyncLibrary(AsyncAPIResource):
    """
    Async library mechanics proxy – from routers_library.py.
    """

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Escape hatch for calling library endpoints that aren't wrapped yet.

        `path` is relative to `/api/library` (e.g. `"/health"` or `"health"`).
        You can also pass a fully-qualified API path like `"/api/library/health"`.
        """
        if path.startswith("/api/"):
            return await self._request(method, path, params=params, json=json)
        return await self._request(method, library_path(path), params=params, json=json)

    async def health(self) -> Dict[str, Any]:
        return await self._get(library_path("health"))

    async def list_files(
        self,
        repo_url: Optional[str] = None,
        repo_rev: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        params = _library_params(
            project_id=project_id, repo_url=repo_url, repo_rev=repo_rev
        )
        return await self._get(library_path("library"), params=params)

    async def list_repo_files(
        self,
        repo_url: Optional[str] = None,
        repo_rev: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        params = _library_params(
            project_id=project_id, repo_url=repo_url, repo_rev=repo_rev
        )
        return await self._get(library_path("repo_files"), params=params)

    async def get_file(
        self,
        file_name: str,
        repo_url: Optional[str] = None,
        repo_rev: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"file_name": file_name}
        params.update(
            _library_params(project_id=project_id, repo_url=repo_url, repo_rev=repo_rev)
        )
        return await self._get(library_path("library_file"), params=params)

    async def search(
        self,
        query: str,
        k: int = 10,
        repo_url: Optional[str] = None,
        repo_rev: Optional[str] = None,
        search_mode: str = "syntactic",
        project_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"query": query, "k": k, "search_mode": search_mode}
        params.update(
            _library_params(project_id=project_id, repo_url=repo_url, repo_rev=repo_rev)
        )
        return await self._get(library_path("search"), params=params)

    async def search_all_repos(
        self,
        query: str,
        k: int = 10,
        search_mode: str = "syntactic",
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"query": query, "k": k, "search_mode": search_mode}
        return await self._get(library_path("search_all_repos"), params=params)

    async def get_target_file(
        self,
        target_id: str,
    ) -> Dict[str, Any]:
        return await self._get(library_path("target_file"), params={"target_id": target_id})

    async def get_target_content(
        self,
        target_id: str,
    ) -> Dict[str, Any]:
        return await self._get(
            library_path("target_content"), params={"target_id": target_id}
        )

    async def add_contribution(
        self,
        name: str,
        file_content: str,
        repo_url: Optional[str] = None,
        repo_rev: Optional[str] = None,
        ephemeral: Optional[bool] = False,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "name": name,
            "file_content": file_content,
        }
        body.update(
            _library_params(project_id=project_id, repo_url=repo_url, repo_rev=repo_rev)
        )
        if ephemeral is not None:
            body["ephemeral"] = ephemeral

        return await self._post(library_path("add_contribution"), json=body)
