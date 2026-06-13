# Synchronization and Providers

## Contents
- Document Updates
- Syncing Clients
- Binary Encoding and Server-Side Sync
- Provider Pattern
- Connection Providers
- Persistence Providers
- Awareness CRDT

---

## Document Updates

Yjs encodes all changes as binary `Uint8Array` *document updates*. These updates are **commutative** (order doesn't matter), **associative** (grouping doesn't matter), and **idempotent** (applying the same update twice has no extra effect). This means clients converge to the same state regardless of network ordering.

### Core Functions

```js
import * as Y from 'yjs'

// Apply a remote update
Y.applyUpdate(doc, update: Uint8Array, origin?: any)

// Encode full document state as an update
const state = Y.encodeStateAsUpdate(doc)

// Encode state relative to a target's state vector (delta only)
const diff = Y.encodeStateAsUpdate(doc, targetStateVector)

// Compute state vector (what updates this client has seen)
const sv = Y.encodeStateVector(doc)
```

### Listening for Updates

```js
doc.on('update', (update: Uint8Array, origin: any, doc, tr) => {
  // Forward `update` to other clients or save to database
  // `origin` lets you filter out updates you applied yourself
})
```

---

## Syncing Clients

### Full State Exchange (Simplest)

Send the complete document state. Works when documents are small or on initial connection:

```js
const state1 = Y.encodeStateAsUpdate(doc1)
const state2 = Y.encodeStateAsUpdate(doc2)
Y.applyUpdate(doc1, state2)
Y.applyUpdate(doc2, state1)
```

### Delta Exchange with State Vectors (Bandwidth-Efficient)

Exchange only missing differences. Requires an extra round-trip but saves bandwidth:

```js
const sv1 = Y.encodeStateVector(doc1)
const sv2 = Y.encodeStateVector(doc2)
const diff1 = Y.encodeStateAsUpdate(doc1, sv2)  // what doc2 is missing
const diff2 = Y.encodeStateAsUpdate(doc2, sv1)  // what doc1 is missing
Y.applyUpdate(doc1, diff2)
Y.applyUpdate(doc2, diff1)
```

### Incremental Sync

After initial sync, forward `update` events in real-time:

```js
doc1.on('update', (update, origin) => {
  if (origin !== 'local') return  // don't echo back
  Y.applyUpdate(doc2, update)
})

doc2.on('update', (update, origin) => {
  if (origin !== 'local') return
  Y.applyUpdate(doc1, update)
})
```

### Origin-Based Filtering

Use `transactionOrigin` to avoid redundant packets:

```js
doc1.on('update', (update, origin) => {
  if (origin === 'doc1') return
  sendTo(doc2, update)
})

// When applying remote updates, set origin
Y.applyUpdate(doc1, remoteUpdate, 'doc1')
```

---

## Binary Encoding and Server-Side Sync

Updates are `Uint8Array` binary data. Most protocols support binary natively. For JSON transport, use Base64:

```js
import { fromUint8Array, toUint8Array } from 'js-base64'

const state = Y.encodeStateAsUpdate(doc)
const base64 = fromUint8Array(state)    // Uint8Array → string
const binary = toUint8Array(base64)     // string → Uint8Array
```

### Server-Side Sync Without Loading Y.Doc

Merge and diff updates on the server without loading documents into memory:

```js
// Merge multiple updates into one (smaller than sum of parts)
const merged = Y.mergeUpdates([update1, update2, update3])

// Compute state vector from an encoded update
const sv = Y.encodeStateVectorFromUpdate(merged)

// Compute diff between two updates
const diff = Y.diffUpdate(currentState, remoteStateVector)

// Sync without Y.Doc instances
let serverState = Y.encodeStateAsUpdate(doc)
doc.destroy() // free memory

// Later, merge incoming client diffs
const clientSv = Y.encodeStateVectorFromUpdate(clientState)
const serverDiff = Y.diffUpdate(serverState, clientSv)
serverState = Y.mergeUpdates([serverState, clientState])
```

**Note:** Server-side merging doesn't garbage-collect deleted content. Periodically load into a `Y.Doc` to reduce document size.

---

## Provider Pattern

A provider connects a Yjs document to a network or database. The recommended pattern uses `lib0/observable`:

```js
import * as Y from 'yjs'
import { Observable } from 'lib0/observable'

class MyProvider extends Observable {
  constructor(ydoc) {
    super()

    // Capture local changes
    ydoc.on('update', (update, origin) => {
      if (origin !== this) {
        this.emit('handleUpdate', [update])
      }
    })

    // Apply remote changes
    this.on('handleUpdate', (update) => {
      Y.applyUpdate(ydoc, update, this)
    })
  }

  destroy() {
    super.destroy()
  }
}
```

The `origin` parameter in `Y.applyUpdate` and the `origin` check in the `update` handler prevent echo loops.

---

## Connection Providers

