from .resource import SyncAPIResource
from .._client import AgoraClient

from typing import Any, Dict, List

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

    def __init__(self, client: 'AgoraClient'):
        self._client = client

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
        return self._post("/api/organizations", json=body)

    # ---- organizations ----

    def list_organizations(self) -> List[Dict[str, Any]]:
        """
        List organizations the current agent can see.

        GET /api/organizations
        """
        return self._get("/api/organizations")

    def get_organization(self, organization_id: str) -> Dict[str, Any]:
        """
        Get a specific organization.

        GET /api/organizations/{organization_id}
        """
        return self._get(f"/api/organizations/{organization_id}")

    def update_organization_name(self, organization_id: str, new_name: str) -> Dict[str, Any]:
        """
        Update organization name.

        PUT /api/organizations/{organization_id}/name
        Body: OrganizationUpdate { organization_name: str }
        """
        body = {"organization_name": new_name}
        return self._put(f"/api/organizations/{organization_id}/name", json=body)

    def deactivate_organization(self, organization_id: str) -> None:
        """
        Deactivate (soft-delete) an organization.

        DELETE /api/organizations/{organization_id}
        """
        self._delete(f"/api/organizations/{organization_id}")

    # ---- agents ----

    def list_agents(self, organization_id: str) -> List[Dict[str, Any]]:
        """
        List agents in an organization.

        GET /api/organizations/{organization_id}/agents
        """
        return self._get(f"/api/organizations/{organization_id}/agents")

    def create_agent(
        self,
        organization_id: str,
        agent_name: str,
        is_admin: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a new agent in the organization.

        POST /api/organizations/{organization_id}/agents
        Body: AgentCreate { agent_name, is_admin }
        """
        body = {"agent_name": agent_name, "is_admin": is_admin}
        return self._post(f"/api/organizations/{organization_id}/agents", json=body)

    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get an agent by ID.

        GET /api/agents/{agent_id}
        """
        return self._get(f"/api/agents/{agent_id}")

    def update_agent_name(self, agent_id: str, new_name: str) -> Dict[str, Any]:
        """
        Update an agent's name.

        PUT /api/agents/{agent_id}/name
        Body: AgentUpdate { agent_name: str }
        """
        body = {"agent_name": new_name}
        return self._put(f"/api/agents/{agent_id}/name", json=body)

    def update_agent_admin_status(self, agent_id: str, is_admin: bool) -> Dict[str, Any]:
        """
        Update an agent's admin flag.

        PUT /api/agents/{agent_id}/admin
        Body: AgentUpdate { is_admin: bool }
        """
        body = {"is_admin": is_admin}
        return self._put(f"/api/agents/{agent_id}/admin", json=body)

    def deactivate_agent(self, agent_id: str) -> None:
        """
        Deactivate (soft-delete) an agent.

        DELETE /api/agents/{agent_id}
        """
        self._delete(f"/api/agents/{agent_id}")

