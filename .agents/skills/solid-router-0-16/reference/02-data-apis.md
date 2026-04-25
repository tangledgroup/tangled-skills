# Solid Router Data APIs

This reference covers preload functions, the query API, createAsync, actions, and form handling in Solid Router v0.16.

## Preload Functions

Preload functions enable parallel data fetching during navigation, following the "render-as-you-fetch" pattern. They're called when routes are loaded or eagerly on link hover.

### Basic Usage

```jsx
import { lazy } from "solid-js";
import { Route } from "@solidjs/router";

const User = lazy(() => import("./pages/User"));

// Preload function receives route context
function preloadUser({ params, location, intent }) {
  // Fetch data in parallel with navigation
  fetch(`/api/users/${params.id}`).then(res => res.json());
}

<Route path="/users/:id" component={User} preload={preloadUser} />;
```

### Preload Context Object

| Key | Type | Description |
|-----|------|-------------|
| `params` | object | Route parameters (same as `useParams()`) |
| `location` | object | Location info: `{ pathname, search, hash, query, state, key }` |
| `intent` | string | Why preload is called: `"initial"`, `"navigate"`, `"native"`, `"preload"` |

**Intent values:**
- `"initial"` - Route being initially shown (page load)
- `"navigate"` - Navigation from router (link click, navigate call)
- `"native"` - Browser navigation (back/forward buttons)
- `"preload"` - Preloading only (link hover), not navigating

### Pattern: Separate Data File

Export preload functions separately to avoid loading route components:

```jsx
// pages/users/[id].data.js
import { query } from "@solidjs/router";

export const getUser = query(async (id) => {
  const res = await fetch(`/api/users/${id}`);
  return res.json();
}, "user"); // Query key for caching

export default async function preloadUser({ params }) {
  void getUser(params.id); // Trigger fetch, don't await
}
```

```jsx
// App.jsx
import preloadUser from "./pages/users/[id].data.js";
const User = lazy(() => import("./pages/User"));

<Route path="/users/:id" component={User} preload={preloadUser} />;
```

## Query API

The `query` function provides deduplication, caching, and revalidation for data fetching.

### Creating Queries

```jsx
import { query } from "@solidjs/router";

// Basic query with key
const getUser = query(async (id) => {
  const res = await fetch(`/api/users/${id}`);
  return res.json();
}, "user"); // Key for caching + serialized args

// Query returns a function with the same signature
const user = await getUser(123);
```

### Query Features

1. **Server-side deduping** - Multiple calls during request lifecycle share one fetch
2. **Browser preload cache** - 5-second cache for preloaded data
3. **Reactive refetching** - Trigger revalidation based on keys
4. **Back/forward cache** - Up to 5 minutes for browser navigation

### Query Key Methods

```jsx
const getUser = query(async (id) => { /* ... */ }, "user");

getUser.key; // "user"
getUser.keyFor(123); // "user[123]"
getUser.keyFor({ id: 123, name: "John" }); // "user[{\"id\":123,\"name\":\"John\"}]"
```

### Revalidation

Invalidate cached data to trigger refetch:

```jsx
// In an action or effect
const updateUser = action(async (userData) => {
  await api.updateUser(userData);
  // Revalidate specific query entry
  reload({ revalidate: getUser.keyFor(userData.id) });
});

// Or invalidate all entries for a query key
reload({ revalidate: "user" });
```

## createAsync

A reactive wrapper for async operations, similar to `createResource` but simpler and designed to work with `query`.

### Basic Usage

```jsx
import { createAsync } from "@solidjs/router";

function User(props) {
  const user = createAsync(() => getUser(props.params.id));
  
  return (
    <Suspense fallback={<Loading />}>
      <h1>{user().name}</h1>
    </Suspense>
  );
}
```

### Latest Value

Access the most recent value (useful for race conditions):

```jsx
const user = createAsync(() => getUser(params.id));

// .latest is deprecated but still available
<h1>{user.latest.name}</h1>
```

### Error Handling

```jsx
function User(props) {
  const [user, setUser] = createAsync(
    () => getUser(props.params.id),
    { onError: (error) => console.error(error) }
  );
  
  return (
    <Suspense fallback={<Loading />}>
      <h1>{user()?.name || "User not found"}</h1>
    </Suspense>
  );
}
```

## createAsyncStore

Similar to `createAsync` but uses a deeply reactive store, ideal for large data models:

```jsx
import { createAsyncStore } from "@solidjs/router";

function Todos() {
  const todos = createAsyncStore(() => getTodos());
  
  return (
    <Suspense fallback={<Loading />}>
      <ul>
        {todos()?.map(todo => (
          <li>{todo.text}</li>
        ))}
      </ul>
    </Suspense>
  );
}
```

## Actions

Actions handle data mutations and can trigger navigation or revalidation.

### Creating Actions

```jsx
import { action } from "@solidjs/router";

const createUser = action(async (formData) => {
  const name = formData.get("name");
  const email = formData.get("email");
  
  await api.createUser({ name, email });
});
```

### Using Actions with Forms

```jsx
<form action={createUser} method="post">
  <input type="text" name="name" required />
  <input type="email" name="email" required />
  <button type="submit">Create User</button>
</form>
```

**Important:** Forms must use `method="post"` for actions.

### Action with Typed Data (`.with()`)

Avoid FormData by binding arguments:

```jsx
const deleteTodo = action(async (id) => {
  await api.deleteTodo(id);
});

// Bind the argument
<form action={deleteTodo.with(todo.id)} method="post">
  <button type="submit">Delete</button>
</form>
```

### Action with Name and onComplete

```jsx
const myAction = action(
  async (data) => {
    await doMutation(data);
  },
  {
    name: "my-action", // Required for SSR/server functions
    onComplete: () => {
      console.log("Action completed");
      // Run after action finishes
    }
  }
);
```

### Using Actions Programmatically

```jsx
import { useAction } from "@solidjs/router";

function MyComponent() {
  const submit = useAction(myAction);
  
  return (
    <button onClick={() => submit({ some: "data" })}>
      Submit
    </button>
  );
}
```

**Note:** `useAction` requires client-side JavaScript and is not progressive enhancement-friendly.

## Submission Tracking

Track action submissions for optimistic updates:

### useSubmission

Get the latest submission for an action:

```jsx
import { useSubmission } from "@solidjs/router";

function MyComponent() {
  const submission = useSubmission(myAction);
  
  return (
    <div>
      {submission()?.pending && <span>Loading...</span>}
      {submission()?.result && <span>Result: {submission().result}</span>}
    </div>
  );
}
```

### useSubmissions

Get all submissions with optional filtering:

```jsx
import { useSubmissions } from "@solidjs/router";

function MyComponent() {
  const submissions = useSubmissions(
    myAction,
    (input) => input.type === "delete" // Filter function
  );
  
  return (
    <ul>
      {submissions().map(sub => (
        <li>
          {sub.pending ? "Pending..." : "Complete"}
          <button onClick={sub.clear}>Clear</button>
          <button onClick={sub.retry}>Retry</button>
        </li>
      ))}
    </ul>
  );
}
```

### Submission Type

```typescript
type Submission<T, U> = {
  readonly input: T;       // Input data
  readonly result?: U;     // Result (after completion)
  readonly pending: boolean; // Is action still running?
  readonly url: string;    // Target URL
  clear: () => void;       // Remove submission
  retry: () => void;       // Retry the action
};
```

## Response Helpers

Helpers for controlling navigation from queries and actions. These are typically thrown to indicate flow control.

### redirect

Redirect to another route:

```jsx
import { redirect } from "@solidjs/router";

const getUser = query(async () => {
  const user = await api.getCurrentUser();
  if (!user) {
    throw redirect("/login");
  }
  return user;
});

// With revalidation
throw redirect("/dashboard", { 
  revalidate: [getUser.key, getPosts.key] 
});
```

### reload

Reload data on current page without navigation:

```jsx
import { reload } from "@solidjs/router";

const updateTodo = action(async (todo) => {
  await api.updateTodo(todo.id, todo);
  throw reload({ 
    revalidate: getTodo.keyFor(todo.id) 
  });
});
```

### Other Response Helpers

```jsx
import { json, error } from "@solidjs/router";

// Return JSON response (for custom handling)
throw json({ message: "Success" }, { status: 200 });

// Throw error response
throw error(new Error("Not found"), { status: 404 });
```

## Complete Example: User Management

```jsx
// routes/users.data.js
import { query, action, redirect, reload } from "@solidjs/router";

export const getUser = query(async (id) => {
  const res = await fetch(`/api/users/${id}`);
  if (!res.ok) throw redirect("/users");
  return res.json();
}, "user");

export const updateUser = action(async (formData) => {
  const id = formData.get("id");
  const data = {
    name: formData.get("name"),
    email: formData.get("email")
  };
  
  await fetch(`/api/users/${id}`, {
    method: "PUT",
    body: JSON.stringify(data)
  });
  
  throw reload({ revalidate: getUser.keyFor(id) });
});

export default async function preloadUser({ params }) {
  void getUser(params.id);
}
```

```jsx
// routes/users/[id].tsx
import { createAsync, useAction } from "@solidjs/router";
import { getUser, updateUser, preloadUser } from "./users.data.js";

export default function UserPage(props) {
  const user = createAsync(() => getUser(props.params.id));
  const submit = useAction(updateUser);
  
  return (
    <Suspense fallback={<Loading />}>
      <h1>{user()?.name}</h1>
      <form action={submit} method="post">
        <input type="hidden" name="id" value={props.params.id} />
        <input type="text" name="name" defaultValue={user()?.name} />
        <input type="email" name="email" defaultValue={user()?.email} />
        <button type="submit">Update</button>
      </form>
    </Suspense>
  );
}

// In router configuration
<Route 
  path="/users/:id" 
  component={UserPage} 
  preload={preloadUser}
/>;
```
