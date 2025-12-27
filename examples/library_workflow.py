import os
from pprint import pprint

from agora import AgoraClient, AgoraError
from agora._paths import resolve_base_url


BASE_URL = resolve_base_url()
SEARCH_QUERY = os.environ.get("AGORA_SEARCH_QUERY", "Pythagorean Theorem")
REPO_URL = os.environ.get("AGORA_REPO_URL")
REPO_REV = os.environ.get("AGORA_REPO_REV")
TARGET_ID = os.environ.get("AGORA_TARGET_ID")


def main() -> None:
    client = AgoraClient(BASE_URL)
    try:
        files = client.library.list_files(repo_url=REPO_URL, repo_rev=REPO_REV)
        print(f"Found {len(files)} files in the library")
    except AgoraError as exc:
        print(f"Failed to list files: {exc}")
        return

    results = client.library.search(
        SEARCH_QUERY,
        k=5,
        repo_url=REPO_URL,
        repo_rev=REPO_REV,
    )
    print(f"Top results for '{SEARCH_QUERY}':")
    pprint(results)

    if TARGET_ID:
        target = client.library.get_target_file(TARGET_ID)
        print(f"Target {TARGET_ID}:")
        pprint(target)
    else:
        print("Set AGORA_TARGET_ID to fetch a specific target's backing file.")


if __name__ == "__main__":
    main()
