# Reactivity Fundamentals

SolidJS's reactivity system is built on fine-grained tracking and updates. This document covers signals, memos, effects, and the reactive graph.

## Signals

Signals are the primitive for managing reactive state in SolidJS.

### Creating Signals

```jsx
import { createSignal } from "solid-js";

// Basic signal with initial value
const [count, setCount] = createSignal(0);

// Signal with options
const [name, setName] = createSignal("Alice", {
  equals: true, // Default: skip update if new value === old value
});

// Disable equality check for always-updating signals
const [tick, setTick] = createSignal(0, { equals: false });
```

### Accessing Signal Values

Always call the getter function to access the current value:

```jsx
const [count, setCount] = createSignal(0);

// Correct - calls the getter
console.log(count()); // 0

// Wrong - gets the signal object itself
console.log(count); // [Function count]
```

### Updating Signals

```jsx
const [count, setCount] = createSignal(0);

// Set a new value directly
setCount(5);

// Update based on previous value (useful for avoiding race conditions)
setCount((prev) => prev + 1);

// Use object spread for immutable updates
setCount({ ...count(), newValue: "test" });
```

### Signal Options

```jsx
// Skip update if values are equal (default behavior)
const [value, setValue] = createSignal(0, { equals: true });
setValue(0); // No update triggered

// Always trigger updates
const [tick, setTick] = createSignal(0, { equals: false });
setTick(0); // Update still triggered even though value is same
```

## Memos

Memos are computed values that automatically update when their dependencies change.

### Basic Memo

```jsx
import { createSignal, createMemo } from "solid-js";

const [firstName, setFirstName] = createSignal("John");
const [lastName, setLastName] = createSignal("Doe");

// Computed value that updates when firstName or lastName changes
const fullName = createMemo(() => `${firstName()} ${lastName()}`);

console.log(fullName()); // "John Doe"

setFirstName("Jane");
console.log(fullName()); // "Jane Doe" - automatically updated
```

### Memo Options

```jsx
const [input, setInput] = createSignal("");

// Initialize with undefined and compute lazily
const uppercased = createMemo(
  () => input().toUpperCase(),
  undefined, // Initial value (undefined = lazy init)
  { equals: false } // Always notify even if value unchanged
);
```

### Memo vs Signal

Use memos when:
- Computing derived values from other signals/memos
- Expensive calculations that should cache results
- Filtering or transforming lists reactively

```jsx
// Using memo for filtering
const [items, setItems] = createSignal([]);
const [filter, setFilter] = createSignal("");

const filteredItems = createMemo(() =>
  items().filter((item) =>
    item.name.toLowerCase().includes(filter().toLowerCase())
  )
);

// Expensive computation cached via memo
const [data, setData] = createSignal([]);

const processedData = createMemo(() => {
  // This only runs when data() changes
  return data().map((item) => expensiveTransformation(item));
});
```

## Effects

Effects run side effects reactively when their dependencies change.

### Basic Effect

```jsx
import { createSignal, createEffect } from "solid-js";

const [count, setCount] = createSignal(0);

// Effect runs once on creation, then whenever count() changes
createEffect(() => {
  console.log("Count is:", count());
});

setCount(1); // Logs: "Count is: 1"
```

### Effect Cleanup

Effects can return cleanup functions that run before the next execution:

```jsx
const [id, setId] = createSignal(1);

createEffect(() => {
  const subscription = subscribeTo(id(), handleUpdate);

  // Cleanup runs before effect re-runs or on unmount
  return () => {
    unsubscribe(subscription);
  };
});
```

### Effect Options

```jsx
const [value, setValue] = createSignal(0);

// Defer effect until after component renders (default)
createEffect(() => {
  console.log("Runs after render:", value());
});

// Run effect immediately during creation
createEffect(() => {
  console.log("Runs immediately:", value());
}, undefined, { defer: false });
```

### Effects vs Memos

| Memo | Effect |
|------|--------|
| Returns computed value | Returns void (side effects) |
| Lazily evaluated | Runs immediately (or deferred) |
| Used in other reactive contexts | Used for side effects only |
| Pure computation | Can have impure side effects |

```jsx
// Use memo for computed values
const [price, setPrice] = createSignal(100);
const [tax, setTax] = createSignal(0.1);

const total = createMemo(() => price() * (1 + tax()));

// Use effect for side effects
createEffect(() => {
  document.title = `Total: $${total()}`;
});
```

## Tracking Scopes

Tracking scopes are contexts where signal reads are tracked for reactivity.

### Automatic Tracking Scopes

These automatically create tracking scopes:
- Component functions (JSX return)
- `createEffect()` callbacks
- `createMemo()` callbacks
- `createRenderEffect()` callbacks
- `createSelector()` selectors
- Event handler functions

```jsx
// Component is a tracking scope
function Counter() {
  const [count, setCount] = createSignal(0);

  // This read is tracked
  return <div>{count()}</div>;
}

// Effect callback is a tracking scope
createEffect(() => {
  // This read is tracked
  console.log(count());
});
```

