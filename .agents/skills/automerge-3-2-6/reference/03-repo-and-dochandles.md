# Repo and DocHandles

## Contents
- Repo Initialization
- DocHandles
- Storage Adapters
- Networking

## Repo Initialization

`@automerge/automerge-repo` provides the networking and storage plumbing that sits on top of the core `@automerge/automerge` CRDT library. Create one `Repo` per application instance.

```javascript
import { Repo } from "@automerge/automerge-repo"

const repo = new Repo()
```

The Repo manages:
- Document lifecycle (creation, loading, persistence)
- Peer discovery and connection management
- Sync message routing between peers
- Storage adapter coordination

### Package Relationship

- `@automerge/automerge` — CRDT implementation, sync protocol, storage format (core)
- `@automerge/automerge-repo` — networking/storage plumbing, DocHandles, peer management
- `@automerge/automerge-repo-network-*` — network transport adapters
- `@automerge/automerge-repo-storage-*` — persistence adapters
- `@automerge/react` — convenience package re-exporting above + React hooks

## DocHandles

A DocHandle is a reactive handle to a document managed by the Repo. It provides access to the current document state and notifies subscribers of changes.

```javascript
// Create a new document with a URL
const docHandle = repo.create({ title: "New Doc" })
console.log(docHandle.url) // "automerge:<uuid>"

// Find existing document by URL
const docHandle = repo.find("automerge:my-app/todo-list")

// Get current document (may be null if not yet loaded)
const doc = docHandle.doc

// Wait for document to exist (useful after loading from storage)
await docHandle.waitToExist()
const doc = docHandle.doc

// Subscribe to changes
const unsubscribe = docHandle.subscribe((doc) => {
  console.log("Document updated:", doc)
})

// Unsubscribe when done
unsubscribe()

// Make changes through the handle
docHandle.change((doc) => {
  doc.items.push("new item")
})

// Observe (read-only subscription, doesn't count as active observer)
docHandle.observe((doc) => {
  render(doc)
})
```

### DocHandle States

A DocHandle transitions through states:
1. **Initializing** — created but not yet loaded
2. **Active** — document exists and is available via `.doc`
3. **Disposed** — removed from repo (call `docHandle.dispose()`)

### Document URLs

Documents are identified by URLs in the format `automerge:<uuid>`. You can also use custom schemes:

```javascript
const handle = repo.find("myapp://documents/123")
```

The URL scheme helps organize documents by application or feature. Use consistent schemes within your app.

## Storage Adapters

Storage adapters persist documents to disk. Install and configure the adapter you need.

### IndexedDB (Browser)

```javascript
import { IndexedDBStorageAdapter } from "@automerge/automerge-repo-storage-indexeddb"

const repo = new Repo(new IndexedDBStorageAdapter())
```

Documents are automatically saved and loaded. No manual save/load needed.

### Custom Storage Adapter

Implement the `StorageAdapter` interface:

```javascript
class MyStorageAdapter {
  async load(documentUrl) {
    // Return saved document data or null
    return fetchData(documentUrl)
  }

  async save(documentUrl, data) {
    // Persist document data
    await storeData(documentUrl, data)
  }

  async *scan() {
    // Yield all stored document URLs
    for (let url of getAllUrls()) {
      yield url
    }
  }

  async dispose() {
    // Cleanup resources
  }
}
```

### Manual Save/Load (without Repo)

When using `@automerge/automerge` directly without a Repo:

```javascript
import * as Automerge from "@automerge/automerge"

// Full save — entire document
let data = Automerge.save(doc)

// Incremental save — only changes since last save
let incremental = Automerge.saveIncremental(doc, lastHeads)

// Save changes since specific heads
let since = Automerge.saveSince(doc, heads)

// Bundle — full state for transfer to a peer that has nothing
let bundle = Automerge.saveBundle(doc, oldHeads)

// Load from saved data
let loaded = Automerge.load(data)

// Incremental load
let [updated, more] = await Automerge.loadIncremental(loaded, incremental)
// more === true means more data available
```

## Networking

Network adapters define how peers communicate. A Repo can use multiple adapters simultaneously.

### NetworkAdapter Interface

```javascript
class MyNetworkAdapter {
  // Called when repo has sync data to send
  send(documentUrl, syncMessage, peerId) {}

  // Called when repo wants to request a document
  request(documentUrl, peerId) {}

  // Called when document is no longer needed
  forget(documentUrl) {}

  // Start/stop the adapter
  gossip() {}
  dispose() {}

  // Unique peer identifier
  get peerId() { return "my-peer-id" }
}
```

### BroadcastChannel (Same Browser, Multiple Tabs)

```javascript
import { BroadcastChannelNetworkAdapter } from "@automerge/automerge-repo-network-broadcastchannel"

const repo = new Repo(null, new BroadcastChannelNetworkAdapter())
```

Syncs documents between tabs in the same browser. No server needed.

### WebSocket (Client-Server)

```javascript
import { WebSocketNetworkAdapter } from "@automerge/automerge-repo-network-websocket"

// Client
const adapter = new WebSocketNetworkAdapter("ws://localhost:3000", repo)
adapter.connect()

// Server (Node.js)
import { WSServer } from "@automerge/automerge-repo-network-websocket"
const server = new WSServer((peer) => {
  // Optional: filter which documents to share with this peer
  return true
}, { port: 3000 })
```

### WebSocket Peer (Peer-to-Peer via Signaling)

```javascript
import { WebRTCNetworkAdapter } from "@automerge/automerge-repo-network-webrtc"

const adapter = new WebRTCNetworkAdapter(repo)
```

### Sync Server Pattern

A sync server is a long-running Automerge instance that:
1. Listens for WebSocket connections
2. Stores documents on disk
3. Mediates sync between clients

Clients connect to the server, which acts as one peer among many. The server runs the same Automerge code — nothing special about it architecturally.

```javascript
// Community sync server (public)
const adapter = new WebSocketNetworkAdapter(
  "wss://sync.automerge.org",
  repo
)
adapter.connect()
```
