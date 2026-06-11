# Advanced Reactivity

## Fine-Grained Reactivity

Solid updates only the specific DOM nodes that depend on changed signals.
Unlike frameworks that re-execute entire components, Solid's compiler generates
code that creates real DOM nodes and inserts reactive markers at exactly the
points where dynamic values appear.

Compiled output example:

```js
// What Solid compiles JSX into (simplified)
const _tmpl$ = template(`<button>Count: </button>`);

function Counter() {
  const [count, setCount] = createSignal(0);

  return () => {
    const _el$ = _tmpl$();
    _el$.onclick = () => setCount(c => c + 1);
    insert(_el$, count); // Only this text node updates
    return _el$;
  };
}
```

## Secondary Primitives

### createComputed

Immediate reactive computation that runs synchronously when created and
whenever dependencies change:

```tsx
import { createComputed } from "solid-js";

createComputed(() => {
  // Runs immediately, then on every dependency change
  console.log("Depended value:", dependentSignal());
});
```

Unlike `createEffect`, it runs **synchronously** in the current execution
context. Use for building custom reactive primitives, not for side effects.

### createReaction

Creates a subscriber that tracks signals without creating a computation:

```tsx
import { createReaction } from "solid-js";

const reaction = createReaction((value) => {
  console.log("Reacted to change:", value);
});
```

### createDeferred

Creates a signal that follows another signal with a delay:

```tsx
import { createSignal, createDeferred } from "solid-js";

const [count, setCount] = createSignal(0);
const deferred = createDeferred(count, { timeoutMs: 100 });

// `deferred()` lags behind `count()` by up to 100ms
```

### createRenderEffect

A specialized effect that runs immediately (not scheduled) and is designed
for rendering logic:

```tsx
import { createRenderEffect } from "solid-js";

createRenderEffect(() => {
  // Runs synchronously when dependencies change
  console.log("Render:", count());
});
```

## createSelector

Creates a memoized computation that only triggers downstream subscribers
when its value actually changes (suppresses more aggressively than `createMemo`):

```tsx
import { createSelector } from "solid-js";

const isSelected = createSelector(() =>
  items().filter(i => i.selected).length > 0
);
```

## getOwner / runWithOwner

Manipulate the reactive owner context:

```tsx
import { getOwner, runWithOwner } from "solid-js";

const owner = getOwner(); // Current reactive owner

runWithOwner(owner, () => {
  // Creates computations under the captured owner
  createEffect(() => console.log("Runs in original owner's scope"));
});
```

Useful for:
- Creating effects outside their normal component scope
- Building custom primitives that need specific ownership
- Debugging reactive graph structure

## catch_error

Catch errors from synchronous computations:

```tsx
import { catchError } from "solid-js";

catchError((err) => {
  console.error("Caught:", err);
});
```

## Server-Side Rendering (SSR)

Solid supports SSR through `solid-js/web`:

```tsx
import { renderToString } from "solid-js/web";

const html = renderToString(() => <App />);
```

### SSR APIs

- `renderToString` — synchronous SSR
- `renderToStringAsync` — async SSR (supports Suspense)
- `renderToStream` — streaming SSR with progressive hydration
- `hydrate` — client-side hydration of server-rendered markup
- `isServer` — boolean, true during SSR
- `isDev` — boolean, true in development mode

### NoHydration

Skip hydrating content that differs between server and client:

```tsx
import { NoHydration } from "solid-js/web";

<div>
  <NoHydration>
    <p>Only on client</p>
  </NoHydration>
  <p>Hydrated on both</p>
</div>
```

## TypeScript Support

Solid has full TypeScript support. Key types:

```tsx
import type { ParentProps, JSX } from "solid-js";

// Typed component props
interface ButtonProps {
  label: string;
  onClick?: () => void;
}

function Button(props: ButtonProps) {
  return <button onClick={props.onClick}>{props.label}</button>;
}

// With children
function Wrapper(props: ParentProps<{ title: string }>) {
  return (
    <div>
      <h1>{props.title}</h1>
      {props.children}
    </div>
  );
}

// JSX type for custom elements
namespace JSX {
  interface IntrinsicElements {
    "my-custom-element": {
      "on-my-event"?: (e: CustomEvent) => void;
    };
  }
}
```
