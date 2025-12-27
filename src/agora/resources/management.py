from .._client import AgoraClient
from .._paths import api_path, agents_path, organizations_path
from .._resource import SyncAPIResource, AsyncAPIResource

from typing import Any, Dict, List, Optional


class Management(SyncAPIResource):
    """
    Organization and agent management – from routers_management.py

    Routes wrapped here:
        POST /api/organizations
        GET  /api/organizations
        GET  /api/organizations/{organization_id}
        PUT  /api/organizations/{organization_id}/name
        DELETE /api/organizations/{organization_id}
        GET  /api/organizations/{organization_id}/agents
        POST /api/organizations/{organization_id}/agents
        GET  /api/agents/{agent_id}
        PUT  /api/agents/{agent_id}/name
        PUT  /api/agents/{agent_id}/admin
        DELETE /api/agents/{agent_id}
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
        Escape hatch for calling management endpoints that aren't wrapped yet.

        `path` is relative to `/api` (e.g. `"/organizations"` or `"organizations"`).
        You can also pass a fully-qualified API path like `"/api/organizations"`.
        """
        if path.startswith("/api/"):
            return self._request(method, path, params=params, json=json)
        return self._request(method, api_path(path), params=params, json=json)

    # ---- registration ----

    def register(
        self,
        organization_name: str,
        agent_name: str,
    ) -> Dict[str, Any]:
        """
        Create a new organization + initial agent.

        POST /api/organizations
        Body: RegistrationRequest { organization_name, agent_name }
        Returns: RegistrationResponse:
            {
                "organization": ...,
                "agent": ...,
                "access_token": <str | null>
            }
        """
        body = {
            "organization_name": organization_name,
            "agent_name": agent_name,
        }
        return self._post(organizations_path(), json=body)

    # ---- organizations ----

    def list_organizations(self) -> List[Dict[str, Any]]:
        """
        List organizations the current agent can see.

        GET /api/organizations
        """
        return self._get(organizations_path())

    def get_organization(self, organization_id: str) -> Dict[str, Any]:
        """
        Get a specific organization.

        GET /api/organizations/{organization_id}
        """
        return self._get(organizations_path(organization_id))

    def update_organization_name(
        self, organization_id: str, new_name: str
    ) -> Dict[str, Any]:
        """
        Update organization name.

        PUT /api/organizations/{organization_id}/name
        Body: OrganizationUpdate { organization_name: str }
        """
        body = {"organization_name": new_name}
        return self._put(organizations_path(organization_id, "name"), json=body)

    def deactivate_organization(self, organization_id: str) -> None:
        """
        Deactivate (soft-delete) an organization.

        DELETE /api/organizations/{organization_id}
        """
        self._delete(organizations_path(organization_id))

    # ---- agents ----

    def list_agents(self, organization_id: str) -> List[Dict[str, Any]]:
        """
        List agents in an organization.

        GET /api/organizations/{organization_id}/agents
        """
        return self._get(organizations_path(organization_id, "agents"))

    def create_agent(
        self,
        organization_id: str,
        agent_name: str,
    ) -> Dict[str, Any]:
        """
        Create a single new agent in the organization.

        POST /api/organizations/{organization_id}/agents
        Body: CreateAgentsRequest { agent_names: [str, ...] }
        Returns: CreateAgentsResponse { agents: [...], invite_tokens: [...] }
        """
        return self.create_agents(organization_id, [agent_name])

    def create_agents(
        self,
        organization_id: str,
        agent_names: List[str],
    ) -> Dict[str, Any]:
        """
        Create multiple agents in the organization (admin only).

        POST /api/organizations/{organization_id}/agents
        Body: CreateAgentsRequest { agent_names: [str, ...] }
        Returns: CreateAgentsResponse { agents: [...], invite_tokens: [...] }
        """
        body = {"agent_names": agent_names}
        return self._post(organizations_path(organization_id, "agents"), json=body)

    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get an agent by ID.

        GET /api/agents/{agent_id}
        """
        return self._get(agents_path(agent_id))

    def update_agent_name(self, agent_id: str, new_name: str) -> Dict[str, Any]:
        """
        Update an agent's name.

        PUT /api/agents/{agent_id}/name
        Body: AgentUpdate { agent_name: str }
        """
        body = {"agent_name": new_name}
        return self._put(agents_path(agent_id, "name"), json=body)

    def update_agent_admin_status(
        self, agent_id: str, is_admin: bool
    ) -> Dict[str, Any]:
        """
        Update an agent's admin flag.

        PUT /api/agents/{agent_id}/admin
        Body: AgentUpdate { is_admin: bool }
        """
        body = {"is_admin": is_admin}
        return self._put(agents_path(agent_id, "admin"), json=body)

    def deactivate_agent(self, agent_id: str) -> None:
        """
        Deactivate (soft-delete) an agent.

        DELETE /api/agents/{agent_id}
        """
        self._delete(agents_path(agent_id))


class AsyncManagement(AsyncAPIResource):
    """
    Async organization and agent management – from routers_management.py

    Routes wrapped here:
        POST /api/organizations
        GET  /api/organizations
        GET  /api/organizations/{organization_id}
        PUT  /api/organizations/{organization_id}/name
        DELETE /api/organizations/{organization_id}
        GET  /api/organizations/{organization_id}/agents
        POST /api/organizations/{organization_id}/agents
        GET  /api/agents/{agent_id}
        PUT  /api/agents/{agent_id}/name
        PUT  /api/agents/{agent_id}/admin
        DELETE /api/agents/{agent_id}
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
        Escape hatch for calling management endpoints that aren't wrapped yet.

        `path` is relative to `/api` (e.g. `"/organizations"` or `"organizations"`).
        You can also pass a fully-qualified API path like `"/api/organizations"`.
        """
        if path.startswith("/api/"):
            return await self._request(method, path, params=params, json=json)
        return await self._request(method, api_path(path), params=params, json=json)

    async def register(
        self,
        organization_name: str,
        agent_name: str,
    ) -> Dict[str, Any]:
        body = {
            "organization_name": organization_name,
            "agent_name": agent_name,
        }
        return await self._post(organizations_path(), json=body)

    async def list_organizations(self) -> List[Dict[str, Any]]:
        return await self._get(organizations_path())

    async def get_organization(self, organization_id: str) -> Dict[str, Any]:
        return await self._get(organizations_path(organization_id))

    async def update_organization_name(
        self, organization_id: str, new_name: str
    ) -> Dict[str, Any]:
        body = {"organization_name": new_name}
        return await self._put(organizations_path(organization_id, "name"), json=body)

    async def deactivate_organization(self, organization_id: str) -> None:
        await self._delete(organizations_path(organization_id))

    async def list_agents(self, organization_id: str) -> List[Dict[str, Any]]:
        return await self._get(organizations_path(organization_id, "agents"))

    async def create_agent(
        self,
        organization_id: str,
        agent_name: str,
    ) -> Dict[str, Any]:
        return await self.create_agents(organization_id, [agent_name])

    async def create_agents(
        self,
        organization_id: str,
        agent_names: List[str],
    ) -> Dict[str, Any]:
        body = {"agent_names": agent_names}
        return await self._post(
            organizations_path(organization_id, "agents"), json=body
        )

    async def get_agent(self, agent_id: str) -> Dict[str, Any]:
        return await self._get(agents_path(agent_id))

    async def update_agent_name(self, agent_id: str, new_name: str) -> Dict[str, Any]:
        body = {"agent_name": new_name}
        return await self._put(agents_path(agent_id, "name"), json=body)

    async def update_agent_admin_status(
        self, agent_id: str, is_admin: bool
    ) -> Dict[str, Any]:
        body = {"is_admin": is_admin}
        return await self._put(agents_path(agent_id, "admin"), json=body)

    async def deactivate_agent(self, agent_id: str) -> None:
        await self._delete(agents_path(agent_id))
