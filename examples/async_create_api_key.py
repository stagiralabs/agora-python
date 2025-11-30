import asyncio
import os

from agora import AsyncAgoraClient, AgoraError


BASE_URL = os.environ.get("AGORA_BASE_URL", "http://localhost:8000")
DESCRIPTION = os.environ.get("AGORA_API_KEY_DESCRIPTION", "Created via async example")
EXPIRES_IN_DAYS = os.environ.get("AGORA_API_KEY_EXPIRES_IN_DAYS")


async def main() -> None:
    # Requires AGORA_API_KEY to be set for the initial authenticated client
    expires = int(EXPIRES_IN_DAYS) if EXPIRES_IN_DAYS else None
    try:
        async with AsyncAgoraClient(BASE_URL) as client:
            me = await client.auth.me()
            print("Authenticated as:", me)

            created = await client.auth.create_api_key(
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
    asyncio.run(main())
