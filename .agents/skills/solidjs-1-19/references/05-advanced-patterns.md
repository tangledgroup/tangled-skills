# Advanced Patterns

This document covers advanced SolidJS patterns including custom hooks, optimization techniques, server-side rendering, and migration strategies.

## Custom Hooks (Primitives)

Custom hooks encapsulate reusable logic with signals and effects.

### Basic Custom Hook

```jsx
import { createSignal, onMount, onCleanup } from "solid-js";

function useLocalStorage(key, initialValue) {
  // Initialize from localStorage
  const [value, setValue] = createSignal(
    () => {
      const stored = localStorage.getItem(key);
      return stored ? JSON.parse(stored) : initialValue;
    }
  );

  // Sync to localStorage on changes
  onMount(() => {
    const storageEvent = (e) => {
      if (e.key === key) {
        setValue(e.newValue ? JSON.parse(e.newValue) : initialValue);
      }
    };
    window.addEventListener("storage", storageEvent);
    onCleanup(() => window.removeEventListener("storage", storageEvent));
  });

  // Update localStorage when value changes
  const setWithValue = (newValue) => {
    setValue(newValue);
    localStorage.setItem(key, JSON.stringify(newValue));
  };

  return [value, setWithValue];
}

// Usage
function Preferences() {
  const [theme, setTheme] = useLocalStorage("theme", "light");

  return (
    <div class={theme}>
      <button onClick={() => setTheme(theme() === "light" ? "dark" : "light")}>
        Toggle Theme
      </button>
    </div>
  );
}
```

### useFetch Hook

```jsx
import { createResource } from "solid-js";

function useFetch(url, options = {}) {
  const [state, setState] = createResource(
    url,
    async (url) => {
      const response = await fetch(url, options);
      if (!response.ok) {
        throw new Error(response.statusText);
      }
      return response.json();
    },
    {
      onError: (error) => console.error("Fetch error:", error),
    }
  );

  const refetch = () => state[1].refetch();

  return {
    data: state[0],
    loading: state.loading,
    error: state.error,
    refetch,
  };
}

// Usage
function UserProfile({ userId }) {
  const { data, loading, error, refetch } = useFetch(
    `/api/users/${userId}`
  );

  return (
    <Suspense fallback={<Loading />}>
      <Show when={error} fallback={data() && (
        <div>
          <h2>{data().name}</h2>
          <button onClick={refetch}>Refresh</button>
        </div>
      )}>
        <p>Error: {error.message}</p>
      </Show>
    </Suspense>
  );
}
```

### useDebounce Hook

```jsx
import { createSignal, createMemo } from "solid-js";

function useDebounce(value, delay = 300) {
  const [debouncedValue, setDebouncedValue] = createSignal(value);

  createMemo(
    () => {
      const timer = setTimeout(() => {
        setDebouncedValue(value());
      }, delay);
      return () => clearTimeout(timer);
    },
    undefined,
    { defer: false }
  );

  return debouncedValue;
}

// Usage
function Search() {
  const [query, setQuery] = createSignal("");
  const debouncedQuery = useDebounce(query, 300);

  const results = createResource(
    debouncedQuery,
    (q) => q && fetch(`/api/search?q=${q}`).then((r) => r.json())
  );

  return (
    <>
      <input
        value={query()}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search..."
      />
      <p>Searching for: {debouncedQuery()}</p>
    </>
  );
}
```

### useEventListener Hook

```jsx
import { onMount, onCleanup } from "solid-js";

function useEventListener(event, handler, element = window) {
  onMount(() => {
    const target = typeof element === "function" ? element() : element;
    target.addEventListener(event, handler);
    onCleanup(() => target.removeEventListener(event, handler));
  });
}

// Usage
function WindowSize() {
  const [size, setSize] = createSignal({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  useEventListener("resize", () => {
    setSize({
      width: window.innerWidth,
      height: window.innerHeight,
    });
  });

  return (
    <div>
      Window size: {size().width} x {size().height}
    </div>
  );
}
```

### useMediaQuery Hook

