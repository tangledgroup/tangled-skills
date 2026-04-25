# Component Patterns

This document covers component creation, props, events, refs, and lifecycle patterns in SolidJS.

## Creating Components

### Function Components

Components are JavaScript functions that return JSX:

```jsx
import { createSignal } from "solid-js";

function Welcome({ name }) {
  return <h1>Hello, {name}!</h1>;
}

export default Welcome;
```

### Component with State

```jsx
function Counter() {
  const [count, setCount] = createSignal(0);

  return (
    <div>
      <p>Count: {count()}</p>
      <button onClick={() => setCount(count() + 1)}>+</button>
      <button onClick={() => setCount(count() - 1)}>-</button>
    </div>
  );
}
```

## Props

Props pass data from parent to child components.

### Receiving Props

```jsx
function UserCard(props) {
  return (
    <div>
      <h2>{props.name}</h2>
      <p>{props.email}</p>
      <span>{props.role}</span>
    </div>
  );
}
```

### Destructuring Props

```jsx
function UserCard({ name, email, role }) {
  return (
    <div>
      <h2>{name}</h2>
      <p>{email}</p>
      <span>{role}</span>
    </div>
  );
}
```

### Props are Getters

In SolidJS, props are reactive getters when passed signals or memos:

```jsx
function Parent() {
  const [name, setName] = createSignal("Alice");

  return <Child name={name} />; // Pass signal directly
}

function Child(props) {
  // props.name is a getter function if parent passed a signal
  createEffect(() => {
    console.log("Name changed:", props.name());
  });

  return <div>{props.name()}</div>;
}
```

### Default Props

```jsx
function Button({ label, variant = "primary", disabled = false }) {
  return (
    <button class={variant} disabled={disabled}>
      {label}
    </button>
  );
}

// Usage
<Button label="Click me" />
// variant="primary", disabled=false by default
```

### Props with Children

```jsx
function Card({ title, children }) {
  return (
    <div class="card">
      <h2>{title}</h2>
      <div class="card-content">{children}</div>
    </div>
  );
}

// Usage
<Card title="My Card">
  <p>This is the card content</p>
  <p>Children can be any JSX</p>
</Card>
```

### Children as Prop

Access children via `props.children`:

```jsx
function Layout(props) {
  return (
    <div class="layout">
      <header>Header</header>
      <main>{props.children}</main>
      <footer>Footer</footer>
    </div>
  );
}
```

## Event Handlers

### Basic Event Handlers

```jsx
function Button() {
  const handleClick = () => {
    console.log("Button clicked!");
  };

  return <button onClick={handleClick}>Click me</button>;
}
```

### Inline Event Handlers

```jsx
function Counter() {
  const [count, setCount] = createSignal(0);

  return (
    <button onClick={() => setCount(count() + 1)}>
      Count: {count()}
    </button>
  );
}
```

### Event Object Access

```jsx
function InputLogger() {
  const handleChange = (event) => {
    console.log("New value:", event.target.value);
  };

  return <input type="text" onChange={handleChange} />;
}
```

### Preventing Default Behavior

```jsx
function Form() {
  const handleSubmit = (event) => {
    event.preventDefault();
    console.log("Form submitted!");
  };

  return (
    <form onSubmit={handleSubmit}>
      <button type="submit">Submit</button>
    </form>
  );
}
```

### Event Delegation with `addEventListener`

```jsx
import { onMount, onCleanup } from "solid-js";

function ClickOutside({ onClick, children }) {
  const ref = {};

  onMount(() => {
    const handler = (event) => {
      if (ref.current && !ref.current.contains(event.target)) {
        onClick();
      }
    };
    document.addEventListener("click", handler);
    onCleanup(() => document.removeEventListener("click", handler));
  });

  return <div ref={ref}>{children}</div>;
}
```

## Component Lifecycle

### `onMount` - After Component Mounts

```jsx
import { onMount, createSignal } from "solid-js";

function DataFetcher() {
  const [data, setData] = createSignal(null);

  onMount(async () => {
    const response = await fetch("/api/data");
    const json = await response.json();
    setData(json);
  });

  return <div>{data() ? "Loaded" : "Loading..."}</div>;
}
```

### `onCleanup` - Before Component Unmounts

```jsx
import { onMount, onCleanup, createSignal } from "solid-js";

function Subscription() {
  const [value, setValue] = createSignal(0);

  onMount(() => {
    const subscription = subscribeToUpdates((v) => setValue(v));

    onCleanup(() => {
      subscription.unsubscribe();
      console.log("Cleaning up subscription");
    });
  });

  return <div>{value()}</div>;
}
```

### `onError` - Error Boundary

```jsx
import { onError, createSignal } from "solid-js";

function RiskyComponent() {
  onError((error) => {
    console.error("Error occurred:", error);
    // Handle error (show fallback UI, log, etc.)
  });

  // Code that might throw
  const result = riskyOperation();

  return <div>{result}</div>;
}
```

## Refs

### Creating Refs

```jsx
import { createRef } from "solid-js";

function InputFocus() {
  const inputRef = createRef();

  const focusInput = () => {
    inputRef.current.focus();
  };

  return (
    <>
      <input ref={inputRef} type="text" />
      <button onClick={focusInput}>Focus Input</button>
    </>
  );
}
```

### Ref with DOM Elements

