# Changes and Patches

## Contents
- Change Model
- Patch Callbacks
- History and Diffing

## Change Model

Every modification to an Automerge document goes through `Automerge.change()`, which returns a new immutable document. The original is never mutated.

```javascript
let doc1 = Automerge.init()

let doc2 = Automerge.change(doc1, (doc) => {
  doc.title = "My Document"
})

// doc1 is unchanged, doc2 has the new value
doc1.title // undefined
doc2.title // "My Document"
```

**Change options:**

```javascript
let doc = Automerge.change(currentDoc, (doc) => {
  doc.updated = true
}, {
  message: "Update flag",      // human-readable change message
  time: Date.now(),             // timestamp (defaults to current time)
  marks: "preserve" | "clear"   // mark behavior for rich text
})
```

**Actor ID:** Each document has an actor identifier (random by default). Set it explicitly for multi-device apps where the same user needs consistent attribution:

```javascript
let doc = Automerge.init({ actor: "device-abc-123" })
Automerge.getActorId(doc) // "device-abc-123"
```

**Merge:** Combine two documents that diverged from a common ancestor. Returns a new document with all changes from both sides.

```javascript
let base = Automerge.from({ count: 0, name: "test" })

let branch1 = Automerge.change(base, (d) => { d.count = 1 })
let branch2 = Automerge.change(base, (d) => { d.name = "renamed" })

let merged = Automerge.merge(branch1, branch2)
// { count: 1, name: "renamed" }
```

**Clone:** Create an independent copy that shares no history.

```javascript
let clone = Automerge.clone(doc)
```

## Patch Callbacks

Pass a callback as the third argument to `change()` to receive a description of what changed. Patches are lightweight and can be sent to peers who don't need the full document.

**Patch types:**

| Type | Description | Fields |
|------|-------------|--------|
| `put` | Property set or updated | `path`, `value`, `action` ("updated" \| "added") |
| `del` | Property or list item deleted | `path`, `value`, `length?` |
| `insert` | Items inserted into list | `path`, `value`, `index` |
| `inc` | Counter incremented | `path`, `value`, `diff` |
| `spliceText` | Text content changed | `path`, `value`, `start`, `deleteCount`, `data` |

```javascript
let [doc, patches] = Automerge.change(doc, (d) => {
  d.tasks.push({ title: "New task", done: false })
  d.count += 1
}, (patch, doc) => {
  // Called for each change
  console.log(patch)
})

// Patches array:
// [
//   { action: "insert", index: 0, path: ["tasks"], value: [{title:"New task",done:false}] },
//   { action: "updated", name: "count", path: [], value: 1 }
// ]
```

**Apply patches to another document:**

```javascript
let [otherDoc, success] = Automerge.applyPatch(otherDoc, patches)
```

Patches are useful for:
- Sending minimal updates to UI subscribers
- Debugging what changed
- Syncing to peers without full document transfer

## History and Diffing

Automerge documents carry their complete history. Use these APIs to inspect changes, compare versions, and create branches.

### Getting Changes

```javascript
// All changes in a document
let allChanges = Automerge.getAllChanges(doc)

// Changes since a specific version (given by heads)
let heads = Automerge.getHeads(baseDoc)
let newChanges = Automerge.getChanges(doc, heads)

// Changes with metadata
let metaChanges = Automerge.getChangesMetaSince(doc, heads)
```

### Heads

Heads are the set of change hashes that represent the current tip(s) of a document's history. Use heads to track what you've already seen.

```javascript
let heads = Automerge.getHeads(doc)
// Array of change hashes

// Check if a document has specific heads
Automerge.hasHeads(doc, heads) // true/false
```

### Diffing

Compare two versions of a document to get patches describing the difference:

```javascript
let patches = Automerge.diff(oldDoc, newDoc)
// Array of patch objects

// Diff along a specific path (more efficient for deep documents)
let patches = Automerge.diffPath(oldDoc, newDoc, ["tasks", 0, "title"])
```

### Historical Views

View a document as it existed at a previous point:

```javascript
// Get the document state at a specific change
let heads = Automerge.getHeads(doc)
let historicalDoc = Automerge.view(doc, [heads[0]])
```

### Change Inspection

```javascript
let changes = Automerge.getAllChanges(doc)
for (let change of changes) {
  let inspected = Automerge.inspectChange(change)
  console.log(inspected.message)    // change message
  console.log(inspected.time)       // timestamp
  console.log(inspected.actor)      // actor ID
  console.log(inspected.sequenceNo) // nth change from this actor
}
```

### Branching and Forking

Create a branch from a specific point in history:

```javascript
// Fork from current heads
let fork = Automerge.init({
  actor: "new-actor",
  awaitWrite: false
})
fork = Automerge.merge(fork, doc)

// Or load from saved state at specific heads
let snapshot = Automerge.saveSince(doc, oldHeads)
let branch = Automerge.load(snapshot)
```

### Empty Changes

Generate a change with no modifications (useful for heartbeat or presence):

```javascript
let [doc, patches] = Automerge.emptyChange(doc, {
  message: "heartbeat",
  time: Date.now()
})
```