```jsx
import { createSignal, onMount } from "solid-js";

function useMediaQuery(query) {
  const [matches, setMatches] = createSignal(
    typeof window !== "undefined" ? window.matchMedia(query).matches : false
  );

  onMount(() => {
    const media = window.matchMedia(query);

    const handler = (e) => setMatches(e.matches);
    media.addEventListener("change", handler);
    onCleanup(() => media.removeEventListener("change", handler));
  });

  return matches;
}

// Usage
function ResponsiveLayout() {
  const isMobile = useMediaQuery("(max-width: 768px)");

  return (
    <div class={isMobile() ? "mobile-layout" : "desktop-layout"}>
      {/* Layout content */}
    </div>
  );
}
```

## Optimization Techniques

### Memoization

Use `createMemo` for expensive computations:

```jsx
function ExpensiveList({ items, filter }) {
  // Without memo - runs on every render
  // const filtered = items.filter(i => i.name.includes(filter()));

  // With memo - only runs when items or filter changes
  const filtered = createMemo(() =>
    items.filter((i) => i.name.toLowerCase().includes(filter().toLowerCase()))
  );

  return (
    <For each={filtered()}>
      {(item) => <div>{item.name}</div>}
    </For>
  );
}
```

### Lazy Initialization

Defer expensive computations until first access:

```jsx
const [expensiveValue] = createSignal(
  () => {
    console.log("Expensive computation running...");
    return computeExpensiveValue();
  }
);

// Computation runs only when expensiveValue() is first called
```

### Selective Updates with `on`

Update effects only when specific signals change:

```jsx
const [user, setUser] = createSignal(null);
const [settings, setSettings] = createSignal({});

// Only tracks user, not settings
createEffect(
  on([user], ([newUser]) => {
    console.log("User changed, syncing...");
    syncUser(newUser);
  })
);
```

### Batching Updates

Group related updates for better performance:

```jsx
import { batch } from "solid-js";

function updateAll() {
  batch(() => {
    setA(newValueA);
    setB(newValueB);
    setC(newValueC);
    // All effects run once with final values
  });
}
```

### Avoiding Unnecessary Re-renders

```jsx
// Bad: Creates new function on every render
function Parent() {
  const [count, setCount] = createSignal(0);

  return (
    <Child
      onClick={() => setCount(count() + 1)} // New function each time
    />
  );
}

// Good: Stable function reference
function Parent() {
  const [count, setCount] = createSignal(0);

  const increment = () => setCount(count() + 1);

  return <Child onClick={increment} />;
}
```

## Server-Side Rendering (SSR)

### Basic SSR Setup

```jsx
// server.js
import { renderToString } from "solid-js/web";
import App from "./App";

const html = renderToString(() => <App />);
res.send(`
  <!DOCTYPE html>
  <html>
    <head><title>My App</title></head>
    <body>
      <div id="root">${html}</div>
      <script src="/app.js"></script>
    </body>
  </html>
`);
```

### Client-Side Hydration

```jsx
// client.js
import { hydrate } from "solid-js/web";
import App from "./App";

hydrate(() => <App />, document.getElementById("root"));
```

### SSR with Resources

Resources need special handling for SSR:

```jsx
// With initial data for SSR
const [user] = createResource(
  userId,
  fetchUser,
  { initialValue: null } // Prevents mismatch during hydration
);
```

### Streaming SSR

For better time-to-first-byte:

```jsx
import { renderToStringAsync, Suspense } from "solid-js/web";

async function streamResponse(res) {
  res.writeHead(200, { "Content-Type": "text/html" });

  const html = await renderToStringAsync(
    () => (
      <html>
        <head><title>My App</title></head>
        <body>
          <div id="root">
            <Suspense fallback={<Loading />}>
              <App />
            </Suspense>
          </div>
        </body>
      </html>
    ),
    { context: {} }
  );

  res.end(html);
}
```

## Internationalization (i18n)

### Basic i18n Setup

