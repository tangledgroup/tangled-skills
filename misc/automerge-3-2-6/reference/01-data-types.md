# Data Types

## Contents
- Simple Values and Maps
- Lists
- Text
- Rich Text (Marks and Blocks)
- Counters
- Conflicts

## Simple Values and Maps

All JSON primitives are supported. JavaScript `Date` objects map to Automerge timestamps. Binary data uses byte arrays.

**Supported scalar types:**

| Automerge type | JavaScript type | Notes |
|---|---|---|
| Number | `number` | IEEE 754 64-bit float |
| Int | `Int` wrapper | Signed integer, use `new Automerge.Int(n)` |
| Uint | `Uint` wrapper | Unsigned integer, use `new Automerge.Uint(n)` |
| Float64 | `Float64` wrapper | Explicit float, use `new Automerge.Float64(n)` |
| Boolean | `boolean` | — |
| String | `string` | Unicode (UTF-16 in JS) |
| Timestamp | `Date` | Stored as milliseconds since epoch |
| Byte array | `Uint8Array` | Binary data |
| null | `null` | Explicit null values |

**Maps** are the root structure. Every Automerge document is a root map with string keys (UTF-8 internally, exposed as UTF-16 in JavaScript) mapping to any Automerge value, including nested maps and lists.

```javascript
let doc = Automerge.change(Automerge.init(), (d) => {
  d.name = "Alice"              // string
  d.age = new Automerge.Int(30) // explicit int
  d.score = new Automerge.Float64(3.14)
  d.active = true               // boolean
  d.created = new Date()        // timestamp
  d.profile = {                 // nested map
    bio: "Developer",
    tags: ["rust", "js"]
  }
})
```

**Important:** Always read from `currentDoc`, never modify it directly. Only mutate `doc` inside the `Automerge.change()` callback.

## Lists

JavaScript arrays are fully supported with CRDT-backed operations. Underlying data structure is an RGA (Replicated Growable Array) sequence, which preserves user intent during concurrent insertions and deletions.

**Supported operations inside `change()`:**

```javascript
let doc = Automerge.change(Automerge.init(), (d) => {
  d.items = ["a", "b", "c"]
})

doc = Automerge.change(doc, (d) => {
  d.items.push("d")           // append
  d.items.unshift("x")        // prepend
  d.items.insertAt(1, "new")  // insert at index
  d.items.deleteAt(0)         // remove at index
  d.items.splice(1, 2, "r")   // splice (start, deleteCount, ...items)
})

// Nested objects in lists
doc = Automerge.change(doc, (d) => {
  d.tasks.push({ title: "Task", done: false })
  d.tasks[0].done = true      // modify nested property
})
```

Concurrent insertions at the same position are deterministically ordered across all peers. Concurrent deletions of the same element merge without loss.

## Text

All strings in Automerge are collaborative text objects under the hood. For simple string values, concurrent edits merge correctly automatically.

For **explicit collaborative text editing**, use `Automerge.splice()` or `Automerge.updateText()`:

```javascript
let doc = Automerge.from({ text: "Hello" })

// Insert " World" at position 5
doc = Automerge.change(doc, (d) => {
  Automerge.splice(d, "text", 5, 0, " World")
})

// Replace characters 0-4 with "Hi"
doc = Automerge.change(doc, (d) => {
  Automerge.splice(d, "text", 0, 5, "Hi")
})

// Or use updateText to replace the whole string
doc = Automerge.change(doc, (d) => {
  Automerge.updateText(d, "text", "Completely new text")
})
```

**`splice(doc, prop, start, deleteCount, insert?)`** — Insert and/or delete characters at a position. Returns array of deleted characters.

Concurrent text edits merge correctly: if two users type at different positions simultaneously, both edits are preserved in the same order on all peers.

## Rich Text (Marks and Blocks)

Rich text extends plain text with two annotation types: **marks** (formatting spans) and **blocks** (structural divisions).

### Marks

Marks represent formatting that applies to a range of characters and can overlap. Each mark has a name, a value (primitive), and an expansion behavior.

```javascript
let doc = Automerge.from({ text: "Hello World" })

// Apply bold mark to "Hello"
doc = Automerge.change(doc, (d) => {
  Automerge.mark(d, "text", 0, 5, "bold", true, { expand: "right" })
})

// Apply italic mark to "World"
doc = Automerge.change(doc, (d) => {
  Automerge.mark(d, "text", 6, 11, "italic", true, { expand: "none" })
})

// Read active marks at a position
let marksAt3 = Automerge.marks(d, "text", 3, 3)
// [{ name: "bold", value: true, start: 0, end: 5 }]

// Remove a mark
doc = Automerge.change(doc, (d) => {
  Automerge.unmark(d, "text", 0, 5, "bold")
})
```

**Expansion options:**
- `expand: "right"` — mark expands when characters inserted at right boundary (typical for bold/italic)
- `expand: "left"` — mark expands when characters inserted at left boundary
- `expand: "none"` — mark does not expand (typical for hyperlinks)

### Blocks

Blocks divide text into structural units (paragraphs, headers, etc.). Each block has a type and optional properties.

```javascript
let doc = Automerge.from({ text: "Hello\nWorld" })

// Create a block
doc = Automerge.change(doc, (d) => {
  Automerge.block(d, "text", 0, 5, "heading", { level: 1 })
})

// Split a block at a position
doc = Automerge.change(doc, (d) => {
  Automerge.splitBlock(d, "text", 3)
})

// Join adjacent blocks
doc = Automerge.change(doc, (d) => {
  Automerge.joinBlock(d, "text", 5)
})

// Update block properties
doc = Automerge.change(doc, (d) => {
  Automerge.updateBlock(d, "text", 0, { level: 2 })
})
```

## Counters

Use `Automerge.Counter` for numeric values that are only changed by adding or subtracting. Counters merge additively, so concurrent increments sum correctly.

```javascript
let doc = Automerge.from({ upvotes: new Automerge.Counter(0) })

// Increment
doc = Automerge.change(doc, (d) => {
  d.upvotes.inc(1)
})

// Decrement
doc = Automerge.change(doc, (d) => {
  d.upvotes.inc(-1)
})

// Check type
Automerge.isCounter(doc.upvotes) // true
```

**Why Counter over plain number?** If two users concurrently increment a value of 3, both would set it to 4 with a plain number (conflict → one wins). With Counter, the result is correctly 5 (3 + 1 + 1).

## Conflicts

Automerge cannot automatically resolve one case: **concurrent updates to the same property in the same object** (or same index in the same list). It picks a deterministic "winner" (same on all peers) and tracks the losing values as conflicts.

```javascript
let doc1 = Automerge.change(Automerge.init(), (d) => { d.name = "Alice" })
let doc2 = Automerge.change(Automerge.init(), (d) => { d.name = "Bob" })

let merged = Automerge.merge(doc1, doc2)
console.log(merged.name)           // "Alice" or "Bob" (deterministic)
console.log(Automerge.getConflicts(merged, "name"))
// { "<actor1>": "Alice", "<actor2>": "Bob" }
```

Conflicts are rare in practice because most concurrent edits touch different properties. Use `Automerge.getConflicts(doc, prop?)` to inspect — returns `{ actorId: value }` map or empty object if no conflicts.
