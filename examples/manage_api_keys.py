"""
manage_api_keys

This example covers the auth client. In general, an admin user
can extend multiple live API keys at a time. An API key
comes with the following metadata and packaged into
```list_api_keys()``` as a list of JSONs.

    api_key_id
    key_prefix
    description
    is_active
    created_at
    last_used_at
    expires_at
"""

import os
from agora import AgoraClient, AgoraError
from agora._paths import resolve_base_url

BASE_URL = resolve_base_url()


def main() -> None:
    if not os.environ.get("AGORA_API_KEY"):
        print(
            "Missing AGORA_API_KEY. Run examples/management.py to register and mint an API key, or export AGORA_API_KEY."
        )
        return

    try:
        client = AgoraClient(BASE_URL)
        auth_client = client.auth
        me = auth_client.me()
        print(f"Me: {me}")

        api_keys = auth_client.list_api_keys()
        print(f"My API keys: {api_keys}")

        new_key = auth_client.create_api_key(
            description="Manage API keys example", expires_in_days=30
        )
        print(f"My new key: {new_key}")

        new_key_id = new_key["api_key_id"]
        auth_client.delete_api_key(new_key_id)

    except AgoraError as exc:
        print(f"Agora API error: {exc}")


if __name__ == "__main__":
    main()
