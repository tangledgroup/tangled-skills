# Libraries and Ecosystem

## Contents
- Yjs
- Automerge
- Loro
- pycrdt (Python)
- Other Notable Libraries
- CRDT-Enabled Databases
- Production Applications

## Yjs

Yjs is the most widely used CRDT library, optimized for collaborative text editing using the YATA algorithm. Written in JavaScript/TypeScript with a modular architecture.

**Key features**:
- YATA sequence CRDT (faster than Automerge for text operations)
- Delta-state sync with state vectors
- Awareness/presence tracking (cursors, selections)
- Bindings for CodeMirror, Monaco, Quill, ProseMirror
- Encoded binary updates (compact network messages)

```javascript
import * as Y from 'yjs';

const doc = new Y.Doc();
const text = doc.getText('shared');
text.insert(0, 'Hello');
text.insert(5, ' World');

// Sync: emit updates on local changes
doc.on('update', (update) => sendToPeers(update));

// Apply remote updates
function onRemoteUpdate(update) {
  Y.applyUpdate(doc, update);
}
```

**Used by**: JupyterLab, Nimbus Note, Serenity Notes, PeerPad, Room.sh.

## Automerge

Automerge implements a JSON-like CRDT data model. Originally JavaScript, rewritten in Rust with WebAssembly bindings for performance. Uses columnar encoding for efficient storage.

**Key features**:
- JSON-compatible data model (maps, arrays, text, counters)
- Conflict-free merging of concurrent edits
- Change history (can replay, fork, or inspect document history)
- `automerge-repo` layer handles networking and persistence separately
- Rust core with JS/Python bindings

```javascript
import { change, merge } from 'automerge';

let doc = change(automerge.init(), doc => {
  doc.title = 'Hello';
  doc.tags = ['crdt', 'collaboration'];
});

// Merge concurrent edits
let merged = merge(doc1, doc2);
```

**Paper**: "A Conflict-Free Replicated JSON Datatype" (Kleppmann et al., 2017).

**Used by**: PushPin, PixelPusher, Trellis, Capstone, Archbee.

## Loro

Loro is a newer CRDT library based on Replayable Event Graph, supporting rich text, lists, maps, and movable trees. Implemented in Rust with JavaScript bindings.

**Key features**:
- Rich text with formatting (bold, italic, links)
- Movable tree (reorderable nested structures)
- Delta-state sync
- Designed for document collaboration (Notion-like editors)

## pycrdt (Python)

Python bindings for Yrs, the Rust port of Yjs. Provides shared data types (Text, Array, Map, XML) with automatic merge of concurrent edits across replicas.

```python
from pycrdt import Doc, Text

doc = Doc()
text = Text()
doc.root.map.set('content', text)
text.insert(0, 'Hello')

# Encode changes for sync
updates = doc.get_updates()
# Apply remote updates
doc.apply_updates(remote_updates)
```

**Used by**: Mempalace (local AI memory system).

## Other Notable Libraries

- **Collabs** (TypeScript): Collection of common CRDTs with custom datatype extension support
- **Ron** (Replicated Object Notation): Data format for encoding CRDT operations, implemented in C++, Elixir, Go, Haskell, Java, JavaScript, Rust
- **Diamond Types**: CRDT for plain text
- **cola**: Another plain text CRDT
- **json-joy**: JSON CRDT specification implementation
- **Akka Distributed Data**: Scala/Java CRDTs in the Akka actor framework
- **Schism** (Clojure): Multiple CRDT implementations
- **Lasp types** (Erlang): CRDTs from the Lasp distributed system
- **Dart CRDT**: Complete Dart/Flutter-native implementation
- **sql_crdt** (Dart): CRDTs backed by SQLite/PostgreSQL
- **Eips** (Rust): List CRDT with logarithmic-time operations, no interleaving issues

## CRDT-Enabled Databases

- **Riak**: One of the first production CRDT databases (2012). Implements counters, sets, maps as native data types using delta CRDTs internally. Used by League of Legends chat (7.5M concurrent users, 11K msg/s) and Bet365.
- **AntidoteDB**: Geo-replicated database designed from the ground up around CRDT semantics. Supports highly available transactions over CRDTs with causal consistency.
- **Redis Enterprise**: Uses operation-based CRDTs for Active-Active geo-distribution between datacenters. Supports strings, hashes, sets, sorted sets with CRDT semantics.
- **Azure CosmosDB**: Allows conflicting values to be merged using CRDTs or custom merge procedures.
- **ElectricSQL**: Local-first SQL system based on AntidoteDB and Rich-CRDTs.
- **Concordant**: Edge-first database spanning cloud-edge spectrum, supports delta-based CRDTs with "just-right consistency."
- **HarperDB**: Uses CRDTs to reconcile transactions across globally-distributed platform.
- **RxDB**: NoSQL document database with optional CRDT plugin for replication.

## Production Applications

- **Apple Notes**: Uses CRDTs for syncing offline edits between iOS devices (evidenced by `TTMergeableString.h` in iOS runtime headers)
- **Zed**: High-performance multiplayer code editor from Atom/Tree-sitter creators, written in Rust with CRDT-based collaboration
- **Teletype for Atom**: Real-time collaborative editing via CRDT (Atom's teletype-crdt)
- **Figma**: Server-authoritative LWW-like replication per property; fractional indexing for ordered sequences (layer ordering) — CRDT-inspired but not pure CRDT
- **SoundCloud (Roshi)**: Open-sourced LWW-element-set CRDT on top of Redis for the SoundCloud stream
- **League of Legends**: Riak CRDT implementation for in-game chat
- **TomTom**: CRDTs for synchronizing navigation data between user devices
- **Facebook Apollo**: Low-latency database with CRDT support
- **Actual Budget**: Uses CRDTs for sync across multiple user devices
- **Pixelboard**: Collaborative whiteboarding app using CRDTs for concurrent drawing