```jsx
import { createContext, useContext } from "solid-js";

const I18nContext = createContext();

const translations = {
  en: {
    welcome: "Welcome",
    goodbye: "Goodbye",
  },
  es: {
    welcome: "Bienvenido",
    goodbye: "Adiós",
  },
};

function I18nProvider({ locale = "en", children }) {
  const t = (key) => translations[locale][key] || key;

  return (
    <I18nContext.Provider value={{ t, locale }}>
      {children}
    </I18nContext.Provider>
  );
}

function useI18n() {
  return useContext(I18nContext);
}

// Usage
function Greeting() {
  const { t } = useI18n();

  return <h1>{t("welcome")}</h1>;
}
```

## Testing

### Unit Testing Components

```jsx
import { render, fireEvent, screen } from "solid-testing-library";
import Counter from "./Counter";

test("increments count when button is clicked", () => {
  render(() => <Counter />);

  expect(screen.getByText(/count: 0/i)).toBeInTheDocument();

  fireEvent.click(screen.getByText("+"));
  expect(screen.getByText(/count: 1/i)).toBeInTheDocument();
});
```

### Testing with Resources

```jsx
import { render, screen, waitFor } from "solid-testing-library";
import UserProfile from "./UserProfile";

test("loads and displays user data", async () => {
  render(() => <UserProfile userId="123" />);

  expect(screen.getByText(/loading/i)).toBeInTheDocument();

  await waitFor(() =>
    screen.getByText(/user name/i).toBeInTheDocument()
  );

  expect(screen.getByText(/user name/i)).toBeInTheDocument();
});
```

### Testing Custom Hooks

```jsx
import { renderHook } from "solid-testing-library";
import { useLocalStorage } from "./useLocalStorage";

test("useLocalStorage initializes from storage", () => {
  localStorage.setItem("test-key", JSON.stringify("stored-value"));

  const { result } = renderHook(() => useLocalStorage("test-key", "default"));

  expect(result.current[0]()).toBe("stored-value");
});
```

## Migration from React

### Key Differences

| React | SolidJS | Notes |
|-------|---------|-------|
| `useState()` | `createSignal()` | Signals are getter/setter pairs |
| `useEffect()` | `createEffect()` | Effects run immediately by default |
| `useMemo()` | `createMemo()` | Memos are lazy by default |
| `useRef()` | `createRef()` | Similar API |
| `useContext()` | `useContext()` | Same API |
| Props as values | Props as getters | Access with `props.name()` |
| Re-renders | No re-renders | Component functions run once |

### Migration Example

```jsx
// React version
function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    document.title = `Count: ${count}`;
  }, [count]);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>+</button>
    </div>
  );
}

// SolidJS version
function Counter() {
  const [count, setCount] = createSignal(0);

  createEffect(() => {
    document.title = `Count: ${count()}`;
  });

  return (
    <div>
      <p>Count: {count()}</p>
      <button onClick={() => setCount(count() + 1)}>+</button>
    </div>
  );
}
```

### Common Migration Pitfalls

1. **Forgetting to call signals**: `count` → `count()`
2. **Using props directly**: `props.name` → `props.name()`
3. **Expecting re-renders**: Components don't re-run in Solid
4. **Creating effects in loops**: Always create at top level
5. **Mutating state**: Use immutable updates or store APIs

## Performance Tips

1. **Use stores for complex state** - Fine-grained updates prevent unnecessary work
2. **Memoize expensive computations** - `createMemo` caches results
3. **Debounce user input** - Prevent excessive reactivity from rapid changes
4. **Use `equals: false` sparingly** - Default equality check prevents unnecessary updates
5. **Batch related updates** - Use `batch()` for grouped signal changes
6. **Lazy load routes and components** - Reduce initial bundle size
7. **Profile with Solid DevTools** - Identify reactivity issues

## Debugging

### Solid DevTools

Install the browser extension to:
- Inspect component hierarchy
- View signal values
- Track reactivity graph
- Profile performance

### Console Logging in Effects

```jsx
createEffect(() => {
  console.log("Effect ran, count:", count());
});
```

### Checking Signal Tracking

```jsx
const [value, setValue] = createSignal(0);

// This creates a dependency
createEffect(() => console.log(value()));

// This does not (outside tracking scope)
console.log(value());
```
