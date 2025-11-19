from agora import AgoraClient, AgoraError

try:
    # Ensure AGORA_API_KEY is set
    client = AgoraClient("http://localhost:8000")
except Exception as e:
    print(f"Caught unexcepted exception {e}")

print(client.library.health())