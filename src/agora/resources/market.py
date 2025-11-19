from .._client import AgoraClient
from .._resource import SyncAPIResource

from typing import Any, Dict, List, Optional

class Market(SyncAPIResource):
    """
    Market mechanics proxy – from routers_market.py

    Routes wrapped here:
        GET  /api/market/health
        GET  /api/market/organization_ids
        GET  /api/market/all_agents
        GET  /api/market/organizations/{organization_id}/agents
        GET  /api/market/all_wallets
        GET  /api/market/wallets_by_id
        GET  /api/market/organizations/{organization_id}/wallets
        GET  /api/market/organizations/{organization_id}/wallets/{wallet_label}/wallet_contents
        GET  /api/market/offers
        GET  /api/market/offers_given_targets
        GET  /api/market/assets_given_targets
        GET  /api/market/targets_given_offers
        GET  /api/market/targets_given_assets
        GET  /api/market/all_target_statuses
        GET  /api/market/specific_target_statuses
    """

    def health(self) -> Dict[str, Any]:
        """GET /api/market/health"""
        return self._get("/api/market/health")

    # ---- organizations / agents ----

    def list_organization_ids(self) -> List[str]:
        """
        GET /api/market/organization_ids
        Returns a list of organization IDs known to market_mechanics.
        """
        return self._get("/api/market/organization_ids")

    def list_all_agents(self) -> List[Dict[str, Any]]:
        """GET /api/market/all_agents"""
        return self._get("/api/market/all_agents")

    def list_organization_agents(self, organization_id: str) -> List[Dict[str, Any]]:
        """
        GET /api/market/organizations/{organization_id}/agents
        """
        return self._get(f"/api/market/organizations/{organization_id}/agents")

    # ---- wallets ----

    def list_all_wallets(self) -> List[Dict[str, Any]]:
        """GET /api/market/all_wallets"""
        return self._get("/api/market/all_wallets")

    def get_wallets_by_id(self, wallet_ids: List[str]) -> List[Dict[str, Any]]:
        """
        GET /api/market/wallets_by_id
        Query: wallet_ids (repeated or comma-separated, depending on implementation)
        Here we send them as repeated query params: ?wallet_ids=id1&wallet_ids=id2...
        """
        # requests handles repeated values via a list.
        params = [("wallet_ids", wid) for wid in wallet_ids]
        # Using _request directly since params is a list of tuples
        return self._request("GET", "/api/market/wallets_by_id", params=params)

    def list_organization_wallets(self, organization_id: str) -> List[Dict[str, Any]]:
        """
        GET /api/market/organizations/{organization_id}/wallets
        """
        return self._get(f"/api/market/organizations/{organization_id}/wallets")

    def get_wallet_contents(
        self,
        organization_id: str,
        wallet_label: str,
        by: str = "name",
    ) -> Dict[str, Any]:
        """
        Get wallet contents.

        GET /api/market/organizations/{organization_id}/wallets/{wallet_label}/wallet_contents
        Query: wallet_id_or_name in {"id", "name"}
        """
        params = {"wallet_id_or_name": by}
        path = f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/wallet_contents"
        return self._get(path, params=params)

    # ---- offers / targets / assets ----

    def list_offers(self) -> List[Dict[str, Any]]:
        """GET /api/market/offers"""
        return self._get("/api/market/offers")

    def get_offers_given_targets(self, target_ids: List[str]) -> Dict[str, Any]:
        """GET /api/market/offers_given_targets"""
        params = [("target_ids", tid) for tid in target_ids]
        return self._request("GET", "/api/market/offers_given_targets", params=params)

    def get_assets_given_targets(self, target_ids: List[str]) -> Dict[str, Any]:
        """GET /api/market/assets_given_targets"""
        params = [("target_ids", tid) for tid in target_ids]
        return self._request("GET", "/api/market/assets_given_targets", params=params)

    def get_targets_given_offers(self, offer_ids: List[str]) -> Dict[str, Any]:
        """GET /api/market/targets_given_offers"""
        params = [("offer_ids", oid) for oid in offer_ids]
        return self._request("GET", "/api/market/targets_given_offers", params=params)

    def get_targets_given_assets(self, asset_ids: List[str]) -> Dict[str, Any]:
        """GET /api/market/targets_given_assets"""
        params = [("asset_ids", aid) for aid in asset_ids]
        return self._request("GET", "/api/market/targets_given_assets", params=params)

    def get_all_target_statuses(self) -> Dict[str, Any]:
        """GET /api/market/all_target_statuses"""
        return self._get("/api/market/all_target_statuses")

    def get_specific_target_statuses(self, target_ids: List[str]) -> Dict[str, Any]:
        """GET /api/market/specific_target_statuses"""
        params = [("target_ids", tid) for tid in target_ids]
        return self._request("GET", "/api/market/specific_target_statuses", params=params)

    # ---- escape hatch ----

    def raw__get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Escape hatch for unwrapped / experimental endpoints under /api/market.

        path should be relative to /api/market, e.g. "/organizations/{org_id}/wallets".
        """
        if not path.startswith("/"):
            path = "/" + path
        return self._get("/api/market" + path, params=params)

    def raw__post(self, path: str, json: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Escape hatch POST for unwrapped /api/market endpoints.
        """
        if not path.startswith("/"):
            path = "/" + path
        return self._post("/api/market" + path, json=json, params=params)
    

