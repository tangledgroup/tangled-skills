---
name: solidjs-1-19
description: A comprehensive toolkit for building reactive user interfaces with SolidJS 1.19, a declarative JavaScript framework using fine-grained reactivity. Use when creating web applications, components, or UI libraries requiring efficient state management and minimal virtual DOM overhead.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - javascript
  - typescript
  - frontend
  - reactivity
  - jsx
  - web-development
  - components
  - signals
  - state-management
category: development

external_references:
  - https://www.solidjs.com/docs
  - https://github.com/solidjs/solid
---
## Overview
A comprehensive toolkit for building reactive user interfaces with SolidJS 1.19, a declarative JavaScript framework using fine-grained reactivity. Use when creating web applications, components, or UI libraries requiring efficient state management and minimal virtual DOM overhead.

SolidJS is a declarative, efficient JavaScript framework for building user interfaces using fine-grained reactivity and a small footprint. Unlike virtual DOM-based frameworks, Solid uses fine-grained reactive updates that compile to direct DOM manipulation, resulting in exceptional performance with minimal overhead.

## When to Use
- Building performant single-page applications (SPAs)
- Creating reusable UI components with precise state management
- Developing real-time dashboards requiring frequent updates
- Migrating from React while maintaining JSX syntax familiarity
- Building design systems and component libraries
- Projects requiring optimal bundle size and runtime performance
- Applications needing fine-grained control over reactivity

## Installation / Setup
### Prerequisites

- Node.js 16+ (LTS recommended), Bun, or Deno
- Familiarity with JavaScript/TypeScript and JSX syntax
- Basic understanding of reactive programming concepts

### Create a New Project

```bash
# Using npm
npm init solid@latest my-app -- --template ts

# Using pnpm
pnpm create solid my-app -- --template ts

# Using yarn
yarn create solid my-app -- --template ts

# Using bun
bun create solid my-app -- --template ts
```

The CLI prompts for:
- Project name
- TypeScript support (recommended)
- Template selection (basic, vite, router, etc.)
- CSS flavor (vanilla, styled-components, tailwindcss)

### Project Structure

```
my-app/
├── src/
│   ├── App.jsx           # Root component
│   ├── index.jsx         # Entry point
│   └── index.css         # Global styles
├── package.json
├── vite.config.js        # Build configuration
└── tsconfig.json         # TypeScript config
```

### Development Commands

```bash
npm install          # Install dependencies
npm run dev          # Start development server
npm run build        # Production build
npm run preview      # Preview production build
```

## Usage Examples
### Basic Component

Components are JavaScript functions that return JSX:

```jsx
import { createSignal } from "solid-js";

function Counter() {
  const [count, setCount] = createSignal(0);

  return (
    <div>
      <p>Count: {count()}</p>
      <button onClick={() => setCount(count() + 1)}>Increment</button>
      <button onClick={() => setCount(count() - 1)}>Decrement</button>
    </div>
  );
}

export default Counter;
```

### Rendering to DOM

```jsx
import { render } from "solid-js/web";
import App from "./App";

render(() => <App />, document.getElementById("root"));
```

## Core Concepts
SolidJS reactivity is built on signals, which track dependencies and update only affected parts of the UI. See detailed guides:

- [Reactivity Fundamentals](reference/01-reactivity-fundamentals.md) - Signals, memos, effects, and tracking scopes
- [Component Patterns](reference/02-component-patterns.md) - Props, children, events, and lifecycle
- [Control Flow](reference/03-control-flow.md) - Show, For, Index, Portal, Suspense components
- [State Management](reference/04-state-management.md) - Stores, context, and complex state patterns
- [Advanced Patterns](reference/05-advanced-patterns.md) - Fine-grained reactivity, custom hooks, optimization

## Advanced Topics
## Advanced Topics

- [Reactivity Fundamentals](reference/01-reactivity-fundamentals.md)
- [Component Patterns](reference/02-component-patterns.md)
- [Control Flow](reference/03-control-flow.md)
- [State Management](reference/04-state-management.md)
- [Advanced Patterns](reference/05-advanced-patterns.md)
- [Build Less Setup](reference/06-build-less-setup.md)

## Common Patterns
### Event Handlers

```jsx
function Form() {
  const [name, setName] = createSignal("");

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Submitted:", name());
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={name()}
        onChange={(e) => setName(e.target.value)}
      />
      <button type="submit">Submit</button>
    </form>
  );
}
```

