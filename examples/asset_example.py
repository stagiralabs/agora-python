import os
from pprint import pprint

from agora import AgoraClient, AgoraError
from agora._paths import resolve_base_url


def main() -> None:
    base_url = resolve_base_url()
    target_ids = [tid for tid in os.environ.get("AGORA_TARGET_IDS", "").split(",") if tid]

    client = AgoraClient(base_url)
    client.market.return_asset_objects = True

    try:
        print("Market health:")
        pprint(client.market.health())

        if not target_ids:
            statuses = client.market.get_all_target_statuses()
            target_ids = list(statuses.keys())[:3]
            print(f"Using inferred targets: {target_ids}")

        if target_ids:
            assets_for_targets = client.market.get_assets_given_targets(target_ids)
            print("\nAssets for targets (parsed Asset objects when available):")
            pprint(assets_for_targets)
        else:
            print("Set AGORA_TARGET_IDS (comma-separated) to fetch assets for specific targets.")
    except AgoraError as exc:
        print(f"Market call failed: {exc}")


if __name__ == "__main__":
    main()
