import os

from agora import AgoraClient, AgoraError
from agora._paths import resolve_base_url


BASE_URL = resolve_base_url()
DESCRIPTION = os.environ.get("AGORA_API_KEY_DESCRIPTION", "Created via sync example")
EXPIRES_IN_DAYS = os.environ.get("AGORA_API_KEY_EXPIRES_IN_DAYS")


def main() -> None:
    # Creating an API key requires an *already-authenticated* token (JWT/access token or an existing API key).
    # If you don't have one yet, start with `examples/management.py` (register -> access_token -> create_api_key).
    if not os.environ.get("AGORA_API_KEY"):
        print(
            "Missing AGORA_API_KEY. Run examples/management.py to register and mint an API key, or export AGORA_API_KEY."
        )
        return

    expires = int(EXPIRES_IN_DAYS) if EXPIRES_IN_DAYS else None
    try:
        client = AgoraClient(BASE_URL)
        me = client.auth.me()
        print("Authenticated as:", me)

        created = client.auth.create_api_key(
            description=DESCRIPTION,
            expires_in_days=expires,
        )
        print("API key created:")
        print("  id:", created.get("id"))
        print("  description:", created.get("description"))
        print("  expires_in_days:", created.get("expires_in_days"))
        print("  api_key (one-time secret):", created.get("api_key"))
    except AgoraError as exc:
        print(f"Agora API error: {exc}")


if __name__ == "__main__":
    main()
