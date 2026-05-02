# Synchronization

## Contents
- Update Encoding & State Vectors
- Y-Sync Protocol
- Provider & Channel
- Awareness

## Update Encoding & State Vectors

pycrdt represents document changes as binary-encoded updates. The synchronization pattern uses **state vectors** to determine what each replica is missing:

```python
from pycrdt import Doc, Text, merge_updates, get_state, get_update

doc_a = Doc()
doc_a["text"] = Text("Hello")

# 1. Remote doc sends its state vector
state_b = doc_b.get_state()          # "I have seen these changes"

# 2. Local doc computes differential update
update = doc_a.get_update(state_b)    # "Here's what you're missing"

# 3. Remote applies the update
doc_b.apply_update(update)

# 4. Repeat in reverse to sync back
state_a = doc_a.get_state()
update_back = doc_b.get_update(state_a)
doc_a.apply_update(update_back)
```

### Module-level helpers

For operating on raw update bytes (e.g., from storage or message queues):

```python
# Merge multiple updates into one
merged = merge_updates(update1, update2, update3)

# Extract state vector from an update
state = get_state(update)

# Get differential update relative to a known state
diff = get_update(accumulated_update, old_state)
```

### Full sync vs incremental

- **Full sync**: `doc.get_update()` with no state argument returns all changes since document creation
- **Incremental**: `doc.get_update(state)` returns only changes not covered by the given state vector
- After applying an update, call `get_update(previous_state)` to get what changed since

## Y-Sync Protocol

The Y-Sync protocol defines a two-step handshake for efficient initial sync plus continuous updates. Use it when building custom transports (WebSockets, TCP, etc.).

### Message types

```python
from pycrdt import (
    YMessageType,          # SYNC=0, AWARENESS=1
    YSyncMessageType,      # SYNC_STEP1=0, SYNC_STEP2=1, SYNC_UPDATE=2
    create_sync_message,
    handle_sync_message,
    create_update_message,
)
```

### Sync handshake

```
Client                          Server
  |                                |
  |-- SYNC_STEP1 (state vector) -->|
  |                                |-- Apply state, compute diff
  |<-- SYNC_STEP2 (diff update) --|
  |                                |
  |<-- SYNC_UPDATE (ongoing) -----| (after initial sync)
```

```python
# Client initiates sync
sync_msg = create_sync_message(doc)       # Creates SYNC_STEP1 with state vector
await channel.send(sync_msg)

# Server receives and replies
reply = handle_sync_message(message[1:], server_doc)
if reply is not None:                      # Only for SYNC_STEP1
    await channel.send(reply)              # Sends SYNC_STEP2

# Ongoing updates (after initial sync)
update_msg = create_update_message(event.update)
await channel.send(update_msg)
```

### Encoder / Decoder

For building custom wire formats on top of Y-Sync:

```python
from pycrdt import Encoder, Decoder

# Encode
enc = Encoder()
enc.write_var_uint(42)
enc.write_var_string("hello")
data = enc.to_bytes()

# Decode
dec = Decoder(data)
num = dec.read_var_uint()           # 42
text = dec.read_var_string()        # "hello"
msg = dec.read_message()            # Read a length-prefixed message
for msg in dec.read_messages():      # Iterate all remaining messages
    process(msg)
```

### handle_sync_message

Processes any incoming sync message and returns a reply only for `SYNC_STEP1`:

```python
# Returns SYNC_STEP2 reply for SYNC_STEP1, None for SYNC_STEP2/SYNC_UPDATE
reply = handle_sync_message(message[1:], doc)
if reply:
    await channel.send(reply)
```

The `message[1:]` strips the outer `YMessageType.SYNC` byte before passing to the handler.

## Provider & Channel

`Provider` abstracts document synchronization over any async byte-stream transport. Implement the `Channel` protocol and pass it to `Provider`:

```python
from pycrdt import Provider, Doc

class WebSocketChannel:
    def __init__(self, websocket, path="/doc1"):
        self._ws = websocket
        self._path = path

    @property
    def path(self) -> str:
        return self._path

    async def send(self, message: bytes) -> None:
        await self._ws.send_bytes(message)

    async def recv(self) -> bytes:
        return await self._ws.recv_bytes()

    def __aiter__(self):
        return self

    async def __anext__(self) -> bytes:
        data = await self.recv()
        if data is None:
            raise StopAsyncIteration
        return data

# Use provider
channel = WebSocketChannel(websocket, path="/doc1")
provider = Provider(doc, channel)

async with provider:
    # Document auto-syncs: initial handshake + continuous updates
    await asyncio.sleep(60)
```

The `Provider` lifecycle:
1. On start: sends `SYNC_STEP1` (full state vector)
2. On reply: processes `SYNC_STEP2` and applies remote updates
3. Continuous: streams local changes as `SYNC_UPDATE` messages
4. On incoming: handles any sync message via `handle_sync_message`

## Awareness

The `Awareness` protocol tracks per-client state (cursor positions, user info, presence) separate from document content. It uses a clock-based update system with automatic timeout cleanup:

```python
from pycrdt import Awareness

awareness = Awareness(doc, outdated_timeout=30000)  # 30s timeout

# Set local state (e.g., cursor position, user info)
awareness.set_local_state({
    "user": "Alice",
    "color": "#ff0000",
    "cursor": {"line": 5, "col": 12},
})

# Update a single field
awareness.set_local_state_field("cursor", {"line": 6, "col": 0})

# Read remote states
for client_id, state in awareness.states.items():
    print(f"Client {client_id}: {state}")

# Metadata (clock, lastUpdated)
print(awareness.meta[client_id]["lastUpdated"])
```

### Encoding / decoding awareness updates

```python
# Encode update for specific clients
update_bytes = awareness.encode_awareness_update([client_id])
await channel.send(update_bytes)

# Apply received update
awareness.apply_awareness_update(received_bytes, origin="remote")
```

### Lifecycle

```python
# Start periodic timeout cleanup (async)
await awareness.start()
# ... runs in background, removes stale clients
await awareness.stop()
```

### Observing awareness changes

```python
sub_id = awareness.observe(lambda topic, (changes, origin):
    added = changes["added"]
    removed = changes["removed"]
    updated = changes["updated"]
    print(f"{topic}: +{added} ~{updated} -{removed}")
)
awareness.unobserve(sub_id)
```

### Disconnect detection

```python
from pycrdt import is_awareness_disconnect_message

if is_awareness_disconnect_message(message):
    # Client disconnected
    pass
```
