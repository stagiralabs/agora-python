# Agora SDK (Python)
Clean, typed access to the Agora API with both sync and async clients.

## Features
- Sync and async clients
- Clear error hierarchy with HTTP status mapping
- Minimal dependencies

## Install
```bash
python -m pip install agora-sdk
```

## Quickstart
```python
from agora import AgoraClient

client = AgoraClient(base_url="http://localhost:8000", token="your-api-key")
print(client.market.health())
```

## Async
```python
import asyncio
from agora import AsyncAgoraClient

async def main() -> None:
    async with AsyncAgoraClient(
        base_url="http://localhost:8000",
        token="your-api-key",
    ) as client:
        print(await client.market.health())

asyncio.run(main())
```

## Configuration
You can also use environment variables:
- `AGORA_API_KEY`
- `AGORA_BASE_URL`
- `AGORA_ENV` (`dev`, `development`, `local`)

## Development
Run the same checks as CI:
```bash
bash scripts/ci_local.sh
```

Run CI in a container:
```bash
bash scripts/ci_docker.sh
```

## Examples
See `examples/` for end-to-end usage patterns.
