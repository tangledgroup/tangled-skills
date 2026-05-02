# Ecosystem and Ports

## Contents
- Editor Bindings
- Non-Editor Bindings
- Ports to Other Languages
- Tooling
- Scaling Patterns

---

## Editor Bindings

Yjs integrates with major text editors through binding libraries. All editor bindings support shared cursors.

### Rich Text Editors

| Editor | Binding | Notes |
|--------|---------|-------|
| **ProseMirror** | `y-prosemirror` | Foundation for Tiptap, BlockNote, Milkdown |
| **Tiptap** | via `y-prosemirror` | Headless rich-text framework (by Hocuspocus team) |
| **Quill** | `y-quill` | Delta format native compatibility |
| **Lexical** | native | Built-in Yjs collaboration support |
| **BlockSuite** | native | Native Yjs integration |
| **Milkdown** | via `y-prosemirror` | Markdown editor |
| **BlockNote** | via `y-prosemirror` | Block-based editor |

### Code Editors

| Editor | Binding | Notes |
|--------|---------|-------|
| **CodeMirror** | `y-codemirror` | Full cursor support |
| **Monaco** | `y-monaco` | VS Code's editor engine |
| **Ace** | `y-ace` | Community-maintained |

### Other Editors

| Editor | Binding | Notes |
|--------|---------|-------|
| **Slate** | `slate-yjs` | React-based editable |
| **Remirror** | via `y-prosemirror` | ProseMirror wrapper for React |
| **Superdoc** | native | Native Yjs support |

### Typical Integration Pattern

```js
import * as Y from 'yjs'
import { WebsocketProvider } from 'y-websocket'
import { bindStateAndChangesToContent } from 'y-prosemirror'

const doc = new Y.Doc()
const provider = new WebsocketProvider('wss://example.com', 'room', doc)
const yxmlFragment = doc.getXmlFragment('content')

// Bind editor to Yjs shared type
bindStateAndChangesToContent(yxmlFragment, schema, [
  new Plugin({ view: (view) => ({
    // cursor rendering
  })})
], view, view.state)
```

---

## Non-Editor Bindings

Bind Yjs shared types to state management libraries for non-editor collaborative features.

| Library | Binding | Use Case |
|---------|---------|----------|
| **React** | `react-yjs` | Reactive Yjs types in React components |
| **valtio** | `valtio-yjs` | Proxy-based reactive state with Yjs |
| **immer** | `immer-yjs` | Immutable updates synced via Yjs |
| **SyncedStore** | `syncedstore.org` | React/Vue/Svelte/MobX bindings |
| **mobx-keystone** | `mobx-keystone-yjs` | MobX state trees with Yjs sync |
| **PSPDFKit** | `yjs-pspdfkit` | Collaborative PDF annotation |

### react-yjs Example

```js
import { useYArray, useYMap, useYText } from 'react-yjs'

function Component() {
  const ytext = useYText(doc, 'title')
  const items = useYArray(doc, 'items')

  return (
    <div>
      <h1>{ytext.toString()}</h1>
      <ul>
        {items.toArray().map((item, i) => <li key={i}>{item}</li>)}
      </ul>
    </div>
  )
}
```

---

## Ports to Other Languages

Yjs CRDT protocol is implemented in multiple languages via the `y-crdt` project. All ports share the same binary update format, enabling cross-language collaboration.

### Rust (Primary Port)

| Crate | Description |
|-------|-------------|
| **yrs** (`y-crdt/yrs`) | Rust interface — full Yjs-compatible CRDT engine |
| **y-octo** | AFFiNE's independent Rust implementation |

### Language Bindings (via y-crdt)

| Binding | Language | Package |
|---------|----------|---------|
| **ypy** | Python | `pip install ypy-websocket` |
| **yrb** | Ruby | `gem install yrb` |
| **yswift** | Swift | iOS/macOS native |
| **yffi** | C FFI | Embed in any language with C bindings |
| **ywasm** | WebAssembly | Run Rust Yjs in browsers |
| **y_ex** | Elixir | Erlang/Elixir integration |

### .NET

| Package | Description |
|---------|-------------|
| **ycs** | C#/.NET compatible implementation |

### Python Ecosystem

```bash
# ypy-websocket: Python WebSocket server for Yjs
pip install ypy-websocket

# Run a Yjs-compatible WebSocket server
python -m ypy_websocket
```

Python's `ypy` provides the same shared types (Y.Map, Y.Array, Y.Text) with identical binary update format as JavaScript.

---

## Tooling

### Utilities

| Tool | Description |
|------|-------------|
| **y-utility** | `YMultiDocUndoManager` (cross-doc undo/redo), `YKeyValue` (optimized key-value store) |
| **yjs-orderedtree** | Ordered tree class via Y.Map — insert/delete/move for folder hierarchies |
| **y-protocols** | Awareness CRDT and sync protocol utilities |

### Debugging

| Tool | Description |
|------|-------------|
| **Yjs Inspector** (inspector.yjs.dev) | Browser extension for inspecting Yjs documents |
| **Liveblocks DevTools** | Browser DevTools extension with Yjs webhook events |
| **y-sweet Debugger** | Cloud debugger for y-sweet deployments |
| **Y.logUpdate()** | Experimental — log binary update contents to console |

---

## Scaling Patterns

### Small Scale (Single Server)

```
Client → y-websocket server → MongoDB/PostgreSQL
```

One WebSocket server handles all clients. Suitable for hundreds of concurrent users per room.

### Medium Scale (Multiple Servers + Redis)

```
Client → y-redis → Multiple application servers
```

`y-redis` uses Redis pub/sub to distribute updates across multiple application servers. Each server connects to the same Redis instance and shares document state.

### Large Scale (Hierarchical)

For indefinite scaling, use a hierarchical architecture where rooms are partitioned and synced through a central database. Providers like Hocuspocus and Liveblocks handle this internally.

### Provider Meshing

Multiple providers can work together on the same document:

```js
const doc = new Y.Doc()

// P2P for low latency between nearby clients
new WebrtcProvider('room', doc)

// WebSocket server for persistence and bridging
new WebsocketProvider('wss://example.com', 'room', doc)

// Local cache for offline support
new IndexeddbPersistence('app', doc)
```

The origin-based filtering in the provider pattern prevents echo loops between providers. Each provider sets its own transaction origin, and filters out updates it applied.

### Persistence Strategy

1. **Client-side** (y-indexeddb): Instant load from cache, diffs sync over network
2. **Server-side** (MongoDB/PostgreSQL/SQLite): Persist full document state or incremental updates
3. **Hybrid**: Client cache + server persistence for offline-first with durable storage

### Server-Side Update Merging

For high-traffic servers, use `Y.mergeUpdates()` to consolidate stored updates:

```js
// Store only the merged state, not every individual update
let persistedState = Y.mergeUpdates([existingState, newUpdate])
db.save(documentId, persistedState)
```

This reduces storage and improves load performance. Periodically load into a `Y.Doc` for garbage collection.
