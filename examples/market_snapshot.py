import os
from pprint import pprint

from agora import AgoraClient, AgoraError


BASE_URL = os.environ.get("AGORA_BASE_URL", "http://localhost:8000")
ORGANIZATION_ID = os.environ.get("AGORA_ORG_ID")
TARGET_IDS = [tid for tid in os.environ.get("AGORA_TARGET_IDS", "").split(",") if tid]


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
    except AgoraError as exc:
        print(f"Market call failed: {exc}")
        return

    if ORGANIZATION_ID:
        org_wallets = client.market.list_organization_wallets(ORGANIZATION_ID)
        print(f"Wallets for org {ORGANIZATION_ID}: {len(org_wallets)}")

    if TARGET_IDS:
        specific_statuses = client.market.get_specific_target_statuses(TARGET_IDS)
        print("Specific target statuses:")
        pprint(specific_statuses)
    else:
        print("Set AGORA_TARGET_IDS (comma-separated) to fetch specific target statuses.")


if __name__ == "__main__":
    main()