```jsx
function MeasureComponent() {
  const boxRef = createRef();
  const [dimensions, setDimensions] = createSignal({ width: 0, height: 0 });

  onMount(() => {
    const box = boxRef.current;
    const rect = box.getBoundingClientRect();
    setDimensions({ width: rect.width, height: rect.height });

    // Update on resize
    const observer = new ResizeObserver((entries) => {
      for (let entry of entries) {
        setDimensions({
          width: entry.contentRect.width,
          height: entry.contentRect.height,
        });
      }
    });
    observer.observe(box);

    onCleanup(() => observer.disconnect());
  });

  return (
    <div>
      <div ref={boxRef} class="box">Measured Box</div>
      <p>Width: {dimensions().width}, Height: {dimensions().height}</p>
    </div>
  );
}
```

### Ref for Non-DOM Values

```jsx
import { createRef } from "solid-js";

function Timer() {
  const intervalRef = createRef();
  const [count, setCount] = createSignal(0);

  const startTimer = () => {
    intervalRef.current = setInterval(() => {
      setCount(count() + 1);
    }, 1000);
  };

  const stopTimer = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  return (
    <div>
      <p>Count: {count()}</p>
      <button onClick={startTimer}>Start</button>
      <button onClick={stopTimer}>Stop</button>
    </div>
  );
}
```

## Component Composition

### Slot Pattern with Children

```jsx
function Dialog({ title, children, onClose }) {
  return (
    <div class="dialog-overlay">
      <div class="dialog">
        <header>
          <h2>{title}</h2>
          <button onClick={onClose}>X</button>
        </header>
        <div class="dialog-content">{children}</div>
      </div>
    </div>
  );
}

// Usage
<Dialog title="Confirm" onClose={() => console.log("Closed")}>
  <p>Are you sure you want to proceed?</p>
  <button>Yes</button>
  <button>No</button>
</Dialog>
```

### Named Slots with Props

```jsx
function Layout(props) {
  return (
    <div class="layout">
      <header>{props.header}</header>
      <main>{props.children}</main>
      <footer>{props.footer}</footer>
      <aside>{props.sidebar}</aside>
    </div>
  );
}

// Usage
<Layout
  header={<Navbar />}
  footer={<Copyright />}
  sidebar={<Navigation />}
>
  <Article />
</Layout>
```

### Higher-Order Components

```jsx
import { mergeProps } from "solid-js";

function withLogging(Component) {
  return function LoggedComponent(props) {
    const merged = mergeProps(
      {
        onMount: () => console.log(`${Component.name} mounted`),
        onUnmount: () => console.log(`${Component.name} unmounted`),
      },
      props
    );

    onMount(merged.onMount);
    onCleanup(merged.onUnmount);

    return <Component {...props} />;
  };
}

// Usage
const LoggedButton = withLogging(Button);
```

## Conditional Component Rendering

### Using JavaScript Conditionals

```jsx
function UserDisplay({ user }) {
  return (
    <div>
      {user ? (
        <p>Welcome, {user.name}!</p>
      ) : (
        <p>Please log in</p>
      )}
    </div>
  );
}
```

### Using Show Component

```jsx
import { Show } from "solid-js";

function UserDisplay({ user }) {
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

### Delay Props

Control when children mount:

```jsx
import { Show } from "solid-js";

function LazyComponent({ condition }) {
  return (
    <Show when={condition} fallback={<Loading />}>
      <ExpensiveComponent />
    </Show>
  );
}
```

## Fragment Components

### Returning Multiple Elements

```jsx
import { Fragment } from "solid-js";

function Row({ items }) {
  return (
    <Fragment>
      {items.map((item) => (
        <div class="item">{item}</div>
      ))}
    </Fragment>
  );
}
```

### Using `<>` Syntax

```jsx
function Row({ items }) {
  return (
    <>
      {items.map((item) => (
        <div class="item">{item}</div>
      ))}
    </>
  );
}
```

## Component Best Practices

1. **Keep components small and focused** - One responsibility per component
2. **Use props for data flow** - Pass data down, callbacks up
3. **Lift state when needed** - Move shared state to common parent
4. **Compose components** - Build complex UIs from simple pieces
5. **Use refs sparingly** - Prefer reactive state over imperative DOM access
6. **Clean up side effects** - Always return cleanup from `onMount`

## Common Patterns

### Controlled Input

```jsx
function ControlledInput() {
  const [value, setValue] = createSignal("");

  return (
    <input
      type="text"
      value={value()}
      onChange={(e) => setValue(e.target.value)}
    />
  );
}
```

### Uncontrolled Input with Ref

```jsx
function UncontrolledInput() {
  const inputRef = createRef();

  const getValue = () => {
    return inputRef.current.value;
  };

  return (
    <>
      <input ref={inputRef} type="text" />
      <button onClick={() => console.log(getValue())}>Log Value</button>
    </>
  );
}
```

### Form with Multiple Fields

```jsx
function LoginForm() {
  const [email, setEmail] = createSignal("");
  const [password, setPassword] = createSignal("");
  const [error, setError] = createSignal(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login({ email: email(), password: password() });
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error() && <div class="error">{error()}</div>}
      <input
        type="email"
        placeholder="Email"
        value={email()}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={password()}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <button type="submit">Login</button>
    </form>
  );
}
```