Connection providers handle network synchronization between peers.

### y-websocket

Central server architecture. Clients connect to a WebSocket server that broadcasts updates to all connected peers.

```js
import { WebsocketProvider } from 'y-websocket'
const provider = new WebsocketProvider('wss://example.com', 'room-name', doc)
```

Server: `node ./node_modules/y-websocket/bin/server.cjs`

### y-webrtc

Peer-to-peer using WebRTC. Peers exchange signaling data over a public signaling server.

```js
import { WebrtcProvider } from 'y-webrtc'
const provider = new WebrtcProvider('room-name', doc)
```

Supports encrypted communication via shared secret.

### Other Notable Providers

| Provider | Type | Notes |
|----------|------|-------|
| **Hocuspocus** | Standalone server | SQLite persistence, webhooks, auth, extensible (by Tiptap team) |
| **Liveblocks** | Hosted service | Full managed WebSocket + data store, REST API, DevTools |
| **y-sweet** | Standalone/serverless | S3 or filesystem persistence, cloud service available |
| **y-libp2p** | P2P | Uses libp2p GossipSub for mesh networking |
| **PartyKit** | Cloud platform | Multiplayer app infrastructure |
| **Matrix-CRDT** | Federation | Uses Matrix protocol for transport and storage |
| **nostr-crdt** | Decentralized | Syncs over nostr relay network |
| **y-electric** | SQL sync | Sync Yjs over ElectricSQL |

---

## Persistence Providers

Persistence providers store document updates locally or in a database, enabling offline editing.

### y-indexeddb (Browser)

```js
import { IndexeddbPersistence } from 'y-indexeddb'
const persistence = new IndexeddbPersistence('app-name', doc)

persistence.whenSynced.then(() => {
  console.log('loaded from indexeddb')
})
```

Provides instant document loading from local cache. Only diffs sync over the network.

### Other Persistence Options

| Provider | Storage | Notes |
|----------|---------|-------|
| **y-mongodb-provider** | MongoDB | Server-side, compatible with y-websocket |
| **y-postgresql** | PostgreSQL | Server-side, compatible with y-websocket |
| **y-fire** | Firestore | Database + connection provider combined |
| **y-op-sqlite** | SQLite (React Native) | Fastest SQLite for React Native |

### Combining Providers

Use a persistence provider + network provider together:

```js
const doc = new Y.Doc()

// Load from local cache first
new IndexeddbPersistence('my-app', doc)

// Then sync with network
new WebsocketProvider('wss://example.com', 'room', doc)
```

---

## Awareness CRDT

Awareness tracks user presence (who is online, cursor positions, usernames). It is defined in `y-protocols`, not the core `yjs` package. Providers typically implement it.

```js
import * as awarenessProtocol from 'y-protocols/awareness.js'

const awareness = new awarenessProtocol.Awareness(doc)
// Usually accessed via provider:
const awareness = provider.awareness
```

### Methods

- `awareness.getLocalState(): Object | null` — Get local awareness state.
- `awareness.setLocalState(state: Object | null)` — Set/update local state. Pass `null` to mark offline. Values must be JSON-encodable.
- `awareness.setLocalStateField(key, value)` — Update a single field.
- `awareness.getStates(): Map<number, Object>` — All awareness states (maps clientID → state).
- `awareness.clientID: number` — This client's ID.
- `awareness.destroy()` — Clean up.

### Events

```js
// Fires on every heartbeat (even if state unchanged) — use for propagation
awareness.on('update', ({ added, updated, removed }) => {
  const changedClients = added.concat(updated).concat(removed)
  broadcast(awarenessProtocol.encodeAwarenessUpdate(awareness, changedClients))
})

// Fires only when state actually changes — use for UI updates
awareness.on('change', ({ added, updated, removed }) => {
  // Update cursor positions, user list, etc.
})
```

### Provider Implementation

```js
// Encode awareness states for network transmission
const encoded = awarenessProtocol.encodeAwarenessUpdate(awareness, clientIds)

// Apply received awareness update
awarenessProtocol.applyAwarenessUpdate(awareness, encodedUpdate, origin)

// Mark clients as offline (call when connection closes)
awarenessProtocol.removeAwarenessStates(awareness, clientIds, 'connection closed')
```

### Timeout Behavior

If a client doesn't broadcast its state for 30 seconds, it is marked offline. Each client must regularly update its awareness state to stay "online."

### Common Patterns

```js
// Announce offline on page close
window.addEventListener('beforeunload', () => {
  awarenessProtocol.removeAwarenessStates(
    awareness, [doc.clientID], 'window unload'
  )
})

// Mark all remote clients offline on disconnect
websocket.onclose = () => {
  const remoteClients = Array.from(awareness.getStates().keys())
    .filter(id => id !== doc.clientID)
  awarenessProtocol.removeAwarenessStates(awareness, remoteClients, 'disconnected')
}
```