### List Rendering

```jsx
import { For } from "solid-js";

function TodoList() {
  const [todos, setTodos] = createSignal([
    { id: 1, text: "Learn SolidJS", done: false },
    { id: 2, text: "Build something", done: false },
  ]);

  return (
    <ul>
      <For each={todos()} fallback={<li>No todos yet</li>}>
        {(todo) => (
          <li>
            <input
              type="checkbox"
              checked={todo.done}
              onChange={() =>
                setTodos(
                  todos().map((t) =>
                    t.id === todo.id ? { ...t, done: !t.done } : t
                  )
                )
              }
            />
            <span style={{ textDecoration: todo.done ? "line-through" : "none" }}>
              {todo.text}
            </span>
          </li>
        )}
      </For>
    </ul>
  );
}
```

### Conditional Rendering

```jsx
import { Show } from "solid-js";

function UserDisplay() {
  const [user, setUser] = createSignal(null);

  return (
    <Show
      when={user()}
      fallback={
        <button onClick={() => setUser({ name: "Alice" })}>Load User</button>
      }
    >
      <p>Welcome, {user().name}!</p>
    </Show>
  );
}
```

## Troubleshooting
### Common Issues

**Signal not updating UI:** Ensure you're calling the signal as a function `count()` within JSX or a tracking scope. Using `count` without parentheses gets the signal object, not its value.

**Effect running too frequently:** Check that your effect only tracks necessary signals. Use `createMemo` to filter unnecessary updates.

**Props not updating:** Remember that Solid props are getters, not values. Access them as `props.name()` not `props.name`.

**Event handler context lost:** Use arrow functions or `.bind()` to preserve `this` context in event handlers.

### Best Practices

1. **Create signals at the top level** of components, not inside conditionals
2. **Use `createMemo` for expensive computations** to avoid recalculating on every render
3. **Prefer immutable updates** with stores for complex nested state
4. **Clean up effects** by returning a cleanup function from `createEffect`
5. **Use `children` prop** for composability instead of nesting components deeply

### Performance Tips

- Solid's fine-grained reactivity means unnecessary optimizations often hurt readability
- Use `createMemo` sparingly - only when computations are genuinely expensive
- For lists with stable keys, prefer `<Index>` over `<For>` when item order matters
- Batch signal updates in the same tick for better performance
- Use `<Suspense>` boundaries to manage async data loading gracefully

## Build-Less Browser Setup
SolidJS can be used without any build tools by importing directly from a CDN:

```html
<script type="module">
  import { render, createSignal } from "https://esm.sh/solid-js";
  import h from "https://esm.sh/solid-js/h";           // HyperScript
  // or import html from "https://esm.sh/solid-js/html";  // Tagged templates
</script>
```

See [Build-Less Setup](reference/06-build-less-setup.md) for comprehensive guide on:
- HyperScript (`solid-js/h`) - Function-based API
- Tagged Template Literals (`solid-js/html`) - HTML-like syntax
- Complete working examples and best practices

## Ecosystem
### Official Packages

- `solid-js` - Core framework
- `solid-js/web` - DOM rendering and hydration
- `solid-js/h` - HyperScript for build-less environments
- `solid-js/html` - Tagged template literals for build-less environments
- `solid-js/store` - Store utilities (included in solid-js)
- `@solidjs/router` - Client-side routing
- `@solidjs/start` - Full-stack framework with SSR

### Popular Libraries

- `vite` - Default build tool (also supports webpack, esbuild)
- `solid-testing-library` - Testing utilities
- `valibot` or `zod` - Schema validation
- `solid-primitives` - Community primitives collection
- `patronum` - Custom hooks and utilities

## Migration from React
SolidJS shares JSX syntax with React but differs in reactivity:

| React | SolidJS |
|-------|---------|
| `useState()` | `createSignal()` |
| `useEffect()` | `createEffect()` |
| `useMemo()` | `createMemo()` |
| `useRef()` | `createRef()` |
| `useContext()` | `createContext()`/`useContext()` |
| Props as values | Props as getters: `props.value()` |

Key differences:
- No virtual DOM - direct DOM updates via reactive graph
- Component functions run once (no re-renders)
- JSX is compiled to DOM APIs, not object trees
- Signals must be called in tracking scopes to establish dependencies

See [Advanced Patterns](reference/05-advanced-patterns.md) for detailed migration guidance.

