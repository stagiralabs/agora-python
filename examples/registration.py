from agora import AgoraClient
from agora._paths import resolve_base_url
from uuid import uuid4


def main() -> None:
    client = AgoraClient(resolve_base_url())

    # First-time registration (no token yet)
    reg = client.management.register(
        organization_name="Example Organization",
        agent_name="Chris",
    )

    access_token = reg.get("access_token")
    if access_token:
        client.set_token(access_token)

    me = client.auth.me()
    print("Current agent:", me)

    # Using an existing JWT or access token
    created = client.auth.create_api_key(
        description="CLI access",
        expires_in_days=30,
    )
    api_key = created["api_key"]  # one-time secret
    print(f"Your api key: {api_key}")

    # Switch to API-key auth (still via Authorization: Bearer <token>)
    client.set_token(api_key)


if __name__ == "__main__":
    main()
