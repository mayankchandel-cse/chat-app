"""
Real-time Chat App — Client.

Run:  python client.py
You will be asked for: server IP, port, username, room.

How it works:
  * One thread (receive_loop) only listens for messages from the
    server and prints them. The main thread only reads what YOU
    type and sends it. Two threads are needed because receiving
    and typing must happen at the same time — if one thread did
    both, you could not type while waiting for a message.
  * Your own messages come back from the server like everyone
    else's (the server broadcasts to the whole room, including
    the sender), so this client never prints what you typed
    itself — it only prints what the server sends back.
"""

import socket
import sys
import threading


def receive_loop(sock):
    """Print every line the server sends, until it disconnects."""
    reader = sock.makefile("r", encoding="utf-8", errors="replace")
    for line in reader:
        print(line.rstrip())
    print("Disconnected from server. Press Enter to exit.")


def main():
    host = input("Server IP (press Enter for localhost): ").strip() or "127.0.0.1"
    port = int(input("Port (press Enter for 5000): ").strip() or 5000)
    username = input("Username: ").strip()
    room = input("Room (press Enter for 'general'): ").strip() or "general"

    sock = socket.create_connection((host, port))
    # Protocol: first line = username, second line = room.
    sock.sendall((username + "\n").encode())
    sock.sendall((room + "\n").encode())

    threading.Thread(target=receive_loop, args=(sock,), daemon=True).start()

    print(f"Connected as {username} in room '{room}'. Type /quit to leave.")
    try:
        for line in sys.stdin:          # read what you type
            msg = line.rstrip("\n")
            if msg:
                sock.sendall((msg + "\n").encode())
            if msg == "/quit":
                break
    except KeyboardInterrupt:
        pass
    sock.close()


if __name__ == "__main__":
    main()
