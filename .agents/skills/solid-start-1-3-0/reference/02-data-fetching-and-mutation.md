# Data Fetching & Mutation

SolidStart extends Solid Router's `query` and `action` APIs with server function support, enabling full-stack data operations.

## Server Functions

Functions marked with `"use server"` run exclusively on the server. Arguments and return values are automatically serialized using [Seroval](https://github.com/lxsmnsyc/seroval).

```tsx
async function getUser(id: string) {
  "use server";
  // Direct database access — never sent to client
  return await db.users.get({ id });
}
```

Supported types include `AbortSignal`, `CustomEvent`, `DOMException`, `Event`, `FormData`, `Headers`, `ReadableStream`, `Request`, `Response`, `URL`, and `URLSearchParams`. `RegExp` is disabled by default.

## Queries

Use `query` from `@solidjs/router` to define fetchable data, then access it with `createAsync`:

```tsx
import { query, createAsync } from "@solidjs/router";

const getPosts = query(async () => {
  "use server";
  return await db.posts.getAll();
}, "posts");

export default function Page() {
  const posts = createAsync(() => getPosts());
  return <ul>{posts()?.map((p) => <li>{p.title}</li>)}</ul>;
}
```

### Loading UI

Wrap data rendering in `<Suspense>` for loading states:

```tsx
import { Suspense } from "solid-js";

export default function Page() {
  const posts = createAsync(() => getPosts());
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ul>{posts()?.map((p) => <li>{p.title}</li>)}</ul>
    </Suspense>
  );
}
```

### Error handling

Use `<ErrorBoundary>` alongside `<Suspense>`:

```tsx
import { ErrorBoundary, Suspense } from "solid-js";

export default function Page() {
  const posts = createAsync(() => getPosts());
  return (
    <ErrorBoundary fallback={<div>Something went wrong!</div>}>
      <Suspense fallback={<div>Loading...</div>}>
        <ul>{posts()?.map((p) => <li>{p.title}</li>)}</ul>
      </Suspense>
    </ErrorBoundary>
  );
}
```

### Preloading data

Export a `route` object with a `preload` function to fetch data before the route renders:

```tsx
import { query, createAsync, type RouteDefinition } from "@solidjs/router";

const getProduct = query(async (id: string) => {
  "use server";
  return await db.products.get(id);
}, "product");

export const route = {
  preload: ({ params }) => getProduct(params.id as string),
} satisfies RouteDefinition;

export default function ProductPage(props) {
  const product = createAsync(() => getProduct(props.params.id as string));
  return <h1>{product()?.name}</h1>;
}
```

### deferStream

When a query may modify headers (redirects, cookies), use `deferStream: true` to prevent streaming before the query resolves:

```tsx
const user = createAsync(() => getCurrentUserQuery(), { deferStream: true });
```

Without this, you may see: `Cannot set headers after they are sent to the client.`

## Actions

Actions handle data mutations, typically triggered by form submissions:

```tsx
import { action } from "@solidjs/router";

const addPost = action(async (formData: FormData) => {
  const title = formData.get("title") as string;
  await db.posts.create({ title });
}, "addPost");

export default function Page() {
  return (
    <form action={addPost} method="post">
      <input name="title" />
      <button>Add Post</button>
    </form>
  );
}
```

### Passing arguments

Use `.with()` to pass additional arguments:

```tsx
const addPost = action(async (userId: number, formData: FormData) => {
  const title = formData.get("title") as string;
  await db.posts.create({ userId, title });
}, "addPost");

// In component:
<form action={addPost.with(userId)} method="post">
```

### Pending UI

Track action state with `useSubmission`:

```tsx
import { action, useSubmission } from "@solidjs/router";

const addPost = action(async (formData: FormData) => {
  // ...
}, "addPost");

export default function Page() {
  const submission = useSubmission(addPost);
  return (
    <form action={addPost} method="post">
      <input name="title" />
      <button disabled={submission.pending}>
        {submission.pending ? "Adding..." : "Add Post"}
      </button>
    </form>
  );
}
```

### Error handling

Access `submission.error` for error states:

```tsx
import { Show } from "solid-js";
import { action, useSubmission } from "@solidjs/router";

const addPost = action(async (formData: FormData) => {
  // ...
}, "addPost");

export default function Page() {
  const submission = useSubmission(addPost);
  return (
    <form action={addPost} method="post">
      <input name="title" />
      <button>Add Post</button>
      <Show when={submission.error}>
        <p>Error: {submission.error}</p>
      </Show>
    </form>
  );
}
```

## Server Functions with Actions

Combine `"use server"` with actions for server-only mutations:

```tsx
import { action, redirect } from "@solidjs/router";
import { useSession } from "vinxi/http";

const logoutAction = action(async () => {
  "use server";
  const session = await useSession({
    password: process.env.SESSION_SECRET as string,
    name: "session",
  });

  if (session.data.sessionId) {
    await session.clear();
    await db.sessions.delete({ id: session.data.sessionId });
  }

  throw redirect("/");
}, "logout");
```

## Single-Flight Mutations

SolidStart's unique feature: when an action updates data and the affected query is preloaded, both the mutation result and fresh data are returned in a **single HTTP response**.

Requirements:
1. The action must use a server function (`"use server"`)
2. The affected query must be preloaded on the route

```tsx title="src/routes/products/[id].tsx"
import { action, query, createAsync, type RouteDefinition } from "@solidjs/router";

const updateProductAction = action(async (id: string, formData: FormData) => {
  "use server";
  const name = formData.get("name")?.toString();
  await db.products.update(id, { name });
}, "updateProduct");

const getProductQuery = query(async (id: string) => {
  "use server";
  return await db.products.get(id);
}, "product");

export const route = {
  preload: ({ params }) => getProductQuery(params.id as string),
} satisfies RouteDefinition;

export default function ProductDetail(props) {
  const product = createAsync(() => getProductQuery(props.params.id as string));

  return (
    <div>
      <p>Name: {product()?.name}</p>
      <form action={updateProductAction.with(props.params.id as string)} method="post">
        <input name="name" placeholder="New name" />
        <button>Save</button>
      </form>
    </div>
  );
}
```

When the form submits, a single POST request updates the product and streams back the fresh data — no separate refetch needed.

## Protected Routes

Combine server functions with queries to protect routes:

```tsx
const getPrivatePosts = query(async function () {
  "use server";
  const user = await getUser();
  if (!user) {
    throw redirect("/login");
  }
  return db.getPosts({ userId: user.id, private: true });
}, "privatePosts");

export default function Page() {
  const posts = createAsync(() => getPrivatePosts(), { deferStream: true });
  // ...
}
```

Use `deferStream: true` to ensure the redirect resolves before streaming begins.

## Returning Responses from Server Functions

Server functions can return Response objects using solid-router helpers:

```tsx
import { json, redirect } from "@solidjs/router";

export async function getUser() {
  "use server";
  const session = await getSession();
  const userId = session.data.userId;
  if (!userId) return redirect("/login");

  const user = await db.user.findUnique({ where: { id: userId } });
  if (!user) return redirect("/login");
  return user;
}
```

The `redirect` and `reload` helpers return `never`, so TypeScript infers the function can only return its data type.
