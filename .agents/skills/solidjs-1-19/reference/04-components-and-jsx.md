# Components and JSX

## Component Basics

Components are functions that return JSX elements. They run once when rendered
and set up a reactive system for updates.

```tsx
function MyComponent() {
  const [count, setCount] = createSignal(0);
  return (
    <div>
      <p>Count: {count()}</p>
      <button onClick={() => setCount(c => c + 1)}>Increment</button>
    </div>
  );
}
```

**Rules:**
- Component names must start with a capital letter
- Return a single root element (use `<>` fragment for multiple children)
- Self-closing tags required: `<img src="..." />`

## Props

Props are passed as JSX attributes and received as the first argument to
component functions:

```tsx
function Greeting(props) {
  return <h1>Hello, {props.name}!</h1>;
}

<Greeting name="World" />
```

### Default Props

Use `mergeProps` for default values:

```tsx
import { mergeProps } from "solid-js";

function Button(props) {
  const merged = mergeProps(
    { type: "button", disabled: false },
    props
  );
  return <button type={merged.type} disabled={merged.disabled}>
    {props.children}
  </button>;
}
```

### splitProps

Split props to pass subsets to different child components:

```tsx
import { splitProps } from "solid-js";

function Wrapper(props) {
  const [buttonProps, rest] = splitProps(props, ["type", "disabled"]);
  return (
    <div {...rest}>
      <button {...buttonProps}>{props.children}</button>
    </div>
  );
}
```

## Event Handling

Event handlers use camelCase and follow standard DOM event patterns:

```tsx
function App() {
  const handleClick = (e) => {
    console.log("Clicked:", e.target);
  };

  return <button onClick={handleClick}>Click me</button>;
}
```

Solid uses **delegated events** — a single listener on the root handles all
events, making it more efficient than attaching listeners to every element.

For direct event listeners (e.g., case-sensitive custom events), use `on:*`:

```tsx
<div on:myCustomEvent={handler} />
```

## JSX Attributes

### class and classList

```tsx
// Static or dynamic class
<div class="active" />
<div class={isActive() ? "active" : "inactive"} />

// Toggle individual classes reactively
<div classList={{
  active: state.active,
  editing: state.currentId === row.id,
}} />
```

### style

Inline styles use double curly braces for objects:

```tsx
<button style={{ color: "red", fontSize: "2rem" }}>
  Styled
</button>
```

### ref

Access DOM elements directly:

```tsx
function Component() {
  let myElement;

  return (
    <div>
      <p ref={myElement}>My Element</p>
    </div>
  );
}
```

Callback form for access before DOM attachment:

```tsx
<p ref={(el) => { myElement = el; }}>My Element</p>
```

### Special JSX Attributes

- `innerHTML` — set inner HTML directly
- `textContent` — set text content (safer than innerHTML)
- `on:` prefix — direct event listener (bypasses delegation)
- `once:` prefix — run expression once, then freeze
- `prop:` prefix — set DOM property instead of attribute
- `attr:` prefix — set DOM attribute explicitly

## Class-Style Components

Solid supports class-based components for stateful patterns:

```tsx
class Counter {
  count = createSignal(0);

  increment = () => this.count[1](c => c + 1);

  render = () => (
    <div>
      <p>Count: {this.count[0]()}</p>
      <button onClick={this.increment}>Increment</button>
    </div>
  );
}
```

## Dynamic Components

Render a component selected at runtime:

```tsx
import { Dynamic } from "solid-js/web";

const [component, setComponent] = createSignal(Button);

<Dynamic component={component()} onClick={handler} />
```

Also works with intrinsic elements:

```tsx
<Dynamic component="h1">Dynamic Heading</Dynamic>
```

## Lazy Loading

Code-split components with dynamic imports:

```tsx
import { lazy } from "solid-js";

const HeavyComponent = lazy(() => import("./HeavyComponent"));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <HeavyComponent />
    </Suspense>
  );
}
```

The lazy component exposes `preload()` for eager loading:

```tsx
HeavyComponent.preload();
```
