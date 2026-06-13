# Under the Hood

## Contents
- Merge Rules
- Storage Format
- Rich Text Schema
- Library Initialization (WASM)

## Merge Rules

Automerge merges concurrent changes automatically. The merge strategy depends on the data type and operation.

### Map Properties

- **Different properties:** Combined without conflict. If user A sets `name` and user B sets `age`, both values appear in the merged result.
- **Same property (scalars):** Last-writer-wins by causal ordering. The value from the change that is causally later wins. If truly concurrent (neither sees the other), a deterministic tiebreaker selects the winner. Losers are tracked as conflicts.
- **Same property (Counters):** Values are added together. Concurrent increments sum correctly.

### Lists

- **Insertions:** All insertions are preserved. Concurrent inserts at the same position are deterministically ordered using actor IDs.
- **Deletions:** All deletions are preserved. Deleting the same item concurrently merges without issue.
- **Insert + delete at same position:** Both operations survive — the inserted item appears, and the deleted item is removed. The RGA algorithm ensures consistent ordering.

### Text

- Uses the peritext CRDT. Concurrent character insertions and deletions merge correctly, preserving all user intent.
- Character-level operations are attributed to actors, enabling deterministic ordering of concurrent edits at the same position.

### Rich Text Marks

- Marks from different actors at overlapping ranges coexist. Each mark is independently tracked.
- Mark expansion behavior (`expand: "right"`, `"left"`, `"none"`) determines how marks interact with text insertions at boundaries.

### Document Merge

`Automerge.merge(doc1, doc2)` combines all changes from both documents. The result contains every change that happened in either document, merged according to the rules above.

## Storage Format

Automerge uses a compressed binary format for persistence and transfer.

### save() — Full Document

```javascript
let data = Automerge.save(doc)
// Returns Uint8Array with complete document state
```

Includes all changes in the document's history. Suitable for backup or transfer to a peer that has nothing.

### saveIncremental() — Changes Since Last Save

```javascript
let heads = Automerge.getHeads(doc)
let incremental = Automerge.saveIncremental(doc, heads)
// Returns only changes not covered by the given heads
```

Efficient for periodic saves — only writes what changed since the last save point.

### saveSince() — Changes Since Specific Heads

```javascript
let bundle = Automerge.saveSince(doc, oldHeads)
// All changes after oldHeads
```

Used to send only new changes to a peer that already has an older version.

### saveBundle() — Full State Transfer

```javascript
let bundle = Automerge.saveBundle(doc, oldHeads)
// Complete document state for transfer
```

Unlike `saveSince`, this includes enough information for the recipient to reconstruct the full document. Use when sending a document to a peer that may have partial or no history.

### load() and loadIncremental()

```javascript
// Load complete document
let doc = Automerge.load(data)

// Incremental loading (for large documents)
let [doc, moreData] = await Automerge.loadIncremental(doc, chunk)
// moreData === true means call loadIncremental again with next chunk
```

### Memory Efficiency

Automerge 3 significantly reduces memory usage compared to version 2 through:
- Compressed storage of counter values
- Deduplicated string storage
- Efficient mark representation
- Incremental materialization (only compute current state when reading)

## Rich Text Schema

The rich text API provides two primitives for annotating text: marks and blocks.

### Mark Model

A mark is a named annotation over a character range. Multiple marks can overlap on the same range.

```
Text:  "Hello World"
Mark1: [=====]         bold = true  (chars 0-5)
Mark2:         [=====] italic = true (chars 6-11)
```

**Mark expansion:** When text is inserted at a mark's boundary, the `expand` option controls behavior:

- `expand: "right"` — inserting at the right edge extends the mark (bold text expands as you type)
- `expand: "left"` — inserting at the left edge extends the mark
- `expand: "none"` — mark boundaries stay fixed (hyperlinks don't expand)

### Block Model

Blocks partition text into segments. Each block has a type and optional properties. Blocks cannot overlap but can be nested in the sense that marks span across blocks.

```
Text:  "# Title\n\nBody paragraph"
Block1: [=======]      heading, level: 1
Block2: [==============] paragraph
```

### marksAt()

Get all active marks at a specific position or range:

```javascript
let marks = Automerge.marksAt(doc, "text", position)
// Returns array of { name, value, start, end } for marks covering the position
```

## Library Initialization (WASM)

Automerge is implemented in Rust and compiled to WebAssembly. Loading behavior varies by environment.

### Node.js

No special configuration needed:

```javascript
import * as Automerge from "@automerge/automerge"
// WASM loads automatically
```

### Webpack

Enable async WebAssembly in `webpack.config.js`:

```javascript
{
  experiments: {
    asyncWebAssembly: true
  }
}
```

### Vite

Add the required plugins for WASM support. Most modern Vite setups handle this automatically.

### Escape Hatch — Manual WASM Loading

If automatic loading fails in your environment, load WASM manually:

```javascript
import * as Automerge from "@automerge/automerge"
import wasmBase64 from "@automerge/automerge/wasm/automerge_wasm_bg.wasm?base64"

await Automerge.initializeBase64Wasm(wasmBase64)

// Now safe to use Automerge
let doc = Automerge.init()
```

### Checking WASM Status

```javascript
Automerge.isWasmInitialized() // true/false
Automerge.wasmInitialized     // Promise that resolves when WASM is ready
```

Always await `Automerge.wasmInitialized` before using the library in environments where WASM loading is asynchronous.
