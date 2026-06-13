# Advanced Types

## Contents
- XML Types
- Typed Containers
- Snapshots
- UndoManager
- Text Formatting & Diff

## XML Types

pycrdt provides three XML shared types for structured document editing:

### XmlFragment

A container for XML nodes (similar to a DOM fragment). Can be a root type in `Doc`:

```python
from pycrdt import Doc, XmlFragment, XmlElement, XmlText

doc = Doc()
doc["xml"] = frag = XmlFragment()
```

### XmlElement

A tagged XML node with attributes and children:

```python
elem = XmlElement(
    tag="div",
    attributes={"class": "content"},
    contents=[XmlText("Hello"), XmlElement(tag="br")]
)
frag.children.append(elem)

# Access properties
print(elem.tag)                    # "div"
print(elem.attributes["class"])    # "content"
print(str(elem))                   # "<div class='content'>Hello<br/></div>"
```

### XmlText

A text node within XML (similar to `Text` but as a child of XmlElement/XmlFragment):

```python
text_node = XmlText("Hello World")
frag.children.append(text_node)
text_node += "!"
print(str(text_node))              # "Hello World!"
```

### Children view

`element.children` and `fragment.children` provide list-like access:

```python
# Iterate children
for child in frag.children:
    print(type(child).__name__, str(child))

# Insert at position
frag.children.insert(0, XmlElement(tag="p"))
frag.children.append(XmlText("footer"))

# Replace / delete
frag.children[0] = XmlElement(tag="h1")
del frag.children[0]
```

### Attributes view

`element.attributes` and `text_node.attributes` provide dict-like access:

```python
elem.attributes["id"] = "main"
del elem.attributes["class"]
print("data-x" in elem.attributes)   # membership test
for key, val in elem.attributes:      # iterate
    print(key, val)
```

### XML events

XML types support `observe_deep()` for change notifications:

```python
frag.observe_deep(lambda events: print(f"{len(events)} XML changes"))
```

`XmlEvent` carries: `children_changed`, `target`, `path`, `delta`, `keys`.

## Typed Containers

For static type hints, pycrdt provides typed wrappers that map Python class annotations to shared type keys.

### TypedDoc

```python
from pycrdt import Array, Doc, Map, Text, TypedDoc

class MyDoc(TypedDoc):
    title: Text
    tags: Array[str]
    config: Map[int]

doc = MyDoc()
doc.title += "My Document"
doc.tags.append("crdt")
doc.config["version"] = 2

# Access underlying untyped Doc
untyped: Doc = doc._
```

### TypedMap

Associates types with specific keys (not uniform values):

```python
from pycrdt import Array, Map, TypedMap

class UserMap(TypedMap):
    name: str
    active: bool
    scores: Array[int]

m = UserMap()
m.name = "Alice"
m.active = True
m.scores = Array([100, 200])

# Underlying Map
raw: Map = m._
```

### TypedArray

Uniform element type with typed indexing:

```python
from pycrdt import Array, TypedArray, TypedMap

class ItemMap(TypedMap):
    id: int
    label: str

class ItemList(TypedArray[ItemMap]):
    type: ItemMap

items = ItemList()
item = ItemMap()
item.id = 1
item.label = "First"
items.append(item)

print(items[0].label)    # "First" (typed access)
raw: Array = items._     # underlying Array
```

**Note:** Typed containers are not subclasses of their untyped counterparts. They wrap the underlying type and expose it via `._`.

## Snapshots

Capture a point-in-time view of a document's state, useful for versioning or historical queries:

```python
from pycrdt import Doc, Text, Snapshot

doc = Doc()
doc["text"] = Text("Hello")

# Create snapshot
snap = Snapshot.from_doc(doc)

# Serialize for storage
data = snap.encode()

# Restore from bytes
restored_snap = Snapshot.decode(data)

# Create a new Doc frozen at the snapshot state
frozen_doc = Doc.from_snapshot(restored_snap, doc)
```

Snapshots capture both the document state vector and the delete set, allowing you to reconstruct exactly what was visible at that point in time.

## UndoManager

Provides undo/redo on shared types with configurable scope and origin filtering:

```python
from pycrdt import Doc, Text, UndoManager

doc = Doc()
doc["text"] = text = Text("Hello")

# Track entire document
undo_mgr = UndoManager(doc=doc)

# Or track specific types only
undo_mgr = UndoManager(scopes=[text])
undo_mgr.expand_scope(doc["other_text"])  # add more later

# Use origins to separate user edits from auto-changes
with doc.transaction(origin="user"):
    text.insert(5, " World")

with doc.transaction(origin="auto-save"):
    pass

undo_mgr.exclude_origin("auto-save")  # don't undo auto-save changes

# Undo / redo
if undo_mgr.can_undo():
    undo_mgr.undo()
if undo_mgr.can_redo():
    undo_mgr.redo()
```

### Configuration

- `capture_timeout_millis` (default 500): groups changes within this time window into a single undo step
- `timestamp`: custom timestamp function (milliseconds since epoch)
- Pre-filled stacks: `UndoManager(undo_stack=[...], redo_stack=[...])`

### StackItem

Each undo/redo step is a `StackItem` containing insertions and deletions as `DeleteSet` objects, plus optional metadata:

```python
from pycrdt import StackItem, DeleteSet

# Access current stacks
for item in undo_mgr.undo_stack:
    print(item.deletions.encode(), item.insertions.encode(), item.meta)

# Merge two stack items
merged = StackItem.merge(
    item_a, item_b,
    merge_meta=lambda a, b: a or b
)
```

### Clear

```python
undo_mgr.clear()  # Reset all undo/redo history
```

## Text Formatting & Diff

`Text` supports rich text with formatting attributes and embedded objects.

### Insert with attributes

```python
doc["text"] = text = Text("Hello World")
text.insert(5, ",", attrs={"bold": True})
text.insert(6, " ", attrs={"italic": True, "color": "blue"})
```

### Format existing range

```python
text.format(0, 5, {"bold": True, "underline": True})
# Characters at indices 0-4 now have bold+underline attributes
```

### Diff (formatted output)

```python
chunks = text.diff()
# Returns list of (content, attrs | None) tuples:
# [("Hello", {"bold": True}), (", ", None), ("World", {"italic": True})]
```

Each chunk contains the content (string or embedded object) and its formatting attributes dict, or `None` for unformatted segments.

### Embeds

Insert non-text objects at a position:

```python
text.insert_embed(0, {"image": "photo.png"}, attrs={"width": 200})
```

Embeds appear in `diff()` output alongside text chunks and can carry attributes.
