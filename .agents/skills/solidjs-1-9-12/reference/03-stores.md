# Stores

## createStore

`createStore` creates a reactive store and setter for structured state.
Unlike signals, stores provide fine-grained property-level reactivity through
JavaScript Proxies — only the specific properties that change trigger updates.

```tsx
import { createStore } from "solid-js/store";

const [store, setStore] = createStore({
  userCount: 3,
  users: [
    { id: 0, username: "alice", loggedIn: false },
    { id: 1, username: "bob", loggedIn: true },
  ],
});

// Access properties directly (no function call needed)
console.log(store.users[0].username); // "alice"
```

### Key Differences from Signals

| Aspect | Signal | Store |
|--------|--------|-------|
| Access | `count()` (function call) | `store.user.name` (direct property) |
| Granularity | Whole value | Per-property |
| Best for | Primitives, simple objects | Nested objects, arrays |

## Modifying Stores

### Path Syntax

The setter uses path syntax: first arguments navigate to the target, last
argument is the new value.

```tsx
// Set a top-level property
setStore("userCount", 5);

// Set a nested property
setStore("users", 0, "loggedIn", true);

// Update with a function
setStore("users", 0, "username", prev => prev.toUpperCase());
```

### Shallow Merge for Objects

When setting an object value, it is shallow-merged with the existing value:

```tsx
setStore("users", 0, { id: 109 });
// Equivalent to: setStore("users", 0, user => ({ ...user, id: 109 }));
```

### Array Operations

**Append using path syntax** (more efficient — only new index triggers reactivity):

```tsx
setStore("users", store.users.length, {
  id: 3,
  username: "charlie",
  loggedIn: false,
});
```

**Modify multiple elements at once**:

```tsx
// Specific indices
setStore("users", [2, 7, 10], "loggedIn", false);

// Range with from/to (both inclusive)
setStore("users", { from: 1, to: store.users.length - 1 }, "loggedIn", false);

// Range with step
setStore("users", { from: 0, to: store.users.length - 1, by: 2 }, "loggedIn", false);
```

**Filter-based updates**:

```tsx
setStore("users", user => user.location === "Canada", "loggedIn", false);
setStore("users", user => user.username.startsWith("t"), "loggedIn", false);
```

Multi-setter calls are automatically wrapped in `batch()`, so all elements
update before downstream effects fire.

## Store Utilities

### produce

Apply mutable-style changes to a store through a draft proxy:

```tsx
import { produce } from "solid-js/store";

setStore("users", 0, produce(user => {
  user.username = "newName";
  user.location = "newPlace";
}));
```

Works with objects and arrays. Not compatible with Sets or Maps.

### reconcile

Merge new data into existing store state, updating only changed values:

```tsx
import { reconcile } from "solid-js/store";

const newData = await fetchUsers();
setData("animals", reconcile(newData));
```

Options:
- `key` — property name used to match items (default: index for arrays)
- `merge` — shallow merge objects instead of replacing (default: false)

### unwrap

Convert a store to a plain JavaScript object (non-reactive snapshot):

```tsx
import { unwrap } from "solid-js/store";

const rawData = unwrap(store);
// rawData is a regular object, not a proxy
```

Useful for:
- Logging state without proxy overhead
- Passing data to third-party libraries expecting plain objects
- Serialization

### createMutable / modifyMutable

For imperative mutations within tracking scopes:

```tsx
import { createMutable } from "solid-js/store";

const mutable = createMutable({ count: 0 });
mutable.count++; // Direct mutation, tracked reactively
```
