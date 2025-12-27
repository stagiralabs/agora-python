import os
from pprint import pprint
from typing import Any, Dict, Iterable, List

from agora import AgoraClient, AgoraError
from agora._paths import resolve_base_url


BASE_URL = resolve_base_url()
ORGANIZATION_ID = os.environ.get("AGORA_ORG_ID")
TARGET_IDS = [tid for tid in os.environ.get("AGORA_TARGET_IDS", "").split(",") if tid]
OFFER_IDS = [oid for oid in os.environ.get("AGORA_OFFER_IDS", "").split(",") if oid]
ASSET_IDS = [aid for aid in os.environ.get("AGORA_ASSET_IDS", "").split(",") if aid]
WALLET_IDS = [wid for wid in os.environ.get("AGORA_WALLET_IDS", "").split(",") if wid]
WALLET_LABEL = os.environ.get("AGORA_WALLET_LABEL")
AGENT_ID = os.environ.get("AGORA_AGENT_ID")


def _extract_ids(items: Iterable[Any], keys: Iterable[str]) -> List[str]:
    ids: List[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        for key in keys:
            value = item.get(key)
            if isinstance(value, str):
                ids.append(value)
            elif isinstance(value, list):
                ids.extend([entry for entry in value if isinstance(entry, str)])
    return ids


def _first_unique(values: Iterable[str], limit: int = 3) -> List[str]:
    seen = set()
    result: List[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
        if len(result) >= limit:
            break
    return result


def main() -> None:
    client = AgoraClient(BASE_URL)
    try:
        org_ids = client.market.list_organization_ids()
        print("Organization ids:", org_ids)

        agents = client.market.list_all_agents()
        print(f"Agents returned: {len(agents)}")

        wallets = client.market.list_all_wallets()
        print(f"Wallets returned: {len(wallets)}")

        offers = client.market.list_offers()
        print(f"Offers returned: {len(offers)}")

        target_statuses = client.market.get_all_target_statuses()
        print("All target statuses keys:", list(target_statuses.keys()))

        wallet_ids = WALLET_IDS or _extract_ids(
            wallets, ("id", "wallet_id", "walletId")
        )
        if wallet_ids:
            wallet_ids = _first_unique(wallet_ids)
            wallets_by_id = client.market.get_wallets_by_id(wallet_ids)
            print(f"Wallets by id ({wallet_ids}): {len(wallets_by_id)}")

        offer_ids = OFFER_IDS or _extract_ids(offers, ("id", "offer_id", "offerId"))
        if offer_ids:
            offer_ids = _first_unique(offer_ids)
            targets_from_offers = client.market.get_targets_given_offers(offer_ids)
            print(
                f"Targets for offers ({offer_ids}): {list(targets_from_offers.keys())}"
            )

        if target_statuses and not TARGET_IDS:
            inferred_targets = _first_unique(list(target_statuses.keys()))
        else:
            inferred_targets = []

        target_ids = TARGET_IDS or inferred_targets
        if target_ids:
            offers_for_targets = client.market.get_offers_given_targets(target_ids)
            assets_for_targets = client.market.get_assets_given_targets(target_ids)
            specific_statuses = client.market.get_specific_target_statuses(target_ids)
            print(
                f"Offers for targets ({target_ids}): {list(offers_for_targets.keys())}"
            )
            print(
                f"Assets for targets ({target_ids}): {list(assets_for_targets.keys())}"
            )
            print(
                f"Specific target statuses for ({target_ids}): {list(specific_statuses.keys())}"
            )

        asset_ids = ASSET_IDS
        if asset_ids:
            asset_ids = _first_unique(asset_ids)
            targets_from_assets = client.market.get_targets_given_assets(asset_ids)
            print(
                f"Targets for assets ({asset_ids}): {list(targets_from_assets.keys())}"
            )
    except AgoraError as exc:
        print(f"Market call failed: {exc}")
        return

    if ORGANIZATION_ID:
        org_wallets = client.market.list_organization_wallets(ORGANIZATION_ID)
        print(f"Wallets for org {ORGANIZATION_ID}: {len(org_wallets)}")

        if AGENT_ID:
            trading_wallets = client.market.get_agent_trading_wallets(
                ORGANIZATION_ID, AGENT_ID
            )
            print(f"Trading wallets for agent {AGENT_ID}: {len(trading_wallets)}")

        if WALLET_LABEL:
            wallet_contents = client.market.get_wallet_contents(
                ORGANIZATION_ID, WALLET_LABEL
            )
            trading_agents = client.market.get_wallet_trading_agents(
                ORGANIZATION_ID, WALLET_LABEL
            )
            print(f"Wallet contents for {WALLET_LABEL}: {list(wallet_contents.keys())}")
            print(f"Trading agents for {WALLET_LABEL}: {len(trading_agents)}")

    if not TARGET_IDS:
        print("Set AGORA_TARGET_IDS (comma-separated) to override inferred target ids.")
    if not OFFER_IDS:
        print("Set AGORA_OFFER_IDS (comma-separated) to override inferred offer ids.")
    if not WALLET_IDS:
        print("Set AGORA_WALLET_IDS (comma-separated) to override inferred wallet ids.")
    if ORGANIZATION_ID and not WALLET_LABEL:
        print(
            "Set AGORA_WALLET_LABEL to fetch wallet contents/trading agents for an org."
        )
    if ORGANIZATION_ID and not AGENT_ID:
        print("Set AGORA_AGENT_ID to fetch agent trading wallets for an org.")


if __name__ == "__main__":
    main()