### Manual Tracking with `createReaction`

For custom tracking scopes:

```jsx
import { createSignal, createReaction } from "solid-js";

const [value, setValue] = createSignal(0);

const reaction = createReaction(() => {
  // This code is tracked
  console.log("Current value:", value());
});

// Trigger the reaction manually
reaction();

// Dispose when done
reaction.dispose();
```

### `on` for Conditional Tracking

The `on` function allows tracking specific signal changes:

```jsx
import { createSignal, createEffect, on } from "solid-js";

const [user, setUser] = createSignal(null);
const [settings, setSettings] = createSignal({});

// Effect runs only when user changes, not settings
createEffect(
  on([user], ([newUser]) => {
    console.log("User changed:", newUser);
  })
);

// Get previous and current values
createEffect(
  on(
    [user],
    ([newUser, oldUser]) => {
      console.log("Changed from", oldUser, "to", newUser);
    },
    { defer: false }
  )
);
```

### `onMount`, `onCleanup`, `onError`

Lifecycle utilities for components:

```jsx
import { onMount, onCleanup, onError } from "solid-js";

function DataFetcher() {
  const [data, setData] = createSignal(null);

  onMount(() => {
    console.log("Component mounted");

    // Fetch data
    fetch("/api/data").then((res) => res.json()).then(setData);

    // Cleanup on unmount
    onCleanup(() => {
      console.log("Component unmounting");
      // Cancel pending requests, clear timers, etc.
    });
  });

  onError((error) => {
    console.error("Error in component:", error);
  });

  return <div>{data() ? "Loaded" : "Loading..."}</div>;
}
```

## Batch Updates

Solid automatically batches updates within the same tick:

```jsx
const [a, setA] = createSignal(0);
const [b, setB] = createSignal(0);
const [c, setC] = createSignal(0);

createEffect(() => {
  console.log("Effect runs once:", a(), b(), c());
});

// All updates batched - effect runs only once
setA(1);
setB(2);
setC(3);
```

### Manual Batching with `batch`

For explicit control over batching:

```jsx
import { batch } from "solid-js";

const [count, setCount] = createSignal(0);
const [double, setDouble] = createSignal(0);

createEffect(() => {
  console.log("Runs once with final values:", count(), double());
});

batch(() => {
  setCount(5);
  setDouble(count() * 2); // Uses OLD value of count (5 not 10)
});

// To use updated values within batch:
batch(() => {
  setCount(5);
  setDouble(count() * 2); // Still uses old value
  
  // Force re-evaluation
  setDouble(() => count() * 2); // Now gets 10
});
```

## Untracking

Sometimes you need to read a signal without creating a dependency:

### `untrack` Function

```jsx
import { untrack } from "solid-js";

const [count, setCount] = createSignal(0);
const [limit, setLimit] = createSignal(10);

// Effect only tracks limit, not count
createEffect(() => {
  const currentCount = untrack(count);
  console.log(`Limit: ${limit()}, Current count (untracked): ${currentCount}`);
});

setCount(5); // No effect trigger
setLimit(20); // Effect triggers
```

### Common Untracking Patterns

```jsx
// Logging without creating dependency
createEffect(() => {
  console.log("Current state:", untrack(state));
  doSomethingWith(trackedValue());
});

// Using signal value in non-reactive context
const [items, setItems] = createSignal([]);

function addItem(item) {
  // Don't track here - this is an event handler
  const currentItems = untrack(items);
  setItems([...currentItems, item]);
}
```

## Derived Signals

Shorthand for creating memos with a specific pattern:

```jsx
import { createSignal, createDerived } from "solid-js";

const [base, setBase] = createSignal(10);

// Computed signal
const doubled = createDerived(() => base() * 2);

console.log(doubled()); // 20
setBase(5);
console.log(doubled()); // 10
```

## Best Practices

1. **Create signals at component top level** - Don't create signals inside conditionals or loops
2. **Use memos for expensive computations** - Cache results that depend on signals
3. **Prefer effects for side effects** - Don't do side effects in component body
4. **Clean up effects properly** - Return cleanup functions for subscriptions, timers
5. **Avoid breaking reactivity** - Always call signals as functions `signal()`

## Common Pitfalls

### Reading Signal Outside Tracking Scope

```jsx
const [count, setCount] = createSignal(0);

// This won't trigger reactivity
function updateDisplay() {
  console.log(count()); // Read outside tracking scope - no dependency created
}
```

### Creating Signals in Loops

```jsx
// Wrong - creates new signal each iteration
items.forEach((item) => {
  const [selected, setSelected] = createSignal(false);
});

// Correct - create array of signals
const selections = items.map(() => createSignal(false));
```

### Mutating Signal Values

```jsx
const [items, setItems] = createSignal([]);

// Wrong - mutates the array
items().push(newItem);

// Correct - creates new array
setItems([...items(), newItem]);
```
