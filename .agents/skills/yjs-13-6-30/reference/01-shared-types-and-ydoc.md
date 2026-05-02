# Shared Types and Y.Doc

## Contents
- Y.Doc
- Y.Map
- Y.Array
- Y.Text
- Y.XmlFragment
- Y.XmlElement
- Y.XmlText
- Common Patterns

---

## Y.Doc

The document root. All shared types live inside a `Y.Doc`.

```js
import * as Y from 'yjs'

const doc = new Y.Doc()
// Optional: specify GUID for subdocument identity
const docWithGuid = new Y.Doc({ guid: 'my-unique-id', autoLoad: true })
```

### Properties

- `doc.clientID: number` (readonly) — Unique per-session identifier. Do not reuse across sessions; use Awareness for user identity instead.
- `doc.gc: boolean` — Garbage collection flag. Set `doc.gc = false` to disable GC and retain old content for restoration.
- `doc.guid: string | null` — Optional UUIDv4 that identifies the document (used by providers as room name).

### Methods

- `doc.transact(fn: (tr: Transaction) => void, origin?: any)` — Execute changes in a transaction. Bundle related changes to fire one combined event. The optional `origin` is stored on `transaction.origin` and available in `update` events for filtering.
- `doc.get(name: string, TypeClass: Y.TypeClass): Y.Type` — Get or create a top-level shared type by name and class.
- `doc.getMap(name?: string): Y.Map` — Shortcut for `doc.get(name, Y.Map)`.
- `doc.getArray(name?: string): Y.Array` — Shortcut for `doc.get(name, Y.Array)`.
- `doc.getText(name?: string): Y.Text` — Shortcut for `doc.get(name, Y.Text)`.
- `doc.getXmlFragment(name?: string): Y.XmlFragment` — Shortcut for `doc.get(name, Y.XmlFragment)`.
- `doc.destroy()` — Destroy the document. Clears all event handlers and frees memory (unless types are still referenced). Attached bindings and providers are also destroyed.
- `doc.getSubdocs(): Set<Y.Doc>` — Get all subdocuments embedded in this document.

### Event Handlers

```js
doc.on(eventName, handler)
doc.once(eventName, handler)
doc.off(eventName, handler)
```

**Available events:**

| Event | Signature | Fires When |
|-------|-----------|------------|
| `beforeTransaction` | `(tr: Transaction, doc: Y.Doc)` | Right before every transaction |
| `beforeObserverCalls` | `(tr: Transaction, doc: Y.Doc)` | Before observers on shared types are called |
| `afterTransaction` | `(tr: Transaction, doc: Y.Doc)` | Right after every transaction |
| `update` | `(update: Uint8Array, origin: any, doc: Y.Doc, tr: Transaction)` | Document state changed — send this update to other clients |
| `subdocs` | `({ loaded, added, removed }: Set<Y.Doc>)` | Subdocuments added/removed/loaded |
| `destroy` | `(doc: Y.Doc)` | Just before document is destroyed |

**Event ordering per transaction:**

1. `beforeTransaction`
2. Transaction executes
3. `beforeObserverCalls`
4. `ytype.observe()` callbacks
5. `ytype.observeDeep()` callbacks
6. `afterTransaction`
7. `update`

---

## Y.Map

A shared key-value store with API matching `global.Map`.

```js
const ymap = doc.getMap('settings')
// or create as nested type
const nestedMap = new Y.Map()
ymap.set('nested', nestedMap)
```

### Methods

- `ymap.set(key: string, value: any)` — Add or update. Value can be JSON-encodable, `Uint8Array`, or another shared type.
- `ymap.get(key: string): any` — Retrieve by key.
- `ymap.delete(key: string)` — Remove entry.
- `ymap.has(key: string): boolean` — Check existence.
- `ymap.clear()` — Remove all entries.
- `ymap.toJSON(): Object` — Copy to plain object, transforming shared types recursively.
- `ymap.size: number` — Entry count.
- `ymap.forEach((value, key, map) => void)` — Iterate entries.
- `ymap.entries() / values() / keys()` — Iterators (supports `for..of`).
- `ymap.clone(): Y.Map` — Clone into a fresh unbound Y.Map.

### Properties

- `ymap.doc: Y.Doc | null` — Parent document (null if not bound).
- `ymap.parent: Y.AbstractType | null` — Containing type (null if top-level).

### Observing Changes

```js
ymap.observe((event) => {
  // Keys that changed
  event.keysChanged          // Set<string>

  // Detailed diff
  event.changes.keys.forEach((change, key) => {
    // change.action: 'add' | 'update' | 'delete'
    // change.oldValue: previous value (undefined for 'add')
  })
})

// Deep observe — also fires when nested types change
ymap.observeDeep((events) => { /* events is Array<Y.Event> */ })

ymap.unobserve(handler)
ymap.unobserveDeep(handler)
```

---

## Y.Array

A shared ordered sequence with API matching `global.Array`.

```js
const yarray = doc.getArray('items')
// or nested
const nestedArray = new Y.Array()
yarray.insert(0, [nestedArray])
```

### Methods

- `Y.Array.from(Array<any>): Y.Array` — Factory from existing content.
- `yarray.length: number` — Element count.
- `yarray.insert(index: number, content: Array<any>)` — Insert at position. Content is always an array (performance optimization).
- `yarray.delete(index: number, length: number)` — Delete range.
- `yarray.push(content: Array<any>)` — Append to end (same as `insert(length, content)`).
- `yarray.unshift(content: Array<any>)` — Prepend (same as `insert(0, content)`).
- `yarray.get(index: number): any` — Retrieve by index.
- `yarray.slice([start], [end]): Array<any>` — Range extract (supports negative indexes).
- `yarray.toArray(): Array<any>` — Copy to plain array.
- `yarray.toJSON(): Array<any>` — Copy with shared types transformed to JSON.
- `yarray.forEach((value, index, yarray) => void)` — Iterate.
- `yarray.map(fn): Array<T>` — Transform each element.
- `yarray.clone(): Y.Array` — Clone into fresh unbound Y.Array.

