# Control Flow Components

SolidJS provides built-in control flow components for conditional rendering, lists, portals, and error handling.

## Show

Conditional rendering with `<Show>`:

```jsx
import { Show } from "solid-js";

function UserGreeting({ user }) {
  return (
    <Show when={user}>
      <p>Welcome back, {user.name}!</p>
    </Show>
  );
}
```

### Show with Fallback

```jsx
function UserStatus({ user }) {
  return (
    <Show
      when={user}
      fallback={<p>Please log in</p>}
    >
      <p>Welcome, {user.name}!</p>
    </Show>
  );
}
```

### Show with Deferred Mounting

```jsx
import { Show } from "solid-js";

function LazyComponent({ show }) {
  return (
    <Show
      when={show}
      fallback={<LoadingSpinner />}
      deferred={true} // Children mount only when condition becomes true
    >
      <ExpensiveComponent />
    </Show>
  );
}
```

### Nested Show Components

```jsx
function ContentDisplay({ status, data }) {
  return (
    <Show when={status === "loading"} fallback={
      <Show when={status === "error"} fallback={
        <Show when={data} fallback={<EmptyState />}>
          <DataList data={data} />
        </Show>
      }>
        <ErrorMessage />
      </Show>
    }>
      <LoadingSpinner />
    </Show>
  );
}
```

## For

Rendering lists with `<For>`:

### Basic List Rendering

```jsx
import { For } from "solid-js";

function TodoList({ todos }) {
  return (
    <ul>
      <For each={todos}>
        {(todo) => (
          <li>
            <span>{todo.text}</span>
            <button onClick={() => todo.completed = !todo.completed}>
              {todo.completed ? "Undo" : "Complete"}
            </button>
          </li>
        )}
      </For>
    </ul>
  );
}
```

### For with Index

```jsx
function NumberedList({ items }) {
  return (
    <ol>
      <For each={items}>
        {(item, index) => (
          <li>
            <span>{index() + 1}. {item.text}</span>
          </li>
        )}
      </For>
    </ol>
  );
}
```

### For with Fallback

```jsx
function EmptyList({ items }) {
  return (
    <For
      each={items}
      fallback={<p>No items in list</p>}
    >
      {(item) => <div>{item.name}</div>}
    </For>
  );
}
```

### For with Keys

For lists where items can be reordered or filtered:

```jsx
function TagList({ tags }) {
  return (
    <For
      each={tags}
      fallback={<p>No tags</p>}
    >
      {(tag) => (
        <span class="tag">{tag.name}</span>
      )}
    </For>
  );
}
```

### Dynamic Lists

```jsx
import { createSignal, For } from "solid-js";

function CounterList() {
  const [counters, setCounters] = createSignal([
    { id: 1, value: 0 },
    { id: 2, value: 0 },
  ]);

  const increment = (id) => {
    setCounters(
      counters().map((c) =>
        c.id === id ? { ...c, value: c.value + 1 } : c
      )
    );
  };

  return (
    <For each={counters()}>
      {(counter) => (
        <div>
          <span>Counter {counter.id}: {counter.value}</span>
          <button onClick={() => increment(counter.id)}>+</button>
        </div>
      )}
    </For>
  );
}
```

## Index

Index provides reactive access to array indices with better performance for certain operations:

### Basic Index Usage

```jsx
import { Index } from "solid-js";

function NumberedList({ items }) {
  return (
    <ol>
      <Index each={items}>
        {(item, index) => (
          <li>
            <span>{index + 1}. {item()}</span>
          </li>
        )}
      </Index>
    </ol>
  );
}
```

### Index vs For

Use `Index` when:
- You need the index for styling or logic
- List order matters and items are reordered
- You're doing complex list manipulations

Use `For` when:
- Simple iteration without index access
- Better performance for large static lists

