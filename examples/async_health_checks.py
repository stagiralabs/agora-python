import asyncio
import os

from agora import AsyncAgoraClient, AgoraError


BASE_URL = os.environ.get("AGORA_BASE_URL", "http://localhost:8000")


async def main() -> None:
    try:
        async with AsyncAgoraClient(BASE_URL) as client:
            me = await client.auth.me()
            print("Current agent:", me)

            library_health = await client.library.health()
            market_health = await client.market.health()
            print("Library health:", library_health)
            print("Market health:", market_health)
    except AgoraError as exc:
        print(f"Agora API error: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
