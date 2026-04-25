# Build-Less Browser Setup

SolidJS can be used without any build tools or compilation step by using HyperScript (`solid-js/h`) or Tagged Template Literals (`solid-js/html`). This is ideal for simple projects, rapid prototyping, or environments where you cannot use a build pipeline.

## Overview

| Method | Package | Syntax Style | Best For |
|--------|---------|--------------|----------|
| HyperScript | `solid-js/h` | Function calls | Programmatic component creation |
| Tagged Templates | `solid-js/html` | Template literals | HTML-like syntax in JS |
| JSX (compiled) | Build tool required | XML-like tags | Production applications |

Both methods work directly in the browser with no compilation, but have trade-offs:
- **Larger runtime** - Cannot treeshake unused features
- **Manual reactivity** - Must wrap expressions in functions
- **No compile-time optimizations** - Slightly slower than compiled JSX

## Setup

### Basic HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SolidJS Build-Less</title>
</head>
<body>
  <div id="app"></div>
  
  <!-- Import SolidJS as ES modules -->
  <script type="module">
    import { render, createSignal } from "https://esm.sh/solid-js";
    import h from "https://esm.sh/solid-js/h";
    // or import html from "https://esm.sh/solid-js/html";
    
    // Your app code here
  </script>
</body>
</html>
```

### CDN Options

**Using esm.sh (recommended):**
```html
<script type="module">
  import { render, createSignal, createEffect } from "https://esm.sh/solid-js";
  import h from "https://esm.sh/solid-js/h";
  import html from "https://esm.sh/solid-js/html";
</script>
```

**Using unpkg:**
```html
<script type="module">
  import { render, createSignal } from "https://unpkg.com/solid-js@latest/dist/solid.esm.js";
  import h from "https://unpkg.com/solid-js@latest/h/dist/h.esm.js";
  import html from "https://unpkg.com/solid-js@latest/html/dist/html.esm.js";
</script>
```

**Using jsDelivr:**
```html
<script type="module">
  import { render, createSignal } from "https://cdn.jsdelivr.net/npm/solid-js@latest/dist/solid.esm.js";
  import h from "https://cdn.jsdelivr.net/npm/solid-js@latest/h/dist/h.esm.js";
</script>
```

## HyperScript (`solid-js/h`)

HyperScript provides a function-based API for creating elements and components without JSX compilation.

### Basic Usage

```js
import { render, createSignal } from "solid-js";
import h from "solid-js/h";

// Create an element with attributes and text
h("button", { title: "Click me" }, "Click Me");

// Create a component with props
h(MyComponent, { name: "Alice" }, "Welcome");

// Nested elements
h("div", { class: "container" },
  h("h1", "Hello"),
  h("p", "This is a paragraph")
);
```

### Component Example

```js
import { render, createSignal } from "solid-js";
import h from "solid-js/h";

function Button(props) {
  return h("button.btn-primary", { ...props });
}

function Counter() {
  const [count, setCount] = createSignal(0);
  
  return h("div", null,
    h("p", () => `Count: ${count()}`),
    h(Button, { 
      type: "button",
      onClick: () => setCount(c => c + 1)
    }, "Increment"),
    h(Button, { 
      type: "button",
      onClick: () => setCount(c => c - 1)
    }, "Decrement")
  );
}

render(Counter, document.getElementById("app"));
```

### Shorthand Syntax

**ID and class shorthand:**
```js
// Instead of:
h("div", { id: "main", class: "container" }, "Content")

// Use:
h("div#main.container", "Content")

// Multiple classes
h("button.btn.btn-primary", { onClick: handler }, "Click")
```

### Reactive Expressions

**Must wrap expressions in functions for reactivity:**

```js
function Greeting({ firstName, lastName }) {
  // Wrong - not reactive
  // h("div", `${firstName()} ${lastName()}`);
  
  // Correct - wrapped in function
  return h("div", () => `${firstName()} ${lastName()}`);
}

