---
name: htm-3-1
description: A skill for using htm 3.1, a tagged template syntax library that provides JSX-like markup in plain JavaScript without requiring a transpiler. Use when building browser-compatible React/Preact applications with native ES modules, implementing server-side rendering, or creating lightweight UI components without build tooling.
version: "3.1.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
- jsx-alternative
- tagged-templates
- preact
- react
- virtual-dom
- es-modules
- server-side-rendering
- hyperscript
category: development
external_references:
- https://github.com/developit/htm
---

# htm 3.1 — Hyperscript Tagged Markup

## Overview

htm is a library that provides JSX-like syntax using standard JavaScript tagged template literals. It compiles HTML-style markup into hyperscript calls at runtime, eliminating the need for a transpiler. At under 600 bytes gzipped (under 500 with Preact), it enables Virtual DOM development directly in the browser with native ES modules.

htm is framework-agnostic — it works with any function that follows the hyperscript pattern `h(type, props, ...children)`. Official integrations are provided for Preact and React, but it can be bound to custom renderers like [vhtml](https://github.com/developit/vhtml) (string HTML output), [jsxobj](https://github.com/developit/jsxobj) (object configuration), or any custom `h()` function.

## When to Use

- Building React or Preact applications without a build step or transpiler
- Prototyping UI components directly in the browser with native ES modules
- Server-side rendering where JSX compilation is undesirable
- Creating lightweight standalone HTML files with no tooling
- Any scenario where you want JSX-like syntax but cannot use Babel, TypeScript, or similar compilers
- Embedding Virtual DOM in environments that only support standard JavaScript

## Core Concepts

### Tagged Template Literals

htm uses JavaScript's built-in tagged template literal feature. A tagged template like `html\`<div>Hello</div>\`` passes the static string parts and interpolated values to a tag function (`html`), which htm provides by binding itself to a hyperscript function.

### The Hyperscript Pattern

htm translates markup into calls to an `h(type, props, ...children)` function. This is the same pattern used by React's `createElement`, Preact's `h`, and many other Virtual DOM libraries. You tell htm which `h` function to use via `.bind()`.

### No Transpilation Required

Unlike JSX, which requires Babel or TypeScript compilation, tagged templates are standard JavaScript supported in all modern browsers. This means you can write component markup directly in `.js` files with zero build configuration.

## Installation and Setup

htm is published to npm and available via CDN:

**Via npm:**

```js
npm i htm
```

**Via CDN (no build tool needed):**

```js
import htm from 'https://unpkg.com/htm?module';
const html = htm.bind(React.createElement);
```

**htm + Preact in a single import:**

```js
import { html, render } from 'https://unpkg.com/htm/preact/standalone.module.js';
```

### Framework Bindings

htm ships with pre-bound integrations for Preact and React that also share a template cache across modules:

**Preact:**

```js
import { render } from 'preact';
import { html } from 'htm/preact';

render(html`<a href="/">Hello!</a>`, document.body);
```

**React:**

```js
import ReactDOM from 'react-dom';
import { html } from 'htm/react';

ReactDOM.render(html`<a href="/">Hello!</a>`, document.body);
```

### Custom Hyperscript Binding

Bind htm to any `h(type, props, ...children)` function:

```js
import htm from 'htm';

function h(type, props, ...children) {
  return { type, props, children };
}

const html = htm.bind(h);

console.log(html`<h1 id=hello>Hello world!</h1>`);
// { type: 'h1', props: { id: 'hello' }, children: ['Hello world!'] }
```

## Usage Examples

### Basic Markup

```js
import { html } from 'htm/preact';

const greeting = 'World';
const element = html`<h1>Hello, ${greeting}!</h1>`;
```

### Components

Components are referenced with `<${ComponentName}>` syntax (dollar sign before the variable):

```js
const Header = ({ title }) => html`<h1>${title}</h1>`;

const App = () => html`
  <div>
    <${Header} title="My App" />
    <p>Welcome!</p>
  </div>
`;
```

Component closing tags use `<//>`:

```js
const Footer = (props) => html`<footer ...${props}><//>`;

html`<${Footer} class="main-footer">Copyright 2024<//>`;
```

### Event Handlers

```js
const Counter = () => {
  const [count, setCount] = useState(0);
  return html`
    <div>
      <p>Count: ${count}</p>
      <button onClick=${() => setCount(c => c + 1)}>Increment</button>
    </div>
  `;
};
```

### Lists with Keys

```js
const TodoList = ({ todos }) => html`
  <ul>
    ${todos.map(todo => html`
      <li key=${todo.id}>${todo.text}</li>
    `)}
  </ul>
`;
```

### Spread Props

Use `...${}` (with dollar sign) for spreading props:

```js
const Wrapper = ({ children, ...rest }) => html`<div ...${rest}>${children}</div>`;

html`<${Wrapper} class="container" id="main">Content</${Wrapper}>`;
```

### Multiple Root Elements (Fragments)

htm supports multiple root elements without a wrapper:

```js
const rows = html`<tr><td>A</td></tr><tr><td>B</td></tr>`;
// Returns an array of two <tr> VNodes
```

### HTML Comments

```js
html`<div><!-- This comment is ignored --></div>`;
```

### Boolean Attributes

```js
html`<input disabled />`;       // { disabled: true }
html`<details open />`;         // { open: true }
```

### Optional Quotes

htm supports HTML-style unquoted attribute values:

```js
html`<div class=foo id=bar>`;   // Same as class="foo" id="bar"
```

## Advanced Topics

**Syntax Reference**: Complete syntax rules, attribute handling, and edge cases → [Syntax Reference](reference/01-syntax-reference.md)

**Build-Time Compilation**: Using babel-plugin-htm to compile htm to 0 bytes at build time → [Build-Time Compilation](reference/02-build-time-compilation.md)

**Custom Renderers and Patterns**: Binding htm to non-Virtual-DOM targets, SSR patterns, and advanced integration techniques → [Custom Renderers and Patterns](reference/03-custom-renderers-and-patterns.md)
