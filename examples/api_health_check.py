from agora import AgoraClient, AgoraError

def main() -> None:
    # Ensure AGORA_API_KEY is set
    try:
        client = AgoraClient("http://localhost:8000")
    except Exception as e:
        print(f"Caught unexcepted exception {e}")

    print(client.library.health())

if __name__ == "__main__":
    main()