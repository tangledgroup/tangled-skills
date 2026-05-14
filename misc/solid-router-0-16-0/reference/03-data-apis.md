# Data APIs

Solid Router provides a data fetching and mutation layer built on top of its preload mechanism. These APIs are optional — you can use plain `fetch` in preload functions if preferred.

## `query`

Wraps an async function with deduplication, caching, and revalidation. Accepts the function and a key string.

```jsx
import { query } from "@solidjs/router";

const getUser = query(async (id) => {
  return (await fetch(`/api/users/${id}`)).json();
}, "users");
```

Behavior:

- **Server deduping** — During a single request, identical calls return the same promise
- **Preload cache** — 5-second browser cache; deduplicates calls during route preload and navigation
- **Reactive revalidation** — Based on key, routes can retrigger on action completion
- **Back/forward cache** — Up to 5 minutes for browser navigation; user navigation bypasses this cache

Key helpers:

```ts
getUser.key;       // "users"
getUser.keyFor(5); // "users[5]"
```

### Using query with preload

```jsx
// route.data.js
import { query } from "@solidjs/router";

export const getUser = query(async (id) => {
  return (await fetch(`/api/users/${id}`)).json();
}, "users");

export function preloadUser({ params }) {
  void getUser(params.id);
}
```

```jsx
// pages/users/[id].js
import { createAsync } from "@solidjs/router";
import { getUser } from "./route.data.js";

export default function User(props) {
  const user = createAsync(() => getUser(props.params.id));
  return <h1>{user().name}</h1>;
}
```

## `createAsync`

A reactive async primitive — a simpler alternative to `createResource`. The function tracks like `createMemo`, expects a promise, and returns a signal. Reading it before ready triggers Suspense/Transitions.

```jsx
import { createAsync } from "@solidjs/router";

const user = createAsync(() => getUser(params.id));
return <h1>{user().name}</h1>;
```

Options:

- `name` — Debug name
- `initialValue` — Initial value before promise resolves
- `deferStream` — Defer streaming on server

The `.latest` field provides the most recent resolved value (transitional, will be removed in future).

## `createAsyncStore`

Similar to `createAsync` but uses a deeply reactive store via `createStore` + `reconcile`. Ideal for fine-grained updates to large model data.

```jsx
import { createAsyncStore } from "@solidjs/router";

const todos = createAsyncStore(() => getTodos());
```

Supports the same options as `createAsync` plus `reconcile` for custom reconciliation options.

## `action`

Actions are data mutations that can trigger revalidation and routing via response helpers. They work with `<form>` elements or programmatically via `useAction`.

```jsx
import { action, redirect } from "@solidjs/router";

const myAction = action(async (formData) => {
  await doMutation(formData);
  throw redirect("/", { revalidate: getUser.keyFor(formData.get("id")) });
});
```

### Form-based actions

Actions only work with POST requests. Include `method="post"` on the form:

```jsx
<form action={myAction} method="post">
  <input type="hidden" name="id" value={todo.id} />
  <button type="submit">Delete</button>
</form>
```

### Typed actions with `.with()`

Instead of `FormData`, use `.with()` to bind arguments:

```jsx
const deleteTodo = action(api.deleteTodo);

<form action={deleteTodo.with(todo.id)} method="post">
  <button type="submit">Delete</button>
</form>
```

### Action options

```jsx
const myAction = action(async (args) => {
  // ...
}, {
  name: "my-action",           // Required for SSR (stable reference)
  onComplete: (submission) => {
    console.log("done", submission.result, submission.error);
  }
});
```

The `name` is required for SSR actions that aren't server functions — it provides a stable serializable reference.

## `useAction`

Wrap an action to call it programmatically (outside of form context):

```jsx
import { useAction } from "@solidjs/router";

const submit = useAction(myAction);
submit(...args);
```

Requires client-side JavaScript — not progressive-enhanceable like forms.

## `useSubmission` / `useSubmissions`

Track in-flight actions for optimistic UI:

```jsx
import { useSubmission, useSubmissions } from "@solidjs/router";

// Latest submission matching the action
const submission = useSubmission(action);

// All submissions matching the action (with optional filter)
const submissions = useSubmissions(action, (input) => filter(input));
```

Each `Submission` has:

- `input` — Arguments passed to the action
- `result` — Resolved value (when complete)
- `error` — Error (when failed)
- `pending` — Boolean, true while in-flight
- `url` — Action URL
- `clear()` — Remove this submission
- `retry()` — Retry the action

## Response Helpers

Thrown from within actions or queries to control navigation.

### `redirect(path, options)`

Redirects to another route. Accepts a status code or options object with `revalidate`:

```jsx
const getUser = query(async () => {
  const user = await api.getCurrentUser();
  if (!user) throw redirect("/login");
  return user;
}, "currentUser");
```

```jsx
// With revalidation
throw redirect("/", { revalidate: getUser.key });
```

### `reload(options)`

Reloads data on the current page without navigation:

```jsx
const updateTodo = action(async (todo) => {
  await api.updateTodo(todo.id, todo);
  reload({ revalidate: getTodo.keyFor(todo.id) });
});
```

### `json(data, options)`

Returns a JSON response with optional revalidation:

```jsx
import { json } from "@solidjs/router";

throw json({ success: true }, { revalidate: "todos" });
```

## `revalidate`

Programmatically invalidate cached query entries:

```jsx
import { revalidate } from "@solidjs/router";

// Revalidate all entries for a key
revalidate("users");

// Revalidate specific entry
revalidate(getUser.keyFor(5));
```
