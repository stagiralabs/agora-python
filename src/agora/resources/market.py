from .._client import AgoraClient
from .._resource import SyncAPIResource, AsyncAPIResource

from typing import Any, Dict, List, Optional


class Market(SyncAPIResource):
    """
    Market mechanics proxy – from routers_market.py

    Routes wrapped here:
        GET  /api/market/health
        GET  /api/market/organization_ids
        GET  /api/market/all_agents
        GET  /api/market/organizations/{organization_id}/agents
        GET  /api/market/find_organizations
        GET  /api/market/all_wallets
        GET  /api/market/wallets_by_id
        GET  /api/market/organizations/{organization_id}/wallets
        GET  /api/market/organizations/{organization_id}/agents/{agent_id}/trading_wallets
        GET  /api/market/organizations/{organization_id}/wallets/{wallet_label}/trading_agents
        GET  /api/market/organizations/{organization_id}/wallets/{wallet_label}/wallet_contents
        POST /api/market/organizations/{organization_id}/wallets/{wallet_name}/add_wallet
        DELETE /api/market/organizations/{organization_id}/wallets/{wallet_label}/delete_wallet
        POST /api/market/organizations/{organization_id}/wallets/{wallet_label}/set_value_lower_bound
        POST /api/market/organizations/{organization_id}/wallets/{wallet_label}/set_trading_agents
        POST /api/market/organizations/{organization_id}/wallets/{wallet_label}/add_to_balance
        POST /api/market/organizations/{organization_id}/wallets/{wallet_label}/withdraw_from_balance
        POST /api/market/organizations/{organization_id}/merge_wallets
        GET  /api/market/organizations/{organization_id}/wallets/{wallet_label}/evaluate_wallet_contents_minimum_value
        POST /api/market/organizations/{organization_id}/general_wallets_update
        POST /api/market/organizations/{organization_id}/transfer_balance_between_wallets
        POST /api/market/organizations/{organization_id}/transfer_assets_between_wallets
        POST /api/market/organizations/{organization_id}/wallets/{wallet_label}/create_offers
        POST /api/market/organizations/{organization_id}/wallets/{wallet_label}/merge_assets
        POST /api/market/organizations/{organization_id}/wallets/{wallet_label}/attempt_to_sell_assets
        POST /api/market/organizations/{organization_id}/wallets/{wallet_label}/force_liquidate_all_assets_and_offers
        POST /api/market/organizations/{organization_id}/wallets/{wallet_label}/force_liquidate_some_assets_and_offers
        POST /api/market/organizations/{organization_id}/wallets/{wallet_label}/take_from_offer
        POST /api/market/organizations/{organization_id}/wallets/{wallet_label}/offers/{offer_id}/new_offer_quantity
        GET  /api/market/offers
        GET  /api/market/offers_given_targets
        GET  /api/market/assets_given_targets
        GET  /api/market/targets_given_offers
        GET  /api/market/targets_given_assets
        GET  /api/market/all_target_statuses
        GET  /api/market/specific_target_statuses
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
        Escape hatch for calling market endpoints that aren't wrapped yet.

        `path` is relative to `/api/market` (e.g. `"/health"` or `"health"`).
        You can also pass a fully-qualified API path like `"/api/market/health"`.
        """
        if path.startswith("/api/"):
            return self._request(method, path, params=params, json=json)
        normalized = path if path.startswith("/") else f"/{path}"
        return self._request(method, f"/api/market{normalized}", params=params, json=json)

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

    def find_organizations(self, agent_ids: List[str]) -> Dict[str, Any]:
        """
        GET /api/market/find_organizations
        """
        params = [("agent_ids", aid) for aid in agent_ids]
        return self._request("GET", "/api/market/find_organizations", params=params)

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

    def get_agent_trading_wallets(
        self,
        organization_id: str,
        agent_id: str,
    ) -> List[Dict[str, Any]]:
        """
        GET /api/market/organizations/{organization_id}/agents/{agent_id}/trading_wallets
        """
        path = (
            f"/api/market/organizations/{organization_id}/agents/{agent_id}/trading_wallets"
        )
        return self._get(path)

    def get_wallet_trading_agents(
        self,
        organization_id: str,
        wallet_label: str,
        by: str = "name",
    ) -> List[Dict[str, Any]]:
        """
        GET /api/market/organizations/{organization_id}/wallets/{wallet_label}/trading_agents
        Query: wallet_id_or_name in {"id", "name"}
        """
        params = {"wallet_id_or_name": by}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/trading_agents"
        )
        return self._get(path, params=params)

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

    def add_wallet(
        self,
        organization_id: str,
        wallet_name: str,
        set_value_lower_bound_to_zero: bool = True,
    ) -> Dict[str, Any]:
        """
        POST /api/market/organizations/{organization_id}/wallets/{wallet_name}/add_wallet
        """
        params = {"set_value_lower_bound_to_zero": set_value_lower_bound_to_zero}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_name}/add_wallet"
        )
        return self._post(path, params=params)

    def delete_wallet(
        self,
        organization_id: str,
        wallet_label: str,
        by: str = "name",
    ) -> Dict[str, Any]:
        """
        DELETE /api/market/organizations/{organization_id}/wallets/{wallet_label}/delete_wallet
        Query: wallet_id_or_name in {"id", "name"}
        """
        params = {"wallet_id_or_name": by}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/delete_wallet"
        )
        return self._delete(path, params=params)

    def set_value_lower_bound(
        self,
        organization_id: str,
        wallet_label: str,
        new_value_lower_bound: Optional[Dict[str, int]] = None,
        by: str = "name",
    ) -> Dict[str, Any]:
        """
        POST /api/market/organizations/{organization_id}/wallets/{wallet_label}/set_value_lower_bound
        """
        params = {"wallet_id_or_name": by}
        body = {"new_value_lower_bound": new_value_lower_bound}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/set_value_lower_bound"
        )
        return self._post(path, params=params, json=body)

    def set_trading_agents(
        self,
        organization_id: str,
        wallet_label: str,
        new_trading_agents: List[str],
        by: str = "name",
    ) -> Dict[str, Any]:
        """
        POST /api/market/organizations/{organization_id}/wallets/{wallet_label}/set_trading_agents
        """
        params = {"wallet_id_or_name": by}
        body = {"new_trading_agents": new_trading_agents}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/set_trading_agents"
        )
        return self._post(path, params=params, json=body)

    def add_to_balance(
        self,
        organization_id: str,
        wallet_label: str,
        amount: Dict[str, int],
        by: str = "name",
    ) -> Dict[str, Any]:
        """
        POST /api/market/organizations/{organization_id}/wallets/{wallet_label}/add_to_balance
        """
        params = {"wallet_id_or_name": by}
        body = {"amount": amount}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/add_to_balance"
        )
        return self._post(path, params=params, json=body)

    def withdraw_from_balance(
        self,
        organization_id: str,
        wallet_label: str,
        amount: Dict[str, int],
        by: str = "name",
    ) -> Dict[str, Any]:
        """
        POST /api/market/organizations/{organization_id}/wallets/{wallet_label}/withdraw_from_balance
        """
        params = {"wallet_id_or_name": by}
        body = {"amount": amount}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/withdraw_from_balance"
        )
        return self._post(path, params=params, json=body)

    def merge_wallets(
        self,
        organization_id: str,
        source_wallet_labels: List[str],
        target_wallet_label: str,
        by: str = "name",
    ) -> Dict[str, Any]:
        """
        POST /api/market/organizations/{organization_id}/merge_wallets
        """
        params = {"wallet_id_or_name": by}
        body = {
            "source_wallet_labels": source_wallet_labels,
            "target_wallet_label": target_wallet_label,
        }
        path = f"/api/market/organizations/{organization_id}/merge_wallets"
        return self._post(path, params=params, json=body)

    def evaluate_wallet_contents_minimum_value(
        self,
        organization_id: str,
        wallet_label: str,
        by: str = "name",
    ) -> Dict[str, Any]:
        """
        GET /api/market/organizations/{organization_id}/wallets/{wallet_label}/evaluate_wallet_contents_minimum_value
        """
        params = {"wallet_id_or_name": by}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/evaluate_wallet_contents_minimum_value"
        )
        return self._get(path, params=params)

    def general_wallets_update(
        self,
        organization_id: str,
        request_body: Dict[str, Any],
        by: str = "name",
    ) -> Dict[str, Any]:
        """
        POST /api/market/organizations/{organization_id}/general_wallets_update
        """
        params = {"wallet_id_or_name": by}
        path = f"/api/market/organizations/{organization_id}/general_wallets_update"
        return self._post(path, params=params, json=request_body)

    def transfer_balance_between_wallets(
        self,
        organization_id: str,
        wallet_label_to_new_balance: Dict[str, Dict[str, int]],
        by: str = "name",
    ) -> Dict[str, Any]:
        """
        POST /api/market/organizations/{organization_id}/transfer_balance_between_wallets
        """
        params = {"wallet_id_or_name": by}
        body = {"wallet_label_to_new_balance": wallet_label_to_new_balance}
        path = f"/api/market/organizations/{organization_id}/transfer_balance_between_wallets"
        return self._post(path, params=params, json=body)

    def transfer_assets_between_wallets(
        self,
        organization_id: str,
        private_asset_to_new_wallet: Dict[str, str],
        by: str = "name",
    ) -> Dict[str, Any]:
        """
        POST /api/market/organizations/{organization_id}/transfer_assets_between_wallets
        """
        params = {"wallet_id_or_name": by}
        body = {"private_asset_to_new_wallet": private_asset_to_new_wallet}
        path = f"/api/market/organizations/{organization_id}/transfer_assets_between_wallets"
        return self._post(path, params=params, json=body)

    def create_offers(
        self,
        organization_id: str,
        wallet_label: str,
        desired_offers: List[Dict[str, Any]],
        by: str = "name",
    ) -> Dict[str, Any]:
        """
        POST /api/market/organizations/{organization_id}/wallets/{wallet_label}/create_offers
        """
        params = {"wallet_id_or_name": by}
        body = {"desired_offers": desired_offers}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/create_offers"
        )
        return self._post(path, params=params, json=body)

    def merge_assets(
        self,
        organization_id: str,
        wallet_label: str,
        assets_to_merge: List[str],
        by: str = "name",
    ) -> Dict[str, Any]:
        """
        POST /api/market/organizations/{organization_id}/wallets/{wallet_label}/merge_assets
        """
        params = {"wallet_id_or_name": by}
        body = {"assets_to_merge": assets_to_merge}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/merge_assets"
        )
        return self._post(path, params=params, json=body)

    def attempt_to_sell_assets(
        self,
        organization_id: str,
        wallet_label: str,
        asset_to_number_of_units_and_price_per_unit: Dict[str, List[int]],
        by: str = "name",
    ) -> Dict[str, Any]:
        """
        POST /api/market/organizations/{organization_id}/wallets/{wallet_label}/attempt_to_sell_assets
        """
        params = {"wallet_id_or_name": by}
        body = {
            "asset_to_number_of_units_and_price_per_unit": (
                asset_to_number_of_units_and_price_per_unit
            )
        }
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/attempt_to_sell_assets"
        )
        return self._post(path, params=params, json=body)

    def force_liquidate_all(
        self,
        organization_id: str,
        wallet_label: str,
        by: str = "name",
    ) -> Dict[str, Any]:
        """
        POST /api/market/organizations/{organization_id}/wallets/{wallet_label}/force_liquidate_all_assets_and_offers
        """
        params = {"wallet_id_or_name": by}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/force_liquidate_all_assets_and_offers"
        )
        return self._post(path, params=params)

    def force_liquidate_some(
        self,
        organization_id: str,
        wallet_label: str,
        assets_to_liquidate: List[str],
        offers_to_liquidate: List[str],
        by: str = "name",
    ) -> Dict[str, Any]:
        """
        POST /api/market/organizations/{organization_id}/wallets/{wallet_label}/force_liquidate_some_assets_and_offers
        """
        params = {"wallet_id_or_name": by}
        body = {
            "assets_to_liquidate": assets_to_liquidate,
            "offers_to_liquidate": offers_to_liquidate,
        }
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/force_liquidate_some_assets_and_offers"
        )
        return self._post(path, params=params, json=body)

    def take_from_offer(
        self,
        organization_id: str,
        wallet_label: str,
        offer_id: str,
        quantity: int,
        by: str = "name",
    ) -> Dict[str, Any]:
        """
        POST /api/market/organizations/{organization_id}/wallets/{wallet_label}/take_from_offer
        """
        params = {"wallet_id_or_name": by}
        body = {"offer_id": offer_id, "quantity": quantity}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/take_from_offer"
        )
        return self._post(path, params=params, json=body)

    def new_offer_quantity(
        self,
        organization_id: str,
        wallet_label: str,
        offer_id: str,
        new_quantity: int,
        by: str = "name",
    ) -> Dict[str, Any]:
        """
        POST /api/market/organizations/{organization_id}/wallets/{wallet_label}/offers/{offer_id}/new_offer_quantity
        """
        params = {"wallet_id_or_name": by}
        body = {"new_quantity": new_quantity}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/offers/{offer_id}/new_offer_quantity"
        )
        return self._post(path, params=params, json=body)

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
    

