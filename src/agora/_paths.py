import os


DEFAULT_LOCAL_BASE_URL = "http://localhost:8000"
AGORA_PROD_BASE_URL = ""

API_BASE = "/api"
MANAGEMENT_BASE = API_BASE
MARKET_BASE = f"{API_BASE}/market"
LIBRARY_BASE = f"{API_BASE}/library"


def resolve_base_url() -> str:
    base_url = os.environ.get("AGORA_BASE_URL")
    if base_url:
        return base_url

    env = os.environ.get("AGORA_ENV", "").lower()
    if env in {"dev", "development", "local"}:
        return os.environ.get("AGORA_DEV_BASE_URL", DEFAULT_LOCAL_BASE_URL)

    return os.environ.get("AGORA_PROD_BASE_URL", DEFAULT_LOCAL_BASE_URL)


DEFAULT_BASE_URL = resolve_base_url()


def _path(base: str, *parts: str) -> str:
    base = base.rstrip("/")
    if not parts:
        return base
    cleaned = [str(part).strip("/") for part in parts if str(part).strip("/")]
    if not cleaned:
        return base
    return "/".join([base, *cleaned])


def api_path(*parts: str) -> str:
    return _path(API_BASE, *parts)


def management_path(*parts: str) -> str:
    return _path(MANAGEMENT_BASE, *parts)


def organizations_path(*parts: str) -> str:
    return management_path("organizations", *parts)


def agents_path(*parts: str) -> str:
    return management_path("agents", *parts)


def library_path(*parts: str) -> str:
    return _path(LIBRARY_BASE, *parts)


def market_path(*parts: str) -> str:
    return _path(MARKET_BASE, *parts)


def market_organizations_path(organization_id: str, *parts: str) -> str:
    return market_path("organizations", organization_id, *parts)