// With signals
function Counter() {
  const [count, setCount] = createSignal(0);
  
  // Wrong
  // h("p", `Count: ${count()}`);
  
  // Correct
  return h("p", () => `Count: ${count()}`);
}
```

### Dynamic Attributes

```js
function UserCard({ user }) {
  return h("div.user-card", { 
    id: () => `user-${user().id}`,  // Reactive attribute
    class: () => user().active ? "active" : "inactive",  // Dynamic class
    "aria-label": () => `Profile for ${user().name}`  // Reactive ARIA
  },
    h("h2", () => user().name),
    h("p", () => user().email)
  );
}
```

### Props Spreading and Merging

**Use `mergeProps` for combining props:**

```js
import { mergeProps } from "solid-js";

function Input(props) {
  const merged = mergeProps(
    { type: "text", class: "input" },
    props
  );
  
  return h("input", merged);
}

// Usage with additional props
h(Input, { 
  type: "email",  // Overrides default
  placeholder: "Enter email" 
});
```

### Event Handlers

**Events on components need explicit event argument:**

```js
function MyButton(props) {
  return h("button", props);
}

// Good - function takes event parameter
h(MyButton, { onClick: (e) => console.log("Clicked", e) });

// Bad - will be wrapped as getter automatically
h(MyButton, { onClick: () => console.log("Clicked") });

// For DOM elements, both work
h("button", { 
  onClick: (e) => console.log(e)  // Good
});
```

### Refs (Callback Form Only)

```js
function InputWithFocus() {
  const inputRef = {};
  
  const focusInput = () => {
    inputRef.current?.focus();
  };
  
  return h("div", null,
    h("input", { 
      ref: (el) => { inputRef.current = el; } 
    }),
    h("button", { onClick: focusInput }, "Focus Input")
  );
}
```

### Fragments

**Fragments are arrays:**

```js
function Row() {
  return [
    h("span", "Item 1"),
    h("span", "Item 2"),
    h("span", "Item 3")
  ];
}

// Or with variable number of children
function List({ items }) {
  return items.map(item => 
    h("li", () => item().name)
  );
}
```

### Control Flow Components

```js
import { Show, For, createSignal } from "solid-js";
import h from "solid-js/h";

function TodoList() {
  const [todos, setTodos] = createSignal([
    { id: 1, text: "Learn HyperScript", done: false },
    { id: 2, text: "Build something", done: false }
  ]);
  
  return h("div", null,
    h("h2", "Todos"),
    
    // Show with fallback
    h(Show, { 
      when: todos().length > 0,
      fallback: h("p", "No todos yet")
    },
      h("ul", null,
        h(For, { each: todos }, (todo) =>
          h("li", null,
            h("input", {
              type: "checkbox",
              checked: () => todo().done,
              onChange: (e) => {
                setTodos(todos().map(t => 
                  t.id === todo().id 
                    ? { ...t, done: e.target.checked } 
                    : t
                ));
              }
            }),
            h("span", () => todo().text)
          )
        )
      )
    ),
    
    h("button", {
      onClick: () => setTodos([...todos(), { 
        id: Date.now(), 
        text: "New todo", 
        done: false 
      }])
    }, "Add Todo")
  );
}
```

## Tagged Template Literals (`solid-js/html`)

Tagged template literals provide HTML-like syntax using JavaScript template strings.

### Basic Usage

```js
import { render, createSignal } from "solid-js";
import html from "solid-js/html";

// Create an element
html`<button title="Click me">Click Me</button>`;

// Create a component (use <${Component}> and <//>)
html`<${MyComponent} name="Alice">Welcome<//>`;

// Nested elements
html`
  <div class="container">
    <h1>Hello</h1>
    <p>This is a paragraph</p>
  </div>
`;
```

### Component Example

```js
import { render, createSignal } from "solid-js";
import html from "solid-js/html";

function Button(props) {
  return html`<button class="btn-primary" ...${props} />`;
}

function Counter() {
  const [count, setCount] = createSignal(0);
  
  return html`
    <div>
      <p>Count: ${count}</p>
      <${Button} type="button" onClick=${() => setCount(c => c + 1}>Increment<//>
      <${Button} type="button" onClick=${() => setCount(c => c - 1}>Decrement<//>
    </div>
  `;
}

render(Counter, document.getElementById("app"));
```

### Reactive Expressions

**Wrap reactive values in functions or use direct interpolation:**

```js
function Greeting({ firstName, lastName }) {
  // Direct interpolation (auto-wrapped)
  return html`<div>${firstName()} ${lastName()}</div>`;
  
  // Or explicit function wrapper for complex expressions
  // return html`<div>${() => firstName() + ' ' + lastName()}</div>`;
}

