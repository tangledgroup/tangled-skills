# Signals and Memos

## createSignal

`createSignal` creates a reactive state primitive consisting of a getter
(accessor) and a setter function. It is the foundation of Solid's reactivity
system.

```tsx
import { createSignal } from "solid-js";

const [count, setCount] = createSignal(0);
//       ^ getter  ^ setter

console.log(count()); // 0
setCount(5);
console.log(count()); // 5
```

### Setter Forms

The setter accepts either a direct value or a function receiving the previous value:

```tsx
setCount(10);                    // Direct value
setCount(prev => prev + 1);      // Function form (useful for batched updates)
```

### Signal Options

```tsx
const [value, setValue] = createSignal("initial", {
  name: "mySignal",    // Debug name for devtools
  equals: false,       // Always notify on change (disable === check)
  // or custom equality:
  equals: (prev, next) => prev.id === next.id,
});
```

- `name` — debug label for Solid DevTools (development only)
- `equals` — comparison function; default is strict equality (`===`). Set to
  `false` to always trigger updates even when value is unchanged.

### When to Use Signals

- Primitive values (strings, numbers, booleans)
- Simple objects read as a whole
- Values read frequently but written infrequently
- State that doesn't need property-level granularity

## createMemo

`createMemo` creates a read-only signal that derives its value from other
reactive values. The computation runs only when dependencies change, and the
result is cached.

```tsx
import { createSignal, createMemo } from "solid-js";

const [items, setItems] = createSignal([1, 2, 3, 4, 5]);

const total = createMemo(() =>
  items().reduce((sum, n) => sum + n, 0)
);

console.log(total()); // 15
```

### Memo Behavior

- The callback receives the previous computed value as its argument
- Calculation runs only when tracked dependencies change
- If the new result equals the previous (per `equals` option), downstream
  updates are suppressed
- Memos create a tracking scope — signals accessed inside are subscribed

### When to Use Memos

- Expensive computations that should be cached
- Derived values from other signals/memos
- Filtering or transforming large data sets
- Values consumed by many downstream consumers

### Memo vs. Derived Signal Function

A plain function wrapping signal reads is not tracked:

```tsx
// ❌ Not reactive — this is just a function, not a tracking scope
const doubleCount = () => count() * 2;
```

This works in JSX because the JSX return is itself a tracking scope. But if
you need the derived value outside JSX (e.g., in an effect), use `createMemo`:

```tsx
// ✅ Reactive — createMemo creates a tracking scope
const doubleCount = createMemo(() => count() * 2);
```

## createResource

`createResource` manages asynchronous data fetching with built-in loading
states and Suspense integration.

```tsx
import { createResource } from "solid-js";

function App() {
  const [user] = createResource(async () => {
    const res = await fetch("/api/user");
    return res.json();
  });

  return (
    <div>
      {/* Access resource like a signal */}
      <p>Name: {user()?.name}</p>

      {/* Check loading state */}
      <Show when={user.loading}>
        <p>Loading...</p>
      </Show>

      {/* Access latest value (may be stale) */}
      <p>Latest: {user.latest?.name}</p>
    </div>
  );
}
```

### Resource Properties

- `resource()` — current value (getter, like a signal)
- `resource.state` — `"unresolved" | "pending" | "ready" | "refreshing" | "errored"`
- `resource.loading` — boolean shorthand for pending states
- `resource.error` — error object if fetch failed
- `resource.latest` — most recent resolved value (may be stale if new fetch pending)

### Resource Actions

- `mutate(value)` — imperatively update the resource value
- `refetch()` — re-run the fetcher function

### Source-Based Resources

Resources can depend on a source signal, automatically refetching when it changes:

```tsx
const [id, setId] = createSignal(1);
const [data] = createResource(id, async (sourceId) => {
  const res = await fetch(`/api/items/${sourceId}`);
  return res.json();
});

setId(2); // Automatically refetches with id=2
```
