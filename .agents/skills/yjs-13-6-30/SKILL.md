---
name: yjs-13-6-30
description: CRDT framework that exposes shared types (Y.Map, Y.Array, Y.Text, Y.XmlFragment) for conflict-free collaborative editing. Provides network-agnostic document synchronization via binary updates, awareness/presence tracking, undo/redo with selective scoping, relative positions for stable cursors, lazy-loaded subdocuments, and a delta-format event system. Use when building real-time collaborative editors, multi-user data sync, offline-first applications, shared cursors, or any app requiring concurrent editing without merge conflicts across WebSocket, WebRTC, or custom transports.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - yjs
  - crdt
  - collaborative-editing
  - real-time
  - shared-types
  - javascript
category: library
external_references:
  - https://yjs.dev/
  - https://docs.yjs.dev/
  - https://github.com/yjs/yjs/tree/v13.6.30
---

# Yjs 13.6.30

## Overview

Yjs is a CRDT implementation that exposes its internal data structures as *shared types* — familiar JavaScript data types (Map, Array, Text) whose changes automatically distribute to peers and merge without conflicts. It is network-agnostic (works over WebSocket, WebRTC, or any custom transport), supports offline editing, version snapshots, undo/redo, and shared cursors. Yjs scales to unlimited users and handles large documents efficiently.

Yjs itself provides **only the CRDT engine**. Network sync, persistence, awareness, and editor bindings are separate modules in the Yjs ecosystem.

## When to Use

- Building collaborative text/code editors with real-time multi-user editing
- Synchronizing shared data structures across multiple clients (forms, kanban boards, whiteboards)
- Implementing offline-first applications where changes merge conflict-free when reconnected
- Adding shared cursors and presence indicators to any UI
- Integrating with rich-text editors (ProseMirror, Tiptap, Quill, CodeMirror, Monaco, Lexical)
- Building custom sync backends using Yjs's binary update format

## Installation

```bash
npm i yjs
# or
pnpm add yjs
# or
yarn add yjs
```

For a complete collaborative setup, also install a provider:

```bash
npm i yjs y-websocket   # central server (WebSocket)
npm i yjs y-webrtc      # peer-to-peer (WebRTC)
npm i yjs y-indexeddb   # offline persistence (browser)
```

## Core Concepts

### Y.Doc — The Document Root

Every Yjs application starts with a `Y.Doc` instance. It holds shared types and manages transactions:

```js
import * as Y from 'yjs'

const doc = new Y.Doc()
const ymap = doc.getMap('my-map')
const yarray = doc.getArray('my-array')
const ytext = doc.getText('my-text')
```

Shared types are defined by name within a document. Each type exists only once per document — attempting to nest the same shared type instance twice throws an error.

### Transactions

All changes happen inside transactions. Bundle related changes into one transaction to fire a single event:

```js
doc.transact(() => {
  ymap.set('a', 1)
  ymap.set('b', 2)
  yarray.insert(0, ['item'])
}) // fires one combined event, not three
```

### Shared Types

Yjs provides six shared types, all observable for changes:

| Type | Purpose |
|------|---------|
| `Y.Map` | Key-value store (like `Map`) |
| `Y.Array` | Ordered sequence (like `Array`) |
| `Y.Text` | Rich text with formatting attributes |
| `Y.XmlFragment` | Container for XML nodes |
| `Y.XmlElement` | Named XML element with attributes and children |
| `Y.XmlText` | Text node inside XML (extends Y.Text) |

### Document Updates

Changes are encoded as binary `Uint8Array` *document updates* that are **commutative, associative, and idempotent** — they can be applied in any order, multiple times, and all clients converge to the same state:

```js
// Listen for local changes
doc.on('update', (update) => {
  // send `update` to other clients
})

// Apply remote changes
Y.applyUpdate(doc, updateFromNetwork)
```

### Awareness

Awareness is a separate CRDT (from `y-protocols`) that tracks user presence — who is online, cursor positions, usernames. It is typically implemented by providers, not the core library.

## Usage Examples

### Basic Collaboration Pattern

```js
import * as Y from 'yjs'
import { WebrtcProvider } from 'y-webrtc'

const doc = new Y.Doc()
const provider = new WebrtcProvider('my-room', doc)

const ytext = doc.getText('content')
ytext.insert(0, 'Hello collaborative world!')

// Observe changes (local + remote)
ytext.observe((event) => {
  console.log('Text changed:', ytext.toString())
})

// Cleanup on unload
window.addEventListener('beforeunload', () => {
  provider.destroy()
  doc.destroy()
})
```

### Combining Multiple Providers

```js
import * as Y from 'yjs'
import { WebsocketProvider } from 'y-websocket'
import { IndexeddbPersistence } from 'y-indexeddb'

const doc = new Y.Doc()

// Load from local cache first (instant)
new IndexeddbPersistence('my-app', doc)

// Sync with server
new WebsocketProvider('wss://example.com', 'my-room', doc)
```

### Undo/Redo

```js
import * as Y from 'yjs'

const doc = new Y.Doc()
const ytext = doc.getText('content')
const undoManager = new Y.UndoManager(ytext)

ytext.insert(0, 'abc')
undoManager.undo()   // ytext.toString() => ''
undoManager.redo()   // ytext.toString() => 'abc'

// Separate undo steps
ytext.insert(0, 'a')
undoManager.stopCapturing()
ytext.insert(0, 'b')
undoManager.undo()   // only removes 'b'
```

## Advanced Topics

**Shared Types and Y.Doc**: Complete API for Y.Doc, Y.Map, Y.Array, Y.Text, Y.XmlFragment, Y.XmlElement, Y.XmlText → [Shared Types and Y.Doc](reference/01-shared-types-and-ydoc.md)

**Synchronization and Providers**: Document updates, state vectors, client syncing patterns, connection providers (y-websocket, y-webrtc, etc.), persistence providers, awareness CRDT → [Synchronization and Providers](reference/02-synchronization-and-providers.md)

**Advanced Features**: UndoManager with tracked origins, relative positions for stable cursors, subdocuments for lazy loading, delta format for change descriptions, event system → [Advanced Features](reference/03-advanced-features.md)

**Ecosystem and Ports**: Editor bindings (ProseMirror, Tiptap, Quill, CodeMirror, Monaco), language ports (Rust/yrs, Python/ypy, Ruby/yrb, .NET/ycs), tooling, scaling patterns → [Ecosystem and Ports](reference/04-ecosystem-and-ports.md)
