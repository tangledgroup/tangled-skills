---
name: automerge-3-2-6
description: CRDT library for building collaborative, local-first applications with automatic conflict-free merging. Provides JSON-like documents with maps, lists, text, rich text, and counters that sync across peers offline. Use when building multiplayer apps, collaborative editors, offline-first tools, or any application requiring concurrent edits with guaranteed convergence.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - automerge
  - crdt
  - local-first
  - collaborative-editing
  - offline-sync
category: library
external_references:
  - https://automerge.org/
  - https://github.com/automerge/automerge/tree/js/automerge-3.2.6
  - https://github.com/automerge/automerge.github.io
---

# Automerge 3.2.6

## Overview

Automerge is a library of data structures for building collaborative, local-first applications. It implements Conflict-Free Replicated Datatypes (CRDTs) that allow multiple users to independently modify shared data — even while offline — with guaranteed automatic convergence when documents sync.

An Automerge document is an immutable snapshot of application state at one point in time. Every change or merge produces a new document, making it compatible with functional reactive patterns (React, SolidJS). The library handles merging internally: concurrent edits to different properties combine cleanly, list insertions use RGA sequences for intent preservation, and text uses the peritext CRDT for collaborative editing.

Automerge is implemented in Rust and compiled to WebAssembly for JavaScript environments. Separate bindings exist for Rust, Swift, Python, and C.

**Design principles:**

- **Network-agnostic** — works with any transport (WebSocket, WebRTC, BroadcastChannel, Bluetooth) or even offline file exchange
- **Immutable state** — every change returns a new document; no in-place mutation
- **Offline-first** — full functionality without network; sync when available

## When to Use

- Building collaborative editing applications (docs, task lists, whiteboards)
- Multiplayer apps requiring real-time sync with offline support
- Applications where multiple users edit the same data concurrently
- Local-first architecture where data lives on the device first
- Replacing server-authoritative state management with peer-to-peer CRDTs
- Building rich text editors with collaborative formatting (marks, blocks)
- Syncing application state across a user's own devices

## Core Concepts

**Document** — The unit of change. Like a JSON object combined with a git repository. Has a URL for sharing. Carries full history enabling versioning, diffing, and branching.

**Change** — A modification to a document wrapped in `Automerge.change(doc, (doc) => { ... })`. Returns a new immutable document. Changes are attributed to an actor ID and can be inspected.

**Patch** — A description of what changed (put, del, insert, inc, spliceText). Obtained by passing a callback to `change()`. Patches can be applied to other documents via `applyPatch()`.

**Repo** — From `@automerge/automerge-repo`. Manages networking and storage plumbing. You create one Repo per application instance; it handles document lifecycle, peer discovery, and sync.

**DocHandle** — A reactive handle to a document managed by a Repo. Provides `.doc` (current state), `.subscribe()` for change notifications, and methods for making changes through the repo.

## Quick Start

### Installation

```bash
npm install @automerge/automerge @automerge/automerge-repo
```

For React apps, use the convenience package:

```bash
npm install @automerge/react
```

### Basic Document Operations

```javascript
import * as Automerge from "@automerge/automerge"

// Create a new document
let doc = Automerge.init()

// Make changes inside a change function
doc = Automerge.change(doc, (d) => {
  d.tasks = [{ title: "Buy milk", done: false }]
  d.title = "My Tasks"
})

// Read values (always read from the current doc, never mutate directly)
console.log(doc.title) // "My Tasks"

// Merge two concurrent documents
let doc1 = Automerge.change(Automerge.init(), (d) => { d.name = "Alice" })
let doc2 = Automerge.change(Automerge.init(), (d) => { d.age = 30 })
let merged = Automerge.merge(doc1, doc2)
// merged = { name: "Alice", age: 30 }

// Save to binary and load back
let saved = Automerge.save(doc)
let loaded = Automerge.load(saved)
```

### With Repo (storage + networking)

```javascript
import { Repo } from "@automerge/automerge-repo"
import { IndexedDBStorageAdapter } from "@automerge/automerge-repo-storage-indexeddb"
import { BroadcastChannelNetworkAdapter } from "@automerge/automerge-repo-network-broadcastchannel"

const repo = new Repo(
  new IndexedDBStorageAdapter(),
  new BroadcastChannelNetworkAdapter()
)

// Create or find a document by URL
const docHandle = repo.find("automerge:my-app/todo-list")

// Get current document
const doc = docHandle.doc

// Subscribe to changes
docHandle.subscribe((doc) => {
  console.log("Document updated:", doc)
})

// Make changes through the handle
docHandle.change((doc) => {
  doc.completed = (doc.completed || 0) + 1
})
```

### React Integration

```jsx
import { RepoProvider, useDoc } from "@automerge/react"

function App() {
  return (
    <RepoProvider>
      <TaskList />
    </RepoProvider>
  )
}

function TaskList() {
  const [doc, change] = useDoc({ tasks: [] }, "my-todo-list")

  return (
    <div>
      {doc.tasks.map((task, i) => (
        <div key={i}>{task.title}</div>
      ))}
      <button onClick={() => change((d) => {
        d.tasks.push({ title: "New task", done: false })
      })}>
        Add Task
      </button>
    </div>
  )
}
```

## Advanced Topics

**Data Types**: Maps, lists, text, rich text (marks/blocks), counters, conflicts → [Data Types](reference/01-data-types.md)

**Changes and Patches**: Change model, patch callbacks, history, diffing, heads/branches → [Changes and Patches](reference/02-changes-and-patches.md)

**Repo and DocHandles**: Repository initialization, document handles, storage adapters, networking transports → [Repo and DocHandles](reference/03-repo-and-dochandles.md)

**React Integration**: `@automerge/react` hooks, patterns, `@automerge/vanillajs` → [React Integration](reference/04-react-integration.md)

**Advanced Features**: Ephemeral data, deep references, cursors, blocks → [Advanced Features](reference/05-advanced-features.md)

**Under the Hood**: Merge rules, storage format, rich text schema, WASM initialization → [Under the Hood](reference/06-under-the-hood.md)