```jsx
// Using Index - index is a number, item() is a getter
<Index each={items}>
  {(item, index) => (
    <li class={index % 2 === 0 ? "even" : "odd"}>
      {item().name}
    </li>
  )}
</Index>

// Using For - index() is a getter, item is the value directly
<For each={items}>
  {(item, index) => (
    <li>{item.name} (position: {index()})</li>
  )}
</For>
```

### Index with Array Operations

```jsx
import { createSignal, Index } from "solid-js";

function SortableList() {
  const [items, setItems] = createSignal(["Apple", "Banana", "Cherry"]);

  const sortItems = () => {
    setItems([...items()].sort());
  };

  return (
    <>
      <button onClick={sortItems}>Sort</button>
      <Index each={items()}>
        {(item, index) => (
          <li>
            <span>{index + 1}. {item()}</span>
          </li>
        )}
      </Index>
    </>
  );
}
```

## Portal

Rendering children into a different DOM location:

### Basic Portal

```jsx
import { Portal } from "solid-js";

function Modal({ isOpen, onClose, children }) {
  return (
    <Show when={isOpen}>
      <Portal mountTo="#modal-root">
        <div class="modal-overlay" onClick={onClose}>
          <div class="modal-content" onClick={(e) => e.stopPropagation()}>
            {children}
            <button onClick={onClose}>Close</button>
          </div>
        </div>
      </Portal>
    </Show>
  );
}
```

### Portal to Document Body

```jsx
function Tooltip({ text, children }) {
  return (
    <div class="tooltip-wrapper">
      {children}
      <Portal mountTo=document.body>
        <div class="tooltip">{text}</div>
      </Portal>
    </div>
  );
}
```

### Portal with Dynamic Mount Point

```jsx
function ContextualMenu({ target, items }) {
  const [mountPoint, setMountPoint] = createSignal(null);

  onMount(() => {
    // Find appropriate mount point
    setMountPoint(document.querySelector("#context-menus") || document.body);
  });

  return (
    <Portal mountTo={mountPoint()}>
      <div class="context-menu">
        <For each={items}>
          {(item) => (
            <button onClick={item.action}>{item.label}</button>
          )}
        </For>
      </div>
    </Portal>
  );
}
```

## Suspense

Handling asynchronous data loading:

### Basic Suspense

```jsx
import { Suspense } from "solid-js";

function UserProfile({ userId }) {
  const user = createResource(() => userId, fetchUser);

  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Show when={user()[0]}>
        <div>
          <h2>{user()[0].name}</h2>
          <p>{user()[0].bio}</p>
        </div>
      </Show>
    </Suspense>
  );
}
```

### Suspense with Multiple Resources

```jsx
function Dashboard() {
  const [user, getUser] = createResource(fetchUser);
  const [posts, getPosts] = createResource(fetchPosts);
  const [stats, getStats] = createResource(fetchStats);

  return (
    <Suspense fallback={<DashboardSkeleton />}>
      <UserProfile user={user} />
      <PostList posts={posts} />
      <StatCards stats={stats} />
    </Suspense>
  );
}
```

### Suspense with Nested Boundaries

```jsx
function Page() {
  const critical = createResource(fetchCriticalData);
  const nonCritical = createResource(fetchNonCriticalData);

  return (
    <div>
      {/* Critical content has its own fallback */}
      <Suspense fallback={<CriticalLoading />}>
        <CriticalContent data={critical} />
      </Suspense>

      {/* Non-critical content waits or shows placeholder */}
      <Suspense fallback={null}>
        <NonCriticalContent data={nonCritical} />
      </Suspense>
    </div>
  );
}
```

### Suspense with `revealOrder`

Control loading reveal order:

```jsx
function MultiStepForm() {
  const step1 = createResource(fetchStep1);
  const step2 = createResource(fetchStep2);
  const step3 = createResource(fetchStep3);

  return (
    <>
      {/* Steps reveal in order */}
      <Suspense fallback={<StepLoading />} revealOrder="ordered">
        <Step1 data={step1} />
        <Step2 data={step2} />
        <Step3 data={step3} />
      </Suspense>

      {/* Steps reveal as they load */}
      <Suspense fallback={<StepLoading />} revealOrder="default">
        <Step1 data={step1} />
        <Step2 data={step2} />
        <Step3 data={step3} />
      </Suspense>
    </>
  );
}
```

