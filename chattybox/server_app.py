import queue
import socket
import threading


PORT = 5050
SERVER = "127.0.0.1"
FORMAT = "utf-8"


def server() -> None:
    threads = ()
    messages = queue.Queue()
    connections = queue.Queue()
    list_connection = []
    event = threading.Event()

    def handle_client(conn, addr) -> None:
        nonlocal event
        nonlocal messages
        nonlocal list_connection

        while True:
            data = conn.recv(1024)
            data = data.decode(FORMAT)
            if not data:
                break
            messages.put(data)
        conn.close()
        list_connection.remove((conn, addr))
        print("client connection closed")
        event.set()

    def create_server_socket() -> socket.socket:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((SERVER, PORT))
        server_socket.listen()
        print(f"LISTENING on {SERVER}")
        return server_socket

    def remove_dead_thread_from_tuple(threads: tuple) -> tuple[threading.Thread]:
        return tuple(thread for idx, thread in enumerate(threads) if thread.is_alive())

    def add_thread_to_tuple(threads: tuple, new_thread: threading.Thread) -> tuple:
        return threads + (new_thread,)

    def put_connection_in_queue(server_socket) -> None:
        nonlocal connections

        while True:
            conn, addr = server_socket.accept()
            connections.put((conn, addr))
            list_connection.append((conn, addr))

    def accept_connection_from_queue() -> None:
        nonlocal threads
        nonlocal connections

        while True:
            conn, addr = connections.get()
            if conn:
                thread1 = threading.Thread(target=handle_client, args=(conn, addr))
                thread1.start()
                threads = add_thread_to_tuple(threads, thread1)
                connections.task_done()

    def send_messages_to_client() -> None:
        nonlocal messages
        nonlocal list_connection

        while True:
            if not messages.empty():
                msg = messages.get()
                for conn, addr in list_connection:
                    try:
                        conn.send(msg.encode(FORMAT))
                    except Exception:
                        print("Couldn't send message!")
                messages.task_done()

    def start() -> None:
        nonlocal threads
        nonlocal connections
        nonlocal messages
        nonlocal event

        threads_are_alive = True
        server_socket = create_server_socket()
        threading.Thread(
            target=put_connection_in_queue, args=(server_socket,), daemon=True
        ).start()
        threading.Thread(target=accept_connection_from_queue, daemon=True).start()
        threading.Thread(target=send_messages_to_client, daemon=True).start()

        while threads_are_alive:
            event.wait()
            threads = remove_dead_thread_from_tuple(threads)
            event.clear()
            if threads == ():
                threads_are_alive = False

        server_socket.close()
        print("CLOSING SERVER")

    start()


if __name__ == "__main__":
    server()
