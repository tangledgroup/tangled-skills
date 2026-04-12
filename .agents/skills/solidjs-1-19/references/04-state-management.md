# State Management

This document covers SolidJS state management patterns including Stores, Context, and complex state architectures.

## Stores

Stores provide fine-grained reactivity for complex nested state objects.

### Creating Stores

```jsx
import { createStore } from "solid-js/store";

// Create a store with initial state
const [state, setState] = createStore({
  user: {
    name: "Alice",
    email: "alice@example.com",
    settings: {
      theme: "dark",
      notifications: true,
    },
  },
  items: [],
});
```

### Reading Store Values

```jsx
// Access store values directly (no parentheses needed)
console.log(state.user.name); // "Alice"
console.log(state.user.settings.theme); // "dark"

// Use in JSX
<div>{state.user.name}</div>
```

### Updating Stores

#### Setting Primitive Values

```jsx
// Update a primitive property
setState("user", "name", "Bob");

// Or using object syntax
setState({ user: { name: "Bob" } });
```

#### Updating Nested Properties

```jsx
// Update nested property
setState("user", "settings", "theme", "light");

// Multiple levels at once
setState("user", "settings", { theme: "light", notifications: false });
```

#### Using Proxies

```jsx
// Set entire object
setState("user", { name: "Charlie", email: "charlie@example.com" });
```

### Array Operations

#### Adding Items

```jsx
// Add to array
setState("items", "push", { id: 1, name: "Item 1" });

// Or using splice
setState("items", "splice", 0, 0, { id: 1, name: "First Item" });
```

#### Updating Array Items

```jsx
// Update item by index
setState("items", 0, "name", "Updated Name");

// Replace entire item at index
setState("items", 1, { id: 2, name: "New Item" });
```

#### Removing Items

```jsx
// Remove item at index
setState("items", "splice", 2, 1);

// Filter items (creates new array)
setState("items", items().filter(item => item.active));
```

### Store Spread Operators

For immutable-style updates:

```jsx
// Spread existing properties
setState("user", "settings", { ...state.user.settings, theme: "light" });

// This is equivalent to:
setState("user", "settings", "theme", "light");
```

### Production Mode Stores

In production, stores use fine-grained tracking automatically:

```jsx
import { createStore, produce } from "solid-js/store";

const [state, setState] = createStore({ count: 0 });

// Using produce for complex updates
setState(produce((draft) => {
  draft.count += 1;
  draft.user.name = "Updated";
}));
```

## Store Best Practices

### When to Use Stores

Use stores when:
- Managing complex nested state objects
- Need fine-grained updates without re-rendering entire components
- Working with arrays that need frequent modifications
- Building form state with many fields
- Creating global or shared state

### When to Use Signals

Use signals when:
- Simple primitive values (numbers, strings, booleans)
- Single values that change together
- Component-local state
- Performance-critical simple counters

```jsx
// Good: Signal for simple counter
const [count, setCount] = createSignal(0);

// Good: Store for complex user object
const [user, setUser] = createStore({
  profile: { name: "", email: "" },
  preferences: { theme: "light", language: "en" },
});
```

## Context

Context provides a way to share values across the component tree without prop drilling.

### Creating Context

```jsx
import { createContext, createStore } from "solid-js";

// Create a context with default value
const ThemeContext = createContext();

// Provider component
function ThemeProvider({ children }) {
  const [theme, setTheme] = createSignal("light");

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}
```

### Using Context

```jsx
import { useContext } from "solid-js";

function ThemedComponent() {
  const { theme, setTheme } = useContext(ThemeContext);

  return (
    <div class={theme}>
      <p>Current theme: {theme}</p>
      <button onClick={() => setTheme(theme === "light" ? "dark" : "light")}>
        Toggle Theme
      </button>
    </div>
  );
}
```

### Context with Stores

For complex context values, use stores:

```jsx
import { createContext, useContext, createStore } from "solid-js";

const UserContext = createContext();

function UserProvider({ children }) {
  const [userState, setUserState] = createStore({
    user: null,
    loading: false,
    error: null,
  });

  const login = async (credentials) => {
    setUserState("loading", true);
    try {
      const user = await authenticate(credentials);
      setUserState({ user, loading: false });
    } catch (error) {
      setUserState({ error: error.message, loading: false });
    }
  };

  const logout = () => {
    setUserState({ user: null, error: null });
  };

  return (
    <UserContext.Provider value={{ userState, login, logout }}>
      {children}
    </UserContext.Provider>
  );
}
```

### Using Store Context

```jsx
function UserProfile() {
  const { userState, logout } = useContext(UserContext);

  return (
    <Show when={userState.loading} fallback={
      <Show when={userState.error} fallback={
        userState.user && (
          <div>
            <h2>Welcome, {userState.user.name}</h2>
            <button onClick={logout}>Logout</button>
          </div>
        )
      }>
        <p>Error: {userState.error}</p>
      </Show>
    }>
      <LoadingSpinner />
    </Show>
  );
}
```

### Multiple Contexts

```jsx
function App() {
  return (
    <ThemeProvider>
      <UserProvider>
        <AppLayout />
      </UserProvider>
    </ThemeProvider>
  );
}
```

## Resource API

Resources handle asynchronous data fetching with built-in caching and loading states.

### Basic Resource

