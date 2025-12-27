from agora import AgoraClient, AgoraError
from agora._paths import resolve_base_url


def main() -> None:
    # Ensure AGORA_API_KEY is set
    try:
        client = AgoraClient(resolve_base_url())
    except Exception as e:
        print(f"Caught unexcepted exception {e}")

    print(client.library.health())


if __name__ == "__main__":
    main()
