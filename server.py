"""
Real-time Chat App — Server.

Run:  python server.py
Then connect with:  python client.py  (from another terminal)

How it works:
  * The server opens one listening socket on PORT.
  * Every time a client connects, the server starts a NEW THREAD
    just for that client (see handle_client). The main thread goes
    straight back to accepting the next connection, so one slow
    client never blocks the others.
  * Clients never talk to each other directly. Each message goes
    client -> server -> every client in the same room (broadcast).
  * Rooms are just a dictionary: room name -> list of members.
    Broadcasting to a room means looping over that room's list.

Protocol (simple text lines, one message per line):
  * First line the client sends  = username
  * Second line the client sends = room name
  * After that, every line is either a chat message or a command:
      /help                     show commands
      /users                    list users in your room
      /rooms                    list all rooms
      /whisper <user> <msg>     private message to one user
      /quit                     leave the chat
"""

import socket
import threading
from datetime import datetime

HOST = "0.0.0.0"   # listen on all network interfaces (LAN + localhost)
PORT = 5000

# room name -> list of (connection, username)
rooms = {}
rooms_lock = threading.Lock()  # guards `rooms` because threads share it


def timestamp():
    """Current time as HH:MM, for message prefixes."""
    return datetime.now().strftime("%H:%M")


def send(conn, text):
    """Send one line to a client. Silently ignore a dead connection."""
    try:
        conn.sendall((text + "\n").encode())
    except OSError:
        pass


def broadcast(room, text):
    """Send `text` to every member of `room` (including the sender)."""
    with rooms_lock:
        members = list(rooms.get(room, []))
    for conn, _ in members:
        send(conn, text)


def handle_client(conn, addr):
    """Runs in its own thread for one connected client."""
    reader = conn.makefile("r", encoding="utf-8", errors="replace")
    username = None
    room = "general"
    try:
        username = reader.readline().strip()
        room = reader.readline().strip() or "general"
        if not username:      # client connected but sent nothing usable
            return

        with rooms_lock:
            rooms.setdefault(room, []).append((conn, username))
        send(conn, f"[{timestamp()}] Welcome to room '{room}', {username}! Type /help for commands.")
        broadcast(room, f"[{timestamp()}] *** {username} joined '{room}' ***")

        for line in reader:   # blocks until this client sends a line
            msg = line.strip()
            if not msg:
                continue
            if msg == "/quit":
                break
            if msg == "/help":
                send(conn, "Commands: /users, /rooms, /whisper <user> <message>, /quit")
            elif msg == "/users":
                with rooms_lock:
                    names = [u for _, u in rooms.get(room, [])]
                send(conn, f"[{timestamp()}] Users in '{room}': {', '.join(names)}")
            elif msg == "/rooms":
                with rooms_lock:
                    names = [r for r, m in rooms.items() if m]
                send(conn, f"[{timestamp()}] Rooms: {', '.join(names)}")
            elif msg.startswith("/whisper "):
                parts = msg.split(" ", 2)   # /whisper, user, message
                if len(parts) < 3:
                    send(conn, "Usage: /whisper <user> <message>")
                    continue
                target, text = parts[1], parts[2]
                with rooms_lock:
                    target_conn = next(
                        (c for c, u in rooms.get(room, []) if u == target), None)
                if target_conn:
                    send(target_conn, f"[{timestamp()}] (whisper) {username}: {text}")
                    send(conn, f"[{timestamp()}] (whisper to {target}): {text}")
                else:
                    send(conn, f"[{timestamp()}] User '{target}' not found in this room.")
            else:
                broadcast(room, f"[{timestamp()}] {username}: {msg}")
    except OSError:
        pass  # client disconnected abruptly; cleanup below handles it
    finally:
        # Client left (or disconnected): remove from room, tell the rest.
        if username:
            with rooms_lock:
                rooms[room] = [(c, u) for c, u in rooms.get(room, []) if c is not conn]
            broadcast(room, f"[{timestamp()}] *** {username} left '{room}' ***")
        conn.close()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Let us restart the server immediately after stopping it.
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Chat server running on port {PORT}. Press Ctrl+C to stop.")
    try:
        while True:
            conn, addr = server.accept()   # wait for the next client
            print(f"Connected: {addr}")
            # daemon=True: threads die automatically when the server stops.
            threading.Thread(target=handle_client, args=(conn, addr),
                             daemon=True).start()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.close()


if __name__ == "__main__":
    main()