## ErrorBoundary

Catching and handling rendering errors:

### Basic Error Boundary

```jsx
import { ErrorBoundary } from "solid-js";

function App() {
  return (
    <ErrorBoundary
      fallback={(error) => (
        <div class="error-boundary">
          <h2>Something went wrong</h2>
          <pre>{error.message}</pre>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      )}
    >
      <RiskyComponent />
    </ErrorBoundary>
  );
}
```

### Error Boundary with Reset

```jsx
function RecoverableComponent() {
  const [retryCount, setRetryCount] = createSignal(0);

  return (
    <ErrorBoundary
      fallback={(error, reset) => (
        <div>
          <p>Error: {error.message}</p>
          <button onClick={() => {
            setRetryCount(retryCount() + 1);
            reset();
          }}>
            Retry ({retryCount()})
          </button>
        </div>
      )}
    >
      <UnstableComponent />
    </ErrorBoundary>
  );
}
```

### Nested Error Boundaries

```jsx
function App() {
  return (
    <ErrorBoundary fallback={(error) => <FullPageError error={error} />}>
      <Layout>
        <ErrorBoundary fallback={(error) => <SectionError error={error} />}>
          <Sidebar />
        </ErrorBoundary>
        <ErrorBoundary fallback={(error) => <ContentError error={error} />}>
          <MainContent />
        </ErrorBoundary>
      </Layout>
    </ErrorBoundary>
  );
}
```

## Match/Switch

Alternative conditional rendering:

### Basic Match/Switch

```jsx
import { Match, Switch } from "solid-js";

function StatusDisplay({ status }) {
  return (
    <Switch>
      <Match when={status === "loading"}>
        <LoadingSpinner />
      </Match>
      <Match when={status === "success"}>
        <SuccessMessage />
      </Match>
      <Match when={status === "error"}>
        <ErrorMessage />
      </Match>
      <Match>
        <UnknownStatus />
      </Match>
    </Switch>
  );
}
```

### Match with Expressions

```jsx
function AgeGroup({ age }) {
  return (
    <Switch>
      <Match when={age < 13}>Child</Match>
      <Match when={age < 20}>Teenager</Match>
      <Match when={age < 65}>Adult</Match>
      <Match>Senior</Match>
    </Switch>
  );
}
```

## Dynamic Components

Rendering components dynamically:

### Basic Dynamic

```jsx
import { Dynamic } from "solid-js";

function ComponentSwitcher({ componentName }) {
  const components = {
    Button,
    Input,
    Card,
  };

  return <Dynamic component={components[componentName]} />;
}
```

### Dynamic with Props

```jsx
function ElementRenderer({ type, props }) {
  return <Dynamic component={type} {...props} />;
}

// Usage
<ElementRenderer
  type="button"
  props={{ onClick: handleClick, children: "Click" }}
/>;
```

### Dynamic Components with Resources

```jsx
function PluginSystem({ pluginName }) {
  const [Plugin] = createResource(
    pluginName,
    (name) => import(`./plugins/${name}`).then(m => m.default)
  );

  return (
    <Suspense fallback={<Loading />}>
      <Dynamic component={Plugin()[0]} />
    </Suspense>
  );
}
```

## Control Flow Best Practices

1. **Use `For` for simple lists** - Better performance for static iteration
2. **Use `Index` when you need indices** - More efficient index access
3. **Wrap async content in `Suspense`** - Always provide fallbacks
4. **Use `Portal` for overlays** - Modals, tooltips, popovers
5. **Add `ErrorBoundary` around risky components** - Prevent app crashes
6. **Prefer `Show` over ternaries for complex conditions** - Better performance with deferred mounting
