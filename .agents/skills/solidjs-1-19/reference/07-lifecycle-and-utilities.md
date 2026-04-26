# Lifecycle and Utilities

## onMount

Runs once after the initial render. Does not track dependencies.

```tsx
import { onMount } from "solid-js";

function Component() {
  const [data, setData] = createSignal(null);

  onMount(async () => {
    const res = await fetch("/api/data");
    setData(await res.json());
  });

  return <div>{data()?.title}</div>;
}
```

- Runs after refs are assigned
- Does not run during SSR or initial hydration
- Equivalent to `createEffect(() => untrack(fn))` internally

## onCleanup

Registers a cleanup function that runs when the reactive scope is disposed.

```tsx
import { onCleanup } from "solid-js";

function Component() {
  const [count, setCount] = createSignal(0);

  const timer = setInterval(() => {
    setCount(c => c + 1);
  }, 1000);

  onCleanup(() => {
    clearInterval(timer);
  });

  return <div>Count: {count()}</div>;
}
```

- In a component, runs when the component unmounts
- In `createEffect`/`createMemo`, runs when that scope disposes or re-executes
- Multiple cleanups run when the owning scope is cleaned up
- Calling outside a reactive owner does nothing (warns in development)

## batch

Groups multiple reactive updates so downstream computations run once after
the batch completes:

```tsx
import { batch } from "solid-js";

batch(() => {
  setA(1);
  setB(2);
  setC(3);
});
// Effects depending on A, B, or C run only once
```

- Nested `batch` calls merge into a single batch
- Reading stale values inside batch triggers on-demand update
- Async functions: batching applies only before the first `await`

### Automatic Batching

Solid automatically batches in these cases:
- Inside `createEffect` and `onMount`
- Inside store setters (`setStore`)
- Inside array mutations on `createMutable`

## untrack

Execute a function without collecting dependencies:

```tsx
import { untrack } from "solid-js";

createEffect(() => {
  const current = untrack(() => count());
  // This effect won't re-run when count changes
});
```

Common use cases:
- Reading a signal for its initial/static value inside an effect
- Passing a non-reactive snapshot to a callback
- Preventing unnecessary subscriptions

## createRoot

Creates a new owned context that requires explicit disposal:

```tsx
import { createRoot } from "solid-js";

const result = createRoot((dispose) => {
  const [count, setCount] = createSignal(0);
  // Computations persist until dispose() is called
  return count();
});

// Later...
dispose(); // Clean up all computations in this root
```

- Useful for top-level code outside components
- Computations are not auto-disposed
- Returns the value from the callback function

## startTransition / useTransition

Mark non-urgent state updates that can be deferred:

```tsx
import { startTransition, useTransition } from "solid-js";

const [pending, start] = useTransition();

start(() => setTab("settings"));
// `pending` is true while transition runs
```

- Defers updates to keep UI responsive
- Works with Suspense for progressive rendering
- `useTransition` returns `[pending, start]` tuple
- `startTransition(fn)` is the standalone version

## mapArray / indexArray

Transform arrays reactively:

```tsx
import { mapArray } from "solid-js";

const [items, setItems] = createSignal([1, 2, 3]);

const doubled = mapArray(items, item => createMemo(() => item() * 2));
// Returns an array of memos, each tracking its own item
```

## observable

Convert a signal into an async iterator:

```tsx
import { observable } from "solid-js";

for await (const value of observable(count)) {
  console.log("Count is now:", value);
}
```

## mergeProps / splitProps

- `mergeProps(...objects)` — left-to-right merge, later props override earlier
- `splitProps(props, ...keys)` — partition props into subsets
