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

## Viva Q&A

**What is a socket?**
An endpoint for communication between two machines over a network, identified by IP + port. Here we use TCP sockets (`SOCK_STREAM`), which are reliable and ordered — messages arrive in the order sent, none lost.

**Why TCP and not UDP?**
Chat messages must not be lost or reordered, and TCP guarantees both. UDP is faster but unreliable — fine for video calls, wrong for chat text.

**Why threads?**
The server must serve many clients at once. Without a thread per client, waiting for one client's message would freeze everyone else. Each thread blocks on its own client's socket independently.

**What happens when a client disconnects?**
The server's read loop ends, the `finally` block removes the client from its room and broadcasts a "left" message. No restart needed.

**How do rooms work?**
A dictionary maps room names to member lists. Broadcast only iterates over the sender's room, so rooms are isolated by construction — no extra filtering needed.

**What is the bottleneck / limit?**
One thread per client uses memory, so this design handles tens to hundreds of users comfortably — enough for a demo and coursework. A production system would use async I/O instead of threads.

**Why does the client use two threads?**
Receiving blocks while waiting for messages, and reading input blocks while waiting for typing. Two threads let both happen at once; otherwise you couldn't type while waiting for a message.
