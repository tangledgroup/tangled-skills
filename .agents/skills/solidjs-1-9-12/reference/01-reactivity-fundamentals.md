# Reactivity Fundamentals

## The Reactive Graph

Solid's reactivity system is a directed graph where:

- **Signals** are nodes that hold values and track subscribers
- **Effects/Memos** are subscriber nodes that depend on signals
- When a signal changes, it notifies its downstream subscribers in order

The graph is built automatically — you never manually wire dependencies.

## Tracking Scopes

Reactivity only works inside tracking scopes. A tracking scope is created by:

- JSX return statements (the `<div>{count()}</div>` expression)
- `createEffect()` callback
- `createMemo()` callback
- `createResource()` fetcher function

Outside these scopes, reading a signal does not establish a dependency:

```tsx
function App() {
  const [count, setCount] = createSignal(0);

  // ❌ Not tracked — only runs once during initialization
  console.log("Count:", count());

  // ✅ Tracked — re-runs whenever count changes
  createEffect(() => {
    console.log("Count:", count());
  });

  return (
    <div>
      {/* ✅ Tracked — DOM updates when count() changes */}
      <span>Count: {count()}</span>
    </div>
  );
}
```

## Synchronous vs. Asynchronous Reactivity

**Synchronous reactivity** is Solid's default. When a signal changes,
subscribers update immediately in an ordered manner. This ensures predictable
update ordering when subscribers depend on each other.

**Asynchronous reactivity** delays subscriber updates until all related signals
have been updated. Use `batch()` to group multiple signal updates so that
downstream computations run once after the batch completes:

```tsx
import { createSignal, createEffect, batch } from "solid-js";

const [a, setA] = createSignal(0);
const [b, setB] = createSignal(0);

createEffect(() => {
  console.log(a(), b()); // runs once after both update
});

batch(() => {
  setA(1);
  setB(2);
});
```

## Read-Write Segregation

Solid encourages separating reads from writes:

- **Reads**: signal getters (`count()`), store property access (`store.user.name`)
- **Writes**: signal setters (`setCount(1)`), store setters (`setStore("user", { name: "new" })`)

This separation aids debugging — you can trace which components read or write
each piece of state.

## Component Lifecycle and Reactivity

Solid components run **once**. The component function body executes a single
time to set up state, effects, and the initial DOM structure. After that, only
the reactive parts of the JSX update when signals change.

This is different from frameworks that re-execute the entire component on every
state change. In Solid:

1. Component runs once → creates signals, effects, and DOM nodes
2. Signal changes → only the specific DOM node or effect that depends on it updates
3. The component function body never re-runs

This means getting the initial setup right is important — signals accessed in
the component body (outside JSX) are not tracked.

## Key Principles

- Signals store and manage data through getters and setters
- Subscribers (effects, memos) automatically track signal dependencies
- A tracking scope must exist for reactivity to work
- Components run once; reactivity handles updates
- The system is synchronous by default; use `batch()` for async grouping
- Read-write segregation keeps state changes traceable
