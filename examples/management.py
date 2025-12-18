from agora import AgoraClient, AgoraError
from uuid import uuid4

def main() -> None:
    client = AgoraClient("http://localhost:8000")

    # First-time registration (no token yet)
    reg = client.management.register(
        organization_name=str(uuid4()),
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