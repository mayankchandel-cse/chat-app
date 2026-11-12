# Real-time Chat App

A multi-user chat app in pure Python (standard library only — no installs, no internet).
Multiple users connect to one server and messages appear instantly for everyone in the same room.

## How to run (Windows)

1. Open the `chat-app` folder.
2. Click the address bar in File Explorer, type `cmd`, press Enter — a terminal opens in this folder.
3. Start the server:
   ```
   python server.py
   ```
   Leave this terminal running.
4. Open a second terminal the same way and start a client:
   ```
   python client.py
   ```
   Enter a username and a room (press Enter for `general`).
5. Open a third terminal, run `python client.py` again with a different username and the same room — type in one window and watch it appear in the other.

To chat with friends on the same Wi-Fi: they run `python client.py` and enter *your* computer's IP instead of localhost.

## How it works

```
Client A ─┐
Client B ─┼── Server ── forwards each message to the whole room
Client C ─┘
```

- **Sockets:** a socket is an endpoint for sending data over a network. The server listens on port 5000; each client connects to it and the connection stays open, which is what makes messages instant.
- **Threading:** the server starts one thread per client. The main thread keeps accepting new connections while each client thread waits for that client's messages. One slow client never blocks the others.
- **Broadcast:** the server keeps a dictionary of rooms (`room name → list of members`). Sending a message = looping over that room's members and sending the line to each.
- **Rooms:** clients only receive messages from their own room, because broadcast looks up only that room's member list.

## Commands (type in the client)

| Command | What it does |
|---|---|
| `/help` | Show commands |
| `/users` | List users in your room |
| `/rooms` | List all active rooms |
| `/whisper <user> <message>` | Private message to one user |
| `/quit` | Leave the chat |

## Files

- `server.py` — accepts clients, one thread each, broadcast + rooms + whispers
- `client.py` — sends what you type, prints what the server sends back (two threads so typing and receiving never block each other)