function Counter() {
  const [count, setCount] = createSignal(0);
  
  return html`<p>Count: ${count}</p>`;
  // Note: count (not count()) in template literals
}
```

### Dynamic Attributes

```js
function UserCard({ user }) {
  return html`
    <div 
      class="user-card" 
      id=${() => `user-${user().id}`}
      data-active=${() => user().active ? "true" : "false"}
    >
      <h2>${user().name}</h2>
      <p>${user().email}</p>
    </div>
  `;
}
```

### Props Spreading

```js
function Input(props) {
  return html`<input class="input" ...${props} />`;
}

// Usage
html`<${Input} type="email" placeholder="Enter email" />`;
```

### Event Handlers

**Events need explicit function wrappers:**

```js
function MyButton(props) {
  return html`<button ...${props} />`;
}

// Good - event parameter included
html`<${MyButton} onClick=${(e) => console.log("Clicked", e)} />`;

// Bad - will be wrapped as getter
html`<${MyButton} onClick=${() => console.log("Clicked")} />`;
```

### Refs (Callback Form Only)

```js
function InputWithFocus() {
  let inputEl;
  
  const focusInput = () => {
    inputEl?.focus();
  };
  
  return html`
    <div>
      <input ref=${(el) => { inputEl = el; }} />
      <button onClick=${focusInput}>Focus Input</button>
    </div>
  `;
}
```

### Multiple Root Elements

**No fragment wrapper needed:**

```js
function Row() {
  return html`
    <span>Item 1</span>
    <span>Item 2</span>
    <span>Item 3</span>
  `;
}
```

### Control Flow Components

```js
import { Show, For, createSignal } from "solid-js";
import html from "solid-js/html";

function TodoList() {
  const [todos, setTodos] = createSignal([
    { id: 1, text: "Learn tagged templates", done: false }
  ]);
  
  return html`
    <div>
      <h2>Todos</h2>
      
      <${Show} when=${todos().length > 0} fallback=${html`<p>No todos yet</p>`}>
        <ul>
          <${For} each=${todos}>
            ${todo => html`
              <li>
                <input 
                  type="checkbox" 
                  checked=${todo().done}
                  onChange=${e => setTodos(todos().map(t => 
                    t.id === todo().id 
                      ? { ...t, done: e.target.checked } 
                      : t
                  ))}
                />
                <span>${todo().text}</span>
              </li>
            `}
          <//>
        </ul>
      <//>
      
      <button onClick=${() => setTodos([...todos(), { 
        id: Date.now(), 
        text: "New todo", 
        done: false 
      }])}>Add Todo</button>
    </div>
  `;
}
```

### Conditional Classes

```js
function Card({ active, selected }) {
  return html`
    <div 
      class=${() => [
        "card",
        active() ? "active" : "",
        selected() ? "selected" : ""
      ].filter(Boolean).join(" ")}
    >
      Card content
    </div>
  `;
}
```

## Complete Example: Counter App

### Using HyperScript

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>SolidJS Counter - HyperScript</title>
  <style>
    .counter { padding: 20px; font-family: sans-serif; }
    button { margin: 5px; padding: 10px 20px; cursor: pointer; }
  </style>
</head>
<body>
  <div id="app"></div>
  
  <script type="module">
    import { render, createSignal } from "https://esm.sh/solid-js";
    import h from "https://esm.sh/solid-js/h";
    
    function Counter() {
      const [count, setCount] = createSignal(0);
      
      return h("div.counter", null,
        h("h1", "Counter App"),
        h("p", () => `Current count: ${count()}`),
        h("div", null,
          h("button", { 
            onClick: () => setCount(c => c - 1) 
          }, "− Decrease"),
          h("button", { 
            onClick: () => setCount(0) 
          }, "Reset"),
          h("button", { 
            onClick: () => setCount(c => c + 1) 
          }, "+ Increase")
        )
      );
    }
    
    render(Counter, document.getElementById("app"));
  </script>
</body>
</html>
```

### Using Tagged Templates

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>SolidJS Counter - Tagged Templates</title>
  <style>
    .counter { padding: 20px; font-family: sans-serif; }
    button { margin: 5px; padding: 10px 20px; cursor: pointer; }
  </style>