### Observing Changes

```js
yarray.observe((event) => {
  // Delta format describing insertions/deletions
  console.log(event.changes.delta)
})

yarray.insert(0, [1, 2, 3])   // [{ insert: [1, 2, 3] }]
yarray.delete(2, 1)            // [{ retain: 2 }, { delete: 1 }]
```

---

## Y.Text

Shared text with rich formatting support.

```js
const ytext = doc.getText('content')
// or nested
const nestedText = new Y.Text('initial content')
```

### Methods

- `ytext.length: number` (readonly) — String length in UTF-16 code units.
- `ytext.insert(index: number, content: string, format?: Object)` — Insert text with optional formatting attributes.
- `ytext.format(index: number, length: number, format: Object)` — Apply formatting to a range.
- `ytext.applyDelta(delta: Delta)` — Apply a Text-Delta for complex operations.
- `ytext.delete(index: number, length: number)` — Delete characters.
- `ytext.toString(): string` — Plain text (no formatting).
- `ytext.toDelta(): Delta` — Full representation with formatting as Quill-style delta.
- `ytext.toJSON(): string` — Same as `toString()`.
- `ytext.clone(): Y.Text` — Clone into fresh unbound Y.Text.

### Formatting Example

```js
ytext.insert(0, 'Hello ')
ytext.insert(6, 'World', { bold: true })
ytext.toDelta()
// => [{ insert: 'Hello ' }, { insert: 'World', attributes: { bold: true } }]

// Format existing range
ytext.format(0, 5, { italic: true })
```

---

## Y.XmlFragment

A container for XML nodes (Y.XmlElement and Y.XmlText). Similar to `DocumentFragment` in DOM.

```js
const yxml = doc.getXmlFragment('document')
yxml.insert(0, [new Y.XmlElement('p'), new Y.XmlText()])
```

### Methods

- `yxml.length: number` — Child count.
- `yxml.firstChild: Y.XmlElement | Y.XmlText | null` — First child.
- `yxml.insert(index, content: Array<Y.XmlElement | Y.XmlText>)` — Insert children.
- `yxml.insertAfter(ref, content)` — Insert after reference node (null = beginning).
- `yxml.delete(index, length)` — Delete children.
- `yxml.push(content) / yxml.unshift(content)` — Append/prepend.
- `yxml.get(index)` — Retrieve child.
- `yxml.slice([start], [end])` — Range extract (negative indexes supported).
- `yxml.toJSON(): string` — Concatenated XML string (may not be valid XML without wrapper).
- `yxml.toDOM(): DocumentFragment` — Convert to real DOM nodes.
- `yxml.createTreeWalker(filter: fn): Iterable` — Walk all descendants matching filter.
- `yxml.clone(): Y.XmlFragment` — Clone into fresh unbound instance.

### Tree Walker

```js
for (const paragraph of yxml.createTreeWalker(node => node.nodeName === 'p')) {
  // process each <p> element
}
```

---

## Y.XmlElement

An XML element with a name, attributes, and children. Inherits from Y.XmlFragment.

```js
const el = new Y.XmlElement('div')
el.setAttribute('class', 'container')
el.insert(0, [new Y.XmlText()])
```

### Properties and Methods

- `el.nodeName: string` — Element name.
- `el.prevSibling / el.nextSibling` — Adjacent siblings.
- `el.setAttribute(name, value: string | Y.AbstractType)` — Set attribute.
- `el.removeAttribute(name)` — Remove attribute.
- `el.getAttribute(name): string | Y.AbstractType` — Get attribute.
- `el.getAttributes(): Object` — All attributes as object.
- `el.toString(): string` — XML string representation.

Inherits all Y.XmlFragment methods (insert, delete, get, etc.) for managing children.

### Observing Changes

```js
el.observe((event) => {
  // Child changes via delta
  event.changes.delta

  // Attribute changes (same format as Y.Map)
  event.changes.keys.forEach((change, attrName) => {
    // change.action: 'add' | 'update' | 'delete'
  })
})
```

---

## Y.XmlText

Text node inside XML. Extends Y.Text with sibling navigation.

```js
const text = new Y.XmlText()
text.insert(0, 'Hello', { bold: true })
text.toString() // => '<bold>Hello</bold>'
```

### Additional Properties (beyond Y.Text)

- `text.prevSibling / text.nextSibling` — Adjacent siblings.
- `text.toString()` — Returns XML string with formatting as tags. Object-valued attributes become element attributes:

```js
text.insert(0, 'link', { a: { href: 'https://example.com' } })
text.toString() // => '<a href="https://example.com">link</a>'
```

---

## Common Patterns

### Nesting Shared Types

Shared types can be nested inside each other. A type must exist only once in the document — reassigning throws:

```js
const ymap = doc.getMap('root')
const foodArray = new Y.Array()
foodArray.insert(0, ['apple', 'banana'])
ymap.set('food', foodArray)

ymap.set('fruit', foodArray) // Error! Already defined
```

### Top-Level vs Nested Definition

```js
// Top-level: registered by name on the document
const ymap = doc.getMap('settings')

// Nested: created standalone, then inserted into another type
const nested = new Y.Map()
ymap.set('nested', nested)
// Now `nested.doc` points to the parent document
```

### Type Uniqueness Constraint

Each shared type instance can exist at only one position in the document tree. This is enforced — attempting to insert the same instance twice throws an error. Clone with `.clone()` if you need a copy.