```jsx
import { createResource } from "solid-js";

function UserProfile({ userId }) {
  // Fetch user data
  const [user, getUser] = createResource(
    userId,
    (id) => fetch(`/api/users/${id}`).then((res) => res.json())
  );

  return (
    <Suspense fallback={<Loading />}>
      <Show when={user.loading} fallback={
        <Show when={user.error} fallback={
          user() && (
            <div>
              <h2>{user().name}</h2>
              <p>{user().email}</p>
            </div>
          )
        }>
          <p>Error: {user.error.message}</p>
        </Show>
      }>
        <LoadingSpinner />
      </Show>
    </Suspense>
  );
}
```

### Resource with Source

Resource that tracks a signal:

```jsx
function SearchResults() {
  const [query, setQuery] = createSignal("");

  // Debounced search query
  const debouncedQuery = createMemo(
    () => query(),
    undefined,
    { timeout: 300 }
  );

  // Resource that refetches when query changes
  const [results] = createResource(
    debouncedQuery,
    (q) => q && fetch(`/api/search?q=${q}`).then((res) => res.json())
  );

  return (
    <>
      <input
        value={query()}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search..."
      />
      <Suspense fallback={<Loading />}>
        <For each={results()}>
          {(item) => <div>{item.name}</div>}
        </For>
      </Suspense>
    </>
  );
}
```

### Manual Resource Control

```jsx
function DataFetcher() {
  const [data, fetchData] = createResource(fetchData);

  // Manually refetch
  const handleRefresh = () => {
    fetchData.refetch();
  };

  return (
    <>
      <button onClick={handleRefresh}>Refresh</button>
      <Suspense fallback={<Loading />}>
        <div>{data()?.value}</div>
      </Suspense>
    </>
  );
}
```

### Resource Options

```jsx
const [data] = createResource(
  source,
  loader,
  {
    initialValue: {}, // Default value before loading
    hydrate: true, // Enable SSR hydration
    onError: (error) => console.error(error),
    onPending: () => console.log("Loading..."),
  }
);
```

## State Management Patterns

### Local Component State

```jsx
function Counter() {
  const [count, setCount] = createSignal(0);

  return (
    <div>
      <p>Count: {count()}</p>
      <button onClick={() => setCount(count() + 1)}>+</button>
    </div>
  );
}
```

### Lifted State

When multiple components need shared state:

```jsx
function Parent() {
  const [value, setValue] = createSignal("");

  return (
    <>
      <Input value={value} onChange={setValue} />
      <Display value={value} />
    </>
  );
}

function Input({ value, onChange }) {
  return (
    <input
      type="text"
      value={value()}
      onChange={(e) => onChange(e.target.value)}
    />
  );
}

function Display({ value }) {
  return <p>You typed: {value()}</p>;
}
```

### Form State with Stores

```jsx
function ContactForm() {
  const [form, setForm] = createStore({
    name: "",
    email: "",
    message: "",
    submitting: false,
    error: null,
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setForm("submitting", true);

    try {
      await submitForm({
        name: form.name,
        email: form.email,
        message: form.message,
      });
      // Reset form
      setForm({ name: "", email: "", message: "", submitting: false });
    } catch (error) {
      setForm({ error: error.message, submitting: false });
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {form.error && <div class="error">{form.error}</div>}

      <input
        type="text"
        name="name"
        value={form.name}
        onChange={(e) => setForm("name", e.target.value)}
        placeholder="Name"
        required
      />

      <input
        type="email"
        name="email"
        value={form.email}
        onChange={(e) => setForm("email", e.target.value)}
        placeholder="Email"
        required
      />

      <textarea
        name="message"
        value={form.message}
        onChange={(e) => setForm("message", e.target.value)}
        placeholder="Message"
        required
      />

      <button type="submit" disabled={form.submitting}>
        {form.submitting ? "Sending..." : "Send"}
      </button>
    </form>
  );
}
```

### Global State with Context and Store

```jsx
// store.js
import { createContext, createStore } from "solid-js";

const AppContext = createContext();

export function AppProvider({ children }) {
  const [state, setState] = createStore({
    user: null,
    theme: "light",
    cart: [],
    notifications: [],
  });

  const actions = {
    setUser: (user) => setState("user", user),
    setTheme: (theme) => setState("theme", theme),
    addToCart: (item) => setState("cart", "push", item),
    addNotification: (notification) =>
      setState("notifications", "push", notification),
  };

  return (
    <AppContext.Provider value={{ state, actions }}>
      {children}
    </AppContext.Provider>
  );
}

export const useApp = () => useContext(AppContext);
```

### Using Global State

```jsx
import { useApp } from "./store";

function Header() {
  const { state, actions } = useApp();

  return (
    <header>
      <Show when={state.user} fallback={<LoginButton />}>
        <span>Hello, {state.user.name}</span>
        <button onClick={() => actions.setUser(null)}>Logout</button>
      </Show>

      <button onClick={() => actions.setTheme(state.theme === "light" ? "dark" : "light")}>
        Toggle Theme
      </button>

      <span>Cart: {state.cart.length} items</span>
    </header>
  );
}
```

## State Management Best Practices

1. **Start local** - Keep state in the component that needs it
2. **Lift when necessary** - Move state up when multiple components need it
3. **Use context for global state** - Avoid prop drilling
4. **Prefer stores for complex state** - Fine-grained updates
5. **Use resources for async data** - Built-in caching and loading states
6. **Derive when possible** - Use memos to compute derived values
7. **Normalize state shape** - Flatten nested structures when possible
