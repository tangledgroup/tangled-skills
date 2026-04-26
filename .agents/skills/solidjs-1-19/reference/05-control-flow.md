# Control Flow

Solid provides built-in control flow components for conditional and list
rendering. These are more efficient than JavaScript ternary/map patterns
because they track their dependencies precisely.

## Conditional Rendering

### Show

`<Show>` renders children when a condition is truthy:

```tsx
import { Show } from "solid-js";

<Show when={user()}>
  <p>Hello, {user().name}!</p>
</Show>
```

With fallback for the false case:

```tsx
<Show when={!loading()} fallback={<div>Loading...</div>}>
  <h1>{data().title}</h1>
</Show>
```

Nested `<Show>` for multiple conditions:

```tsx
<Show when={state() === "loading"}>
  <p>Loading...</p>
</Show>
<Show when={state() === "error"}>
  <p>Error occurred</p>
</Show>
<Show when={state() === "success"}>
  <p>Success!</p>
</Show>
```

### Switch and Match

For mutually exclusive conditions, use `<Switch>` with `<Match>`:

```tsx
import { Switch, Match } from "solid-js";

<Switch fallback={<p>Unknown state</p>}>
  <Match when={status() === "loading"}>
    <p>Loading...</p>
  </Match>
  <Match when={status() === "error"}>
    <p>Error!</p>
  </Match>
  <Match when={status() === "success"}>
    <p>Done!</p>
  </Match>
</Switch>
```

Only the first matching `<Match>` renders. Falls back to `<Switch>`'s
`fallback` if no match.

### keyed Option

By default, children receive an accessor function. Set `keyed: true` to
receive the value directly (re-creates children on every change):

```tsx
<Show when={user()} keyed>
  {(user) => <p>Hello, {user.name}!</p>}
</Show>
```

## List Rendering

### For

`<For>` renders lists by item identity. Best for arrays of objects where order
and length change frequently:

```tsx
import { For } from "solid-js";

<For each={items()}>
  {(item, index) => (
    <li style={{ color: index() % 2 === 0 ? "red" : "blue" }}>
      {item.name}
    </li>
  )}
</For>
```

- `each` — the array to iterate over
- `fallback` — content when `each` is empty/null/undefined/false
- `index` is a signal (call as `index()`)

### Index

`<Index>` renders lists by position. Best when list order and length are stable
but content changes frequently:

```tsx
import { Index } from "solid-js";

<Index each={items()}>
  {(item, index) => (
    <li>
      Item {index}: {item}
    </li>
  )}
</Index>
```

### For vs. Index

- Use `<For>` when items are identified by data (e.g., user objects with IDs)
- Use `<Index>` when items are identified by position (e.g., form fields, tabs)
- `<For>` preserves DOM nodes across reordering; `<Index>` does not

## Suspense

`<Suspense>` renders fallback content while async dependencies are pending:

```tsx
import { Suspense } from "solid-js";

<Suspense fallback={<div>Loading...</div>}>
  <UserDetails />
</Suspense>
```

Works with `createResource` and `lazy()` components. Nested suspense boundaries
each handle their own async dependencies.

## ErrorBoundary

Catch rendering errors and show fallback content:

```tsx
import { ErrorBoundary } from "solid-js";

<ErrorBoundary fallback={(err, reset) => (
  <div>
    <p>Something went wrong</p>
    <button onClick={reset}>Try again</button>
  </div>
)}>
  <ComponentThatMightError />
</ErrorBoundary>
```

## Portal

Render content outside the normal DOM hierarchy:

```tsx
import { Portal } from "solid-js/web";

<Portal mount={document.body}>
  <div class="modal">Modal content</div>
</Portal>
```

- `mount` — target DOM node (default: document.body)
- `useShadowDOM` — render into shadow root
