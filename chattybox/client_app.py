import socket

PORT = 5050
FORMAT = "utf-8"
SERVER = "127.0.0.1"


def send(client: socket.socket, msg: str) -> None:
    client.send(msg.encode(FORMAT))


def receive(client: socket.socket) -> str or None:
    data = client.recv(1024).decode(FORMAT)
    if not data:
        client.close()
        return None
    return data


def start_client() -> socket.socket:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER, PORT))
    return client
