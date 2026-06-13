# Advanced Features

## Contents
- Ephemeral Data
- Deep References
- Cursors and Text Positions
- Blocks in Rich Text

## Ephemeral Data

Ephemeral data is state that shouldn't be persisted — it changes too fast or is only useful during a live session. Examples: cursor positions, user presence, selection ranges.

Ephemeral data is associated with a document (via its DocHandle), so peers exchange it alongside document sync.

```javascript
// Send ephemeral data
docHandle.sendEphemeralMessage({
  type: "cursor",
  position: { line: 5, column: 12 },
  userId: "alice"
})

// Receive ephemeral data
docHandle.onEphemeralMessage((message, peerId) => {
  switch (message.type) {
    case "cursor":
      updateCursor(message.position, message.userId)
      break
    case "presence":
      updateUserPresence(peerId, message.online)
      break
  }
})
```

Ephemeral messages are not stored or replayed. They're fire-and-forget — if a peer is offline, the message is lost. Use them for real-time presence, cursors, selections, and typing indicators.

If you need ephemeral data with no associated document, create a blank document and use it as the communication channel.

## Deep References

Deep references let you maintain stable pointers to specific parts of a document, even as the document changes around them. Useful for comments, annotations, or deep links.

### getObjectId

Get a stable identifier for any value in the document:

```javascript
let doc = Automerge.from({
  tasks: [
    { title: "Task 1", notes: "Important" },
    { title: "Task 2" }
  ]
})

// Get object ID for a nested value
let taskId = Automerge.getObjectId(doc, "tasks.0")
// Returns an ObjID that persists across changes to other parts of the document

// Get the root object ID
let rootId = Automerge.getObjectId(doc, "")
```

Object IDs remain stable even when items are inserted or deleted elsewhere in the document. They identify the CRDT object itself, not its position.

### Ref Class

The `Ref` class provides deep-linking to specific document paths:

```javascript
import { Ref } from "@automerge/automerge"

// Create a reference to a specific path
let ref = new Ref(doc, ["tasks", 0, "title"])

// Get the value at the reference
let value = ref.value(doc) // "Task 1"

// The ref stays valid even if items are inserted before index 0
// (use object IDs for truly stable references across reordering)
```

Use deep references when:
- Building comment systems that attach to specific document locations
- Creating shareable links to parts of a document
- Maintaining external metadata indexed by document structure

## Cursors and Text Positions

Cursors provide stable text positions that don't shift when content is inserted or deleted nearby. Unlike integer indices, cursors survive concurrent edits.

```javascript
let doc = Automerge.from({ text: "Hello World" })

// Create a cursor at position 5 (between "Hello" and "World")
let cursor = Automerge.getCursor(doc, "text", 5)

// Later, after other edits, find where the cursor now points
let position = Automerge.getCursorPosition(doc, "text", cursor)
console.log(position) // May differ from 5 if content was inserted before it

// Insert text at a cursor position
doc = Automerge.change(doc, (d) => {
  Automerge.splice(d, "text", cursor, 0, " Beautiful ", "after")
})
```

**`getCursor(doc, prop, position)`** — Create a cursor string at the given integer position.

**`getCursorPosition(doc, prop, cursor)`** — Resolve a cursor back to an integer position in the current document.

**Insert at cursor with `splice`:** Pass the cursor as the start position and use `"before"` or `"after"` as the fourth argument to control placement relative to the cursor:

```javascript
Automerge.splice(doc, "text", cursor, 0, "inserted text", "before")
Automerge.splice(doc, "text", cursor, 0, "inserted text", "after")
```

Cursors are essential for collaborative editors where multiple users maintain selections and insertions must respect each other's positions.

## Blocks in Rich Text

Blocks divide text into structural units (paragraphs, headings, lists). They complement marks (inline formatting) by providing document structure.

### Creating and Managing Blocks

```javascript
let doc = Automerge.from({ text: "Hello World" })

// Mark a range as a heading block
doc = Automerge.change(doc, (d) => {
  Automerge.block(d, "text", 0, 5, "heading", { level: 1 })
})

// Get blocks
let blocks = Automerge.blocks(doc, "text")
// [{ type: "heading", props: { level: 1 }, start: 0, end: 5 }]
```

### Splitting and Joining

```javascript
// Split a block at a position (creates two blocks)
doc = Automerge.change(doc, (d) => {
  Automerge.splitBlock(d, "text", 3)
})

// Join two adjacent blocks
doc = Automerge.change(doc, (d) => {
  Automerge.joinBlock(d, "text", 5)
})
```

### Block Properties

Update block metadata without changing text content:

```javascript
doc = Automerge.change(doc, (d) => {
  // Change heading level
  Automerge.updateBlock(d, "text", 0, { level: 2 })

  // Add custom properties
  Automerge.updateBlock(d, "text", 10, { align: "center" })
})
```

### Block Types

Common block types (define your own schema):

| Type | Use Case | Typical Properties |
|------|----------|-------------------|
| `heading` | Section headings | `level: 1-6` |
| `paragraph` | Body text | — |
| `blockquote` | Quoted content | `cite?` |
| `code` | Code blocks | `language?` |
| `list-item` | List items | `checked?` (for todo lists) |
| `divider` | Horizontal rule | — |

Blocks and marks work together: a heading block can contain bold/italic text via marks. Use blocks for structure, marks for inline formatting.
