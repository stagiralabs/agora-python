from agora import _paths


def test_path_helper_strips_slashes() -> None:
    assert _paths._path("/api/", "foo/", "/bar", "", "/") == "/api/foo/bar"


def test_path_helper_no_parts_returns_base() -> None:
    assert (
        _paths._path(
            "/api/",
        )
        == "/api"
    )


def test_resolve_base_url_prefers_explicit_env(monkeypatch) -> None:
    monkeypatch.setenv("AGORA_BASE_URL", "https://example.test")
    assert _paths.resolve_base_url() == "https://example.test"


def test_resolve_base_url_dev_env(monkeypatch) -> None:
    monkeypatch.delenv("AGORA_BASE_URL", raising=False)
    monkeypatch.setenv("AGORA_ENV", "dev")
    monkeypatch.setenv("AGORA_DEV_BASE_URL", "http://dev.local")
    assert _paths.resolve_base_url() == "http://dev.local"


def test_resolve_base_url_default(monkeypatch) -> None:
    monkeypatch.delenv("AGORA_BASE_URL", raising=False)
    monkeypatch.delenv("AGORA_ENV", raising=False)
    monkeypatch.delenv("AGORA_PROD_BASE_URL", raising=False)
    assert _paths.resolve_base_url() == _paths.DEFAULT_LOCAL_BASE_URL