</head>
<body>
  <div id="app"></div>
  
  <script type="module">
    import { render, createSignal } from "https://esm.sh/solid-js";
    import html from "https://esm.sh/solid-js/html";
    
    function Counter() {
      const [count, setCount] = createSignal(0);
      
      return html`
        <div class="counter">
          <h1>Counter App</h1>
          <p>Current count: ${count}</p>
          <div>
            <button onClick=${() => setCount(c => c - 1)}>− Decrease</button>
            <button onClick=${() => setCount(0)}>Reset</button>
            <button onClick=${() => setCount(c => c + 1)}>+ Increase</button>
          </div>
        </div>
      `;
    }
    
    render(Counter, document.getElementById("app"));
  </script>
</body>
</html>
```

## Comparison: JSX vs HyperScript vs Templates

| Feature | JSX (Compiled) | HyperScript | Tagged Templates |
|---------|----------------|-------------|------------------|
| Build required | Yes | No | No |
| Syntax | XML-like | Function calls | Template literals |
| Reactivity | Automatic | Manual wrapping | Semi-automatic |
| Performance | Best | Good | Good |
| Bundle size | Small (treeshaked) | Larger | Larger |
| Readability | High | Medium | High |
| IDE support | Excellent | Limited | Limited |

### JSX Equivalent Examples

```jsx
// JSX (requires compilation)
function Example() {
  const [value, setValue] = createSignal("hello");
  
  return (
    <div id="main" className="container">
      <span>{value()}</span>
      <button onClick={() => setValue("world")}>Change</button>
    </div>
  );
}

// HyperScript equivalent
function Example() {
  const [value, setValue] = createSignal("hello");
  
  return h("div#main.container", null,
    h("span", () => value()),
    h("button", { onClick: () => setValue("world") }, "Change")
  );
}

// Tagged template equivalent
function Example() {
  const [value, setValue] = createSignal("hello");
  
  return html`
    <div id="main" class="container">
      <span>${value}</span>
      <button onClick=${() => setValue("world")}>Change</button>
    </div>
  `;
}
```

## Best Practices for Build-Less Setup

1. **Use CDN imports** - esm.sh, unpkg, or jsDelivr for module loading
2. **Wrap reactive expressions** - Always use functions for dynamic content in HyperScript
3. **Use callback refs** - Only callback form refs are supported
4. **Merge props correctly** - Use `mergeProps` for combining prop objects
5. **Event handlers need parameters** - Include event parameter to prevent auto-wrapping
6. **Keep components simple** - Build-less is best for smaller applications
7. **Consider migration path** - Plan to migrate to JSX for larger projects

## Limitations

- **No treeshaking** - Entire SolidJS runtime is loaded
- **Manual reactivity** - Must remember to wrap expressions
- **Limited tooling** - Less IDE support and autocomplete
- **Runtime overhead** - Slightly slower than compiled JSX
- **No static analysis** - Can't catch errors at compile time

## When to Use Build-Less

✅ **Good for:**
- Rapid prototyping
- Simple widgets or components
- Learning SolidJS concepts
- Embedded scripts in existing sites
- Environments without build tools

❌ **Not recommended for:**
- Large-scale applications
- Performance-critical projects
- Projects needing optimal bundle size
- Teams requiring strong type safety

## Migration to JSX

When ready to migrate to a build setup:

1. Set up Vite or other build tool
2. Replace `h()` calls with JSX syntax
3. Remove manual function wrappers from expressions
4. Add TypeScript for type safety
5. Enable treeshaking for smaller bundles

```js
// Before (HyperScript)
h("div.container", null,
  h("h1", () => title()),
  h("p", () => description())
);

// After (JSX)
<div class="container">
  <h1>{title()}</h1>
  <p>{description()}</p>
</div>
```

## Resources

- [SolidJS Documentation](https://docs.solidjs.com/)
- [solid-js/h GitHub](https://github.com/solidjs/solid/tree/main/packages/solid/h)
- [solid-js/html GitHub](https://github.com/solidjs/solid/tree/main/packages/solid/html)
- [esm.sh CDN](https://esm.sh/)
- [SolidJS Examples](https://github.com/solidjs/examples)
