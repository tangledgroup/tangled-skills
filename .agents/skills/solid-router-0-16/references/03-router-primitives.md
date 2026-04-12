# Solid Router Primitives

This reference covers all router hooks and primitives for accessing route context, navigation, and state in Solid Router v0.16.

## useParams

Returns a reactive store-like object containing the current route's path parameters.

```jsx
import { useParams } from "@solidjs/router";

function UserPage() {
  const params = useParams();
  
  // Access parameters reactively
  const userId = () => params.id;
  
  return <h1>User ID: {userId()}</h1>;
}
```

### Reactive Updates

Parameters update reactively when route changes:

```jsx
function DynamicContent() {
  const params = useParams();
  
  // This creates a reactive subscription to params.id
  const title = createMemo(() => `Viewing ${params.id}`);
  
  return <h1>{title()}</h1>;
}
```

### Type Safety with TypeScript

```tsx
import { useParams } from "@solidjs/router";

// For route /users/:id
function UserPage() {
  const params = useParams<{ id: string }>();
  // params.id is typed as string
  
  return <h1>User: {params.id}</h1>;
}

// Using 'in' operator (v0.15.4+)
if ("id" in params) {
  console.log(params.id);
}
```

## useNavigate

Returns a navigation function for programmatic routing.

```jsx
import { useNavigate } from "@solidjs/router";

function LoginForm() {
  const navigate = useNavigate();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    const success = await authenticate();
    if (success) {
      navigate("/dashboard");
    }
  };
  
  return <form onSubmit={handleSubmit}>...</form>;
}
```

### Navigate Options

```jsx
const navigate = useNavigate();

// Replace current history entry (don't add new entry)
navigate("/login", { replace: true });

// Disable scroll-to-top
navigate("/users", { scroll: false });

// Pass state to history
navigate("/checkout", { 
  state: { from: "cart", items: cartItems } 
});

// Resolve path relative to current route (default: true)
navigate("../settings", { resolve: true });
navigate("/settings", { resolve: false }); // Absolute path
```

### Options Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `resolve` | boolean | true | Resolve path against current route |
| `replace` | boolean | false | Replace history entry instead of push |
| `scroll` | boolean | true | Scroll to top after navigation |
| `state` | any | undefined | State object for history API |

**Note:** State is serialized using the structured clone algorithm, which doesn't support all object types (no functions, symbols, etc.).

## useLocation

Returns a reactive location object with URL information.

```jsx
import { useLocation } from "@solidjs/router";

function Breadcrumbs() {
  const location = useLocation();
  
  return (
    <nav>
      <span>You are at: {location.pathname}</span>
      <span>Search: {location.search}</span>
      <span>Hash: {location.hash}</span>
    </nav>
  );
}
```

### Location Properties

| Property | Type | Description |
|----------|------|-------------|
| `pathname` | string | Path portion of URL |
| `search` | string | Query string including `?` |
| `hash` | string | Hash portion including `#` |
| `query` | object | Parsed query parameters |
| `state` | any | State from history API |
| `key` | string | Unique navigation key |

### Parsing Pathname

```jsx
import { useLocation, parsePath } from "@solidjs/router";

function RouteDebugger() {
  const location = useLocation();
  
  const parsed = createMemo(() => parsePath(location.pathname));
  // Returns { pathname: string, search: string, hash: string }
  
  return <pre>{JSON.stringify(parsed(), null, 2)}</pre>;
}
```

## useSearchParams

Returns a tuple with reactive search params and a setter function.

```jsx
import { useSearchParams } from "@solidjs/router";

function PaginatedList() {
  const [searchParams, setSearchParams] = useSearchParams();
  
  const currentPage = createMemo(() => 
    parseInt(searchParams.page) || 1
  );
  
  const nextPage = () => {
    setSearchParams({ 
      page: String(currentPage() + 1) 
    });
  };
  
  return (
    <div>
      <span>Page: {currentPage()}</span>
      <button onClick={nextPage}>Next</button>
    </div>
  );
}
```

### Setter Behavior

```jsx
const [searchParams, setSearchParams] = useSearchParams();

// Merge with existing params
setSearchParams({ page: "2" }); 
// ?foo=bar&page=2 (if foo=bar was already present)

// Remove a param (empty string, null, or undefined)
setSearchParams({ foo: "" });
setSearchParams({ bar: null });
setSearchParams({ baz: undefined });

// Multiple params at once
setSearchParams({ page: "1", sort: "desc", filter: "active" });

// With navigation options
setSearchParams(
  { page: "2" },
  { replace: true, scroll: false }
);
```

### Array Values (v0.14.10+)

```jsx
const [searchParams, setSearchParams] = useSearchParams();

// Set array value
setSearchParams({ tags: ["react", "solidjs"] });
// Results in: ?tags=react&tags=solidjs

// Access array values
const tags = searchParams.tags; // May be string or string[]
```

### Type Safety

```tsx
import { useSearchParams } from "@solidjs/router";

function FilteredList() {
  const [searchParams, setSearchParams] = useSearchParams<{
    page: string;
    sort: string;
    filter: string;
  }>();
  
  // searchParams.page is typed
  return <span>Page: {searchParams.page}</span>;
}
```

## useIsRouting

Returns a signal indicating whether a route transition is in progress.

