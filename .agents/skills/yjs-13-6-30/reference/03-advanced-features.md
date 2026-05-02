# Advanced Features

## Contents
- Y.UndoManager
- Y.RelativePosition
- Subdocuments
- Delta Format
- Y.Event
- Internals Overview

---

## Y.UndoManager

Selective undo/redo scoped to specific shared types or transaction origins.

```js
import * as Y from 'yjs'

const ytext = doc.getText('content')
const undoManager = new Y.UndoManager(ytext)

ytext.insert(0, 'abc')
undoManager.undo()    // ytext.toString() => ''
undoManager.redo()    // ytext.toString() => 'abc'
```

### Constructor Options

```js
new Y.UndoManager(scope: Y.AbstractType | Array<Y.AbstractType>, {
  captureTimeout: number,      // ms to merge consecutive edits (default: 500)
  trackedOrigins: Set<any>,    // which transaction origins to track
  deleteFilter: (item) => bool // filter items that should be undoable
})
```

- `scope` — Single type or array of types to track. Changes to these types or their children are captured.
- `captureTimeout` — Edits within this window are merged into one undo step. Set to `0` for individual captures.
- `trackedOrigins` — By default, changes with no `origin` (null) are tracked. Specify a Set to track only specific origins. The UndoManager instance itself is always added to tracked origins.

### Methods