class AsyncMarket(AsyncAPIResource):
    """
    Async market mechanics proxy – from routers_market.py.
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
        Escape hatch for calling market endpoints that aren't wrapped yet.

        `path` is relative to `/api/market` (e.g. `"/health"` or `"health"`).
        You can also pass a fully-qualified API path like `"/api/market/health"`.
        """
        if path.startswith("/api/"):
            return await self._request(method, path, params=params, json=json)
        normalized = path if path.startswith("/") else f"/{path}"
        return await self._request(
            method, f"/api/market{normalized}", params=params, json=json
        )

    async def health(self) -> Dict[str, Any]:
        return await self._get("/api/market/health")

    async def list_organization_ids(self) -> List[str]:
        return await self._get("/api/market/organization_ids")

    async def list_all_agents(self) -> List[Dict[str, Any]]:
        return await self._get("/api/market/all_agents")

    async def list_organization_agents(self, organization_id: str) -> List[Dict[str, Any]]:
        return await self._get(f"/api/market/organizations/{organization_id}/agents")

    async def find_organizations(self, agent_ids: List[str]) -> Dict[str, Any]:
        params = [("agent_ids", aid) for aid in agent_ids]
        return await self._request("GET", "/api/market/find_organizations", params=params)

    async def list_all_wallets(self) -> List[Dict[str, Any]]:
        return await self._get("/api/market/all_wallets")

    async def get_wallets_by_id(self, wallet_ids: List[str]) -> List[Dict[str, Any]]:
        params = [("wallet_ids", wid) for wid in wallet_ids]
        return await self._request("GET", "/api/market/wallets_by_id", params=params)

    async def list_organization_wallets(self, organization_id: str) -> List[Dict[str, Any]]:
        return await self._get(f"/api/market/organizations/{organization_id}/wallets")

    async def get_agent_trading_wallets(
        self,
        organization_id: str,
        agent_id: str,
    ) -> List[Dict[str, Any]]:
        path = (
            f"/api/market/organizations/{organization_id}/agents/{agent_id}/trading_wallets"
        )
        return await self._get(path)

    async def get_wallet_trading_agents(
        self,
        organization_id: str,
        wallet_label: str,
        by: str = "name",
    ) -> List[Dict[str, Any]]:
        params = {"wallet_id_or_name": by}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/trading_agents"
        )
        return await self._get(path, params=params)

    async def get_wallet_contents(
        self,
        organization_id: str,
        wallet_label: str,
        by: str = "name",
    ) -> Dict[str, Any]:
        params = {"wallet_id_or_name": by}
        path = f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/wallet_contents"
        return await self._get(path, params=params)

    async def add_wallet(
        self,
        organization_id: str,
        wallet_name: str,
        set_value_lower_bound_to_zero: bool = True,
    ) -> Dict[str, Any]:
        params = {"set_value_lower_bound_to_zero": set_value_lower_bound_to_zero}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_name}/add_wallet"
        )
        return await self._post(path, params=params)

    async def delete_wallet(
        self,
        organization_id: str,
        wallet_label: str,
        by: str = "name",
    ) -> Dict[str, Any]:
        params = {"wallet_id_or_name": by}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/delete_wallet"
        )
        return await self._delete(path, params=params)

    async def set_value_lower_bound(
        self,
        organization_id: str,
        wallet_label: str,
        new_value_lower_bound: Optional[Dict[str, int]] = None,
        by: str = "name",
    ) -> Dict[str, Any]:
        params = {"wallet_id_or_name": by}
        body = {"new_value_lower_bound": new_value_lower_bound}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/set_value_lower_bound"
        )
        return await self._post(path, params=params, json=body)

    async def set_trading_agents(
        self,
        organization_id: str,
        wallet_label: str,
        new_trading_agents: List[str],
        by: str = "name",
    ) -> Dict[str, Any]:
        params = {"wallet_id_or_name": by}
        body = {"new_trading_agents": new_trading_agents}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/set_trading_agents"
        )
        return await self._post(path, params=params, json=body)

    async def add_to_balance(
        self,
        organization_id: str,
        wallet_label: str,
        amount: Dict[str, int],
        by: str = "name",
    ) -> Dict[str, Any]:
        params = {"wallet_id_or_name": by}
        body = {"amount": amount}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/add_to_balance"
        )
        return await self._post(path, params=params, json=body)

    async def withdraw_from_balance(
        self,
        organization_id: str,
        wallet_label: str,
        amount: Dict[str, int],
        by: str = "name",
    ) -> Dict[str, Any]:
        params = {"wallet_id_or_name": by}
        body = {"amount": amount}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/withdraw_from_balance"
        )
        return await self._post(path, params=params, json=body)

    async def merge_wallets(
        self,
        organization_id: str,
        source_wallet_labels: List[str],
        target_wallet_label: str,
        by: str = "name",
    ) -> Dict[str, Any]:
        params = {"wallet_id_or_name": by}
        body = {
            "source_wallet_labels": source_wallet_labels,
            "target_wallet_label": target_wallet_label,
        }
        path = f"/api/market/organizations/{organization_id}/merge_wallets"
        return await self._post(path, params=params, json=body)

    async def evaluate_wallet_contents_minimum_value(
        self,
        organization_id: str,
        wallet_label: str,
        by: str = "name",
    ) -> Dict[str, Any]:
        params = {"wallet_id_or_name": by}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/evaluate_wallet_contents_minimum_value"
        )
        return await self._get(path, params=params)

    async def general_wallets_update(
        self,
        organization_id: str,
        request_body: Dict[str, Any],
        by: str = "name",
    ) -> Dict[str, Any]:
        params = {"wallet_id_or_name": by}
        path = f"/api/market/organizations/{organization_id}/general_wallets_update"
        return await self._post(path, params=params, json=request_body)

    async def transfer_balance_between_wallets(
        self,
        organization_id: str,
        wallet_label_to_new_balance: Dict[str, Dict[str, int]],
        by: str = "name",
    ) -> Dict[str, Any]:
        params = {"wallet_id_or_name": by}
        body = {"wallet_label_to_new_balance": wallet_label_to_new_balance}
        path = f"/api/market/organizations/{organization_id}/transfer_balance_between_wallets"
        return await self._post(path, params=params, json=body)

    async def transfer_assets_between_wallets(
        self,
        organization_id: str,
        private_asset_to_new_wallet: Dict[str, str],
        by: str = "name",
    ) -> Dict[str, Any]:
        params = {"wallet_id_or_name": by}
        body = {"private_asset_to_new_wallet": private_asset_to_new_wallet}
        path = f"/api/market/organizations/{organization_id}/transfer_assets_between_wallets"
        return await self._post(path, params=params, json=body)

    async def create_offers(
        self,
        organization_id: str,
        wallet_label: str,
        desired_offers: List[Dict[str, Any]],
        by: str = "name",
    ) -> Dict[str, Any]:
        params = {"wallet_id_or_name": by}
        body = {"desired_offers": desired_offers}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/create_offers"
        )
        return await self._post(path, params=params, json=body)

    async def merge_assets(
        self,
        organization_id: str,
        wallet_label: str,
        assets_to_merge: List[str],
        by: str = "name",
    ) -> Dict[str, Any]:
        params = {"wallet_id_or_name": by}
        body = {"assets_to_merge": assets_to_merge}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/merge_assets"
        )
        return await self._post(path, params=params, json=body)

    async def attempt_to_sell_assets(
        self,
        organization_id: str,
        wallet_label: str,
        asset_to_number_of_units_and_price_per_unit: Dict[str, List[int]],
        by: str = "name",
    ) -> Dict[str, Any]:
        params = {"wallet_id_or_name": by}
        body = {
            "asset_to_number_of_units_and_price_per_unit": (
                asset_to_number_of_units_and_price_per_unit
            )
        }
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/attempt_to_sell_assets"
        )
        return await self._post(path, params=params, json=body)

    async def force_liquidate_all(
        self,
        organization_id: str,
        wallet_label: str,
        by: str = "name",
    ) -> Dict[str, Any]:
        params = {"wallet_id_or_name": by}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/force_liquidate_all_assets_and_offers"
        )
        return await self._post(path, params=params)

    async def force_liquidate_some(
        self,
        organization_id: str,
        wallet_label: str,
        assets_to_liquidate: List[str],
        offers_to_liquidate: List[str],
        by: str = "name",
    ) -> Dict[str, Any]:
        params = {"wallet_id_or_name": by}
        body = {
            "assets_to_liquidate": assets_to_liquidate,
            "offers_to_liquidate": offers_to_liquidate,
        }
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/force_liquidate_some_assets_and_offers"
        )
        return await self._post(path, params=params, json=body)

    async def take_from_offer(
        self,
        organization_id: str,
        wallet_label: str,
        offer_id: str,
        quantity: int,
        by: str = "name",
    ) -> Dict[str, Any]:
        params = {"wallet_id_or_name": by}
        body = {"offer_id": offer_id, "quantity": quantity}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/take_from_offer"
        )
        return await self._post(path, params=params, json=body)

    async def new_offer_quantity(
        self,
        organization_id: str,
        wallet_label: str,
        offer_id: str,
        new_quantity: int,
        by: str = "name",
    ) -> Dict[str, Any]:
        params = {"wallet_id_or_name": by}
        body = {"new_quantity": new_quantity}
        path = (
            f"/api/market/organizations/{organization_id}/wallets/{wallet_label}/offers/{offer_id}/new_offer_quantity"
        )
        return await self._post(path, params=params, json=body)

    async def list_offers(self) -> List[Dict[str, Any]]:
        return await self._get("/api/market/offers")

    async def get_offers_given_targets(self, target_ids: List[str]) -> Dict[str, Any]:
        params = [("target_ids", tid) for tid in target_ids]
        return await self._request("GET", "/api/market/offers_given_targets", params=params)

    async def get_assets_given_targets(self, target_ids: List[str]) -> Dict[str, Any]:
        params = [("target_ids", tid) for tid in target_ids]
        return await self._request("GET", "/api/market/assets_given_targets", params=params)

    async def get_targets_given_offers(self, offer_ids: List[str]) -> Dict[str, Any]:
        params = [("offer_ids", oid) for oid in offer_ids]
        return await self._request("GET", "/api/market/targets_given_offers", params=params)

    async def get_targets_given_assets(self, asset_ids: List[str]) -> Dict[str, Any]:
        params = [("asset_ids", aid) for aid in asset_ids]
        return await self._request("GET", "/api/market/targets_given_assets", params=params)

    async def get_all_target_statuses(self) -> Dict[str, Any]:
        return await self._get("/api/market/all_target_statuses")

    async def get_specific_target_statuses(self, target_ids: List[str]) -> Dict[str, Any]:
        params = [("target_ids", tid) for tid in target_ids]
        return await self._request("GET", "/api/market/specific_target_statuses", params=params)