```jsx
import { useIsRouting } from "@solidjs/router";

function PageContent() {
  const isRouting = useIsRouting();
  
  return (
    <div classList={{ 
      "opacity-50": isRouting(),
      "transition-opacity": true 
    }}>
      <MyContent />
    </div>
  );
}
```

### Loading States

```jsx
function App() {
  const isRouting = useIsRouting();
  
  return (
    <>
      {isRouting() && <GlobalLoadingOverlay />}
      <main>
        <Routes />
      </main>
    </>
  );
}
```

### With Suspense

```jsx
function Page() {
  const isRouting = useIsRouting();
  
  return (
    <Suspense fallback={isRouting() ? <StaleContent /> : <Loading />}>
      <ExpensiveComponent />
    </Suspense>
  );
}
```

## useMatch

Creates a memo that returns match information if the current path matches a given path.

```jsx
import { useMatch } from "@solidjs/router";

function CustomLink(props) {
  const match = useMatch(() => props.href);
  
  return (
    <a classList={{ 
      active: Boolean(match()),
      "font-bold": match()
    }}>
      {props.children}
    </a>
  );
}
```

### Match Result Structure

```jsx
const match = useMatch(() => "/users");

if (match()) {
  // match() returns object with:
  // - params: route parameters
  // - pathname: matched pathname
  // - ...other match info
}
```

## useCurrentMatches

Returns all matches for the current route, useful for breadcrumbs or multi-level data.

```jsx
import { useCurrentMatches } from "@solidjs/router";

function Breadcrumbs() {
  const matches = useCurrentMatches();
  
  const crumbs = createMemo(() => 
    matches().map(m => m.route.info.breadcrumb)
  );
  
  return (
    <nav>
      {crumbs().map((crumb, i) => (
        <span key={i}>{crumb} / </span>
      ))}
    </nav>
  );
}
```

### Match Object Structure

```typescript
type RouteMatch = {
  route: {
    path: string;
    component: Component;
    info: any; // Custom route metadata
  };
  params: Record<string, string>;
  pathname: string;
  // ...additional properties
};
```

### Storing Metadata on Routes

```jsx
<Route 
  path="/users" 
  component={Users}
  info={{ breadcrumb: "Users", title: "User List" }}
>
  <Route 
    path="/:id" 
    component={User}
    info={{ breadcrumb: "User Detail", title: "User Details" }}
  />
</Route>

// Access in component
function PageHeader() {
  const matches = useCurrentMatches();
  const title = createMemo(() => 
    matches().at(-1)?.route.info.title || "Home"
  );
  return <h1>{title()}</h1>;
}
```

## usePreloadRoute

Returns a function to manually preload routes.

```jsx
import { usePreloadRoute } from "@solidjs/router";

function QuickLinks() {
  const preload = usePreloadRoute();
  
  const handleHover = (path) => {
    preload(path, { preloadData: true });
  };
  
  return (
    <ul>
      <li onMouseEnter={() => handleHover("/users")}>Users</li>
      <li onMouseEnter={() => handleHover("/settings")}>Settings</li>
    </ul>
  );
}
```

### Preload Options

```jsx
const preload = usePreloadRoute();

// Basic preload
preload("/users/123");

// With data preloading
preload("/users/123", { preloadData: true });

// This is what <A> components do automatically on hover
```

## useBeforeLeave

Registers a handler that runs before leaving the current route.

```jsx
import { useBeforeLeave } from "@solidjs/router";

function EditForm() {
  const [isDirty, setIsDirty] = createSignal(false);
  
  useBeforeLeave((event) => {
    if (isDirty() && !event.defaultPrevented) {
      // Prevent navigation
      event.preventDefault();
      
      // Show confirmation dialog
      if (window.confirm("Discard unsaved changes?")) {
        // User confirmed, retry navigation (force=true skips handlers again)
        event.retry(true);
      }
    }
  });
  
  return (
    <form onChange={() => setIsDirty(true)}>
      {/* form fields */}
    </form>
  );
}
```

### Event Object

```typescript
type BeforeLeaveEventArgs = {
  from: Location;           // Current location
  to: string | number;      // Target path
  options: NavigateOptions; // Navigation options
  preventDefault: () => void; // Block navigation
  defaultPrevented: boolean; // True if any handler called preventDefault
  retry: (force?: boolean) => void; // Retry navigation
};
```

### Multiple Handlers

```jsx
function ParentComponent() {
  useBeforeLeave((event) => {
    console.log("Parent leave handler");
    if (shouldBlock()) {
      event.preventDefault();
      // ...handle blocking
    }
  });
  
  return <ChildComponent />;
}

function ChildComponent() {
  useBeforeLeave((event) => {
    console.log("Child leave handler");
    // All handlers run, any can block
  });
}
```

## useAction

Wraps an action for programmatic invocation outside forms.

```jsx
import { useAction } from "@solidjs/router";

function DeleteButton({ id }) {
  const deleteItem = useAction(deleteItemAction);
  
  return (
    <button onClick={() => deleteItem(id)}>
      Delete
    </button>
  );
}
```

**Note:** Requires client-side JavaScript. For progressive enhancement, use `<form action={...}>` instead.

## Component Context Access

All primitives require being inside a Router component:

```jsx
// This will throw error - no router context
function Broken() {
  const params = useParams(); // Error!
}

// Correct usage
<Router>
  <Route path="/" component={WorkingComponent} />
</Router>

function WorkingComponent() {
  const params = useParams(); // Works!
}
```