- `undoManager.undo()` — Undo last operation. Reverse goes on redo stack.
- `undoManager.redo()` — Redo last undone operation.
- `undoManager.stopCapturing()` — Ensure next operation starts a new undo step (don't merge with previous).
- `undoManager.clear()` — Clear both undo and redo stacks.

### Separate Undo Steps

```js
// Without stopCapturing — merged into one step
ytext.insert(0, 'a')
ytext.insert(1, 'b')
undoManager.undo()  // removes 'ab'

// With stopCapturing — separate steps
ytext.insert(0, 'a')
undoManager.stopCapturing()
ytext.insert(0, 'b')
undoManager.undo()  // only removes 'b'
```

### Origin Tracking

Control which changes are undoable via transaction origins:

```js
class CustomBinding {}

const undoManager = new Y.UndoManager(ytext, {
  trackedOrigins: new Set([42, CustomBinding])
})

// Not tracked (origin is null, not in set)
ytext.insert(0, 'abc')
undoManager.undo()  // no effect

// Tracked (origin 42 is in set)
doc.transact(() => { ytext.insert(0, 'abc') }, 42)
undoManager.undo()  // removes 'abc'

// Not tracked (origin 41 not in set)
doc.transact(() => { ytext.insert(0, 'xyz') }, 41)
undoManager.undo()  // no effect

// Tracked (instance of CustomBinding)
doc.transact(() => { ytext.insert(0, 'def') }, new CustomBinding())
undoManager.undo()  // removes 'def'
```

### Stack Events with Meta

Associate metadata (cursor position, scroll state) with undo/redo steps:

```js
undoManager.on('stack-item-added', (event) => {
  event.stackItem.meta.set('cursor', getRelativeCursor())
})

undoManager.on('stack-item-popped', (event) => {
  restoreCursor(event.stackItem.meta.get('cursor'))
})
```

**Available events:** `stack-item-added`, `stack-item-popped`, `stack-item-updated`. Each event provides `{ stackItem, origin, type: 'undo'|'redo', changedParentTypes }`.

---

## Y.RelativePosition

Stable positions that survive document edits. Regular integer indexes break when remote users edit the document. Relative positions stay attached to a specific element.

```js
// Create from an index position
const relPos = Y.createRelativePositionFromTypeIndex(ytext, 5)

// Convert back to absolute position
const absPos = Y.createAbsolutePositionFromRelativePosition(relPos, doc)
// => { type: ytext, index: 7, assoc: 0 } — index updated after remote edits
```

### API

- `Y.createRelativePositionFromTypeIndex(type, index, assoc?: number)` — Create relative position. `assoc >= 0` associates with character after index; `assoc < 0` associates with character before.
- `Y.createAbsolutePositionFromRelativePosition(relPos, doc)` — Resolve to `{ type, index, assoc }` or `null` if type was deleted.
- `Y.encodeRelativePosition(relPos): Uint8Array` — Binary encoding for network transport.
- `Y.decodeRelativePosition(Uint8Array): RelativePosition` — Decode binary.

### Encoding Options

```js
// JSON encoding (human-readable)
const json = JSON.stringify(relPos)
const decoded = JSON.parse(json)

// Binary encoding (compact, preferred for networks)
const binary = Y.encodeRelativePosition(relPos)
const decoded = Y.decodeRelativePosition(binary)
```

### Use Cases

- **Shared cursors**: Store cursor as relative position, resolve to absolute for rendering
- **Selections/ranges**: Two relative positions define a stable range
- **Comments/annotations**: Attach comments to text that survives edits
- **Bookmarks**: Persistent references to document locations

---

## Subdocuments

Embed `Y.Doc` instances inside shared types. Enables lazy loading of large documents within a folder structure.

```js
const rootDoc = new Y.Doc()
const folder = rootDoc.getMap()

// Create and embed a subdocument
const subDoc = new Y.Doc()
subDoc.getText().insert(0, 'content')
folder.set('document.txt', subDoc)
```

### Lazy Loading

Subdocuments are empty until explicitly loaded:

```js
// Client Two — content is initially empty
const subDoc = rootDoc.getMap().get('document.txt')
subDoc.getText().toString() // => ""

// Load on demand
subDoc.load()

// Providers fetch content from network/database
subDoc.on('synced', () => {
  subDoc.getText().toString() // => "content"
})
```

### Lifecycle

```js
subDoc.load()      // Start loading
// ... use the document ...
subDoc.destroy()   // Free memory, destroy bindings

// Access again creates a fresh reference
const reloaded = rootDoc.getMap().get('document.txt')
reloaded.load()
```

### GUID-Based Identity

Each subdocument has a unique GUID (UUIDv4 by default). Documents with the same GUID automatically sync:

```js
const doc = new Y.Doc()
console.log(doc.guid) // => "123e4567-e89b-12d3-a456-426614174000"

// Duplicate reference — same GUID = same document
const copy = new Y.Doc({ guid: doc.guid })
rootDoc.getMap().set('copy.txt', copy)
// doc and copy sync automatically
```

### Auto-Load Option

```js
const autoLoadedDoc = new Y.Doc({ autoLoad: true })
// All peers automatically load this document when discovered
```

### Subdocs Event

Providers listen to this event for lazy loading:

```js
doc.on('subdocs', ({ added, removed, loaded }) => {
  // added: new subdocuments in the tree
  // removed: destroyed subdocuments
  // loaded: subdocuments that called .load()

  loaded.forEach(subdoc => {
    // Create provider for this subdocument's room
    new WebrtcProvider(subdoc.guid, subdoc)
  })
})

// Get all current subdocuments
doc.getSubdocs() // Set<Y.Doc>
```

---

## Delta Format

Quill-inspired format for describing changes on sequence types (Y.Text, Y.Array, Y.XmlFragment). Used in `observe` events and `applyDelta`.

### Operations

| Operation | Meaning |
|-----------|---------|
| `{ insert: 'text' }` | Insert content |
| `{ delete: 3 }` | Delete 3 items |
| `{ retain: 2 }` | Skip past 2 items (can include formatting) |

### Text Delta (Y.Text)

```js
ytext.insert(0, '12345')
ytext.applyDelta([{ retain: 1 }, { delete: 3 }])
// Result: '15' — kept first char, deleted next 3

// Insert with formatting at specific position
ytext.applyDelta([
  { retain: 1 },
  { insert: 'abc', attributes: { bold: true } },
  { retain: 1 },
  { insert: 'xyz' }
])

// Format existing text via retain
ytext.applyDelta([{ retain: 5, attributes: { italic: true } }])
```

### Array Delta (Y.Array)

Insert values are arrays of elements:

```js
yarray.observe(event => console.log(event.changes.delta))

yarray.insert(0, [1, 2, 3])    // [{ insert: [1, 2, 3] }]
yarray.insert(2, ['abc'])      // [{ retain: 2 }, { insert: ['abc'] }]
yarray.delete(0, 1)            // [{ delete: 1 }]
```

### Transaction Batching

Multiple changes in one transaction produce a single combined delta:

```js
ydoc.transact(() => {
  yarray.insert(0, [1, 2, 3])
  yarray.insert(2, ['abc'])
  yarray.delete(0, 1)
}) // [{ insert: [2, 'abc', 3] }] — combined result
```

### toDelta()

Get current state as delta:

```js
ytext.insert(0, 'Hello ')
ytext.insert(6, 'World', { bold: true })
ytext.toDelta()
// => [{ insert: 'Hello ' }, { insert: 'World', attributes: { bold: true } }]
```

---

## Y.Event

Event objects passed to `observe` and `observeDeep` callbacks.

### Properties

- `event.target: Y.AbstractType` — The type that was modified.
- `event.currentTarget: Y.AbstractType` — The type the observer is attached to (for deep observation).
- `event.transaction: Y.Transaction` — The transaction containing this change.
- `event.path: Array<string | number>` — Path from Y.Doc root to the changed type.
- `event.changes.delta: Delta` — Changes in delta format (for sequence types).
- `event.changes.keys: Map<string, { action, oldValue }>` — Key/attribute changes (for Y.Map, Y.XmlElement).

### observe vs observeDeep

```js
// Fires only when this specific type changes
ymap.observe((event) => {
  // event.target === ymap
})

// Fires when this type OR any nested type changes
ymap.observeDeep((events) => {
  // events is Array<Y.Event>, each with its own target and path
  for (const event of events) {
    console.log(event.path) // Path to the actual changed type
  }
})
```

---

## Internals Overview

### CRDT Algorithm

Yjs implements an adaptation of the YATA CRDT with optimized runtime performance. Key properties:

- **State vectors** track what updates each client has seen, enabling efficient delta sync
- **Garbage collection** removes deleted content from memory; disabled with `doc.gc = false`
- **ClientID collision** can permanently corrupt a document — never reuse clientIDs across sessions

### Performance Considerations

- Bundle changes in transactions to minimize event overhead
- Use state vectors for delta sync instead of full state exchange
- Server-side `Y.mergeUpdates()` reduces stored data without loading documents
- Periodically load into Y.Doc for garbage collection if using server-side merging
- Awareness states are small and exchanged regularly (30s timeout)

### Visualization

CRDT algorithm visualization available at: https://text-crdt-compare.surge.sh/
