---
name: solidjs-1-9-12
description: >-
  A comprehensive toolkit for building reactive user interfaces with SolidJS
  1.x, a declarative JavaScript framework using fine-grained reactivity.
  Solid compiles templates to real DOM nodes and updates them with
  fine-grained reactions — no Virtual DOM, no rerendering. Components are
  regular functions that run once. Use when creating web applications,
  components, or UI libraries requiring efficient state management and
  minimal virtual DOM overhead.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - solidjs
  - reactivity
  - signals
  - jsx
  - fine-grained
  - web-framework
  - components
category: frontend-framework
external_references:
  - https://www.solidjs.com/docs
  - https://github.com/solidjs/solid
---

# SolidJS 1.x

## Overview

SolidJS is a declarative JavaScript library for building user interfaces.
Instead of using a Virtual DOM, it compiles templates to real DOM nodes and
updates them with fine-grained reactions. Declare your state and use it
throughout your app, and when a piece of state changes, only the code that
depends on it will rerun.

Key characteristics:

- **Fine-grained updates** to the real DOM — no Virtual DOM diffing
- **Declarative data**: model state as a system with reactive primitives
- **Render-once mental model**: components are regular JavaScript functions
  that run once to set up the view
- **Automatic dependency tracking**: accessing reactive state subscribes to it
- **Small and fast**: minimal bundle size, top benchmark performance
- **Modern framework features**: JSX, fragments, Context, Portals, Suspense,
  streaming SSR, progressive hydration, Error Boundaries
- **Isomorphic**: render on client and server
- **Universal**: write custom renderers to use Solid anywhere

## When to Use

- Building reactive single-page applications with minimal overhead
- Creating component libraries that need fine-grained DOM updates
- Migrating from React/Vue/Svelte where performance matters
- Building isomorphic apps with SSR and streaming hydration
- Any project needing a simple, composable reactivity model without hidden rules

## Core Concepts

### Reactivity Model

Solid uses a **pull-based reactive system** built on two core concepts:

- **Signals** — getter/setter pairs that store and manage data. Accessing a
  signal within a tracking scope subscribes to it.
- **Subscribers** — automated responders (effects, memos) that observe signals
  and respond when they change.

Components run **once**. After initial render, only the reactive parts of the
JSX update — the component function body never re-executes.

### Signals vs. Stores

- **Signals** (`createSignal`) track a single value. Best for primitives,
  simple objects, and values read frequently but written infrequently.
- **Stores** (`createStore`) manage complex nested state with fine-grained
  property-level reactivity via JavaScript Proxies. Best for large objects,
  arrays, and deeply nested data.

### Tracking Scopes

Reactivity only works inside tracking scopes. JSX return statements are
tracking scopes. Outside the return statement (in the component body),
signals are not tracked. Use `createEffect`, `createMemo`, or place signals
inside JSX to establish tracking.

## Installation / Setup

Create a project using the official scaffolding tool:

```sh
npx degit solidjs/templates/js my-app
# or for TypeScript
npx degit solidjs/templates/ts my-app
cd my-app
npm install
npm run dev
```

Or install manually:

```sh
npm i solid-js
npm i -D babel-preset-solid
```

Add to Babel config:

```json
{
  "presets": ["solid"]
}
```

For TypeScript, configure `tsconfig.json`:

```json
{
  "compilerOptions": {
    "jsx": "preserve",
    "jsxImportSource": "solid-js"
  }
}
```

## Usage Examples

### Basic Counter

```tsx
import { createSignal } from "solid-js";
import { render } from "solid-js/web";

function Counter() {
  const [count, setCount] = createSignal(0);

  return (
    <div>
      <p>Count: {count()}</p>
      <button onClick={() => setCount(c => c + 1)}>Increment</button>
    </div>
  );
}

render(() => <Counter />, document.getElementById("app")!);
```

### Derived State with Memo

```tsx
import { createSignal, createMemo } from "solid-js";

function App() {
  const [items, setItems] = createSignal([1, 2, 3, 4, 5]);
  const total = createMemo(() => items().reduce((a, b) => a + b, 0));

  return (
    <div>
      <p>Total: {total()}</p>
    </div>
  );
}
```

### Side Effects

```tsx
import { createSignal, createEffect } from "solid-js";

function App() {
  const [count, setCount] = createSignal(0);

  createEffect(() => {
    console.log("Count changed to:", count());
  });

  return (
    <button onClick={() => setCount(c => c + 1)}>
      Click ({count()})
    </button>
  );
}
```

## Advanced Topics

**Reactivity Deep Dive**: Signals, subscribers, tracking scopes, and the reactive graph → [Reactivity Fundamentals](reference/01-reactivity-fundamentals.md)

**Signals and Memos**: Creating reactive state, derived values, performance optimization → [Signals and Memos](reference/02-signals-and-memos.md)

**Stores**: Complex nested state, path syntax, produce/reconcile/unwrap utilities → [Stores](reference/03-stores.md)

**Components and JSX**: Component patterns, props, event handling, class-style components → [Components and JSX](reference/04-components-and-jsx.md)

**Control Flow**: Show, Switch/Match, For, Index conditional and list rendering → [Control Flow](reference/05-control-flow.md)

**Context and Refs**: Cross-component data sharing, DOM element access → [Context and Refs](reference/06-context-and-refs.md)

**Lifecycle and Utilities**: onMount, onCleanup, batch, untrack, createRoot → [Lifecycle and Utilities](reference/07-lifecycle-and-utilities.md)

**Advanced Reactivity**: Fine-grained updates, secondary primitives, render effects → [Advanced Reactivity](reference/08-advanced-reactivity.md)
