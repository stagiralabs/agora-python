API_BASE = "/api"
MARKET_BASE = f"{API_BASE}/market"
LIBRARY_BASE = f"{API_BASE}/library"


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
    return api_path(*parts)


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
