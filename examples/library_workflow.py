import os
from pprint import pprint

from agora import AgoraClient, AgoraError


BASE_URL = os.environ.get("AGORA_BASE_URL", "http://localhost:8000")
SEARCH_QUERY = os.environ.get("AGORA_SEARCH_QUERY", "vector database")
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
        target = client.library.get_target_file(
            TARGET_ID,
            repo_url=REPO_URL,
            repo_rev=REPO_REV,
        )
        print(f"Target {TARGET_ID}:")
        pprint(target)
    else:
        print("Set AGORA_TARGET_ID to fetch a specific target's backing file.")


if __name__ == "__main__":
    main()
