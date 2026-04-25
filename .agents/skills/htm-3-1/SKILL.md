---
name: htm-3-1
description: A skill for using htm 3.1, a tagged template syntax library that provides JSX-like markup in plain JavaScript without requiring a transpiler. Use when building browser-compatible React/Preact applications with native ES modules, implementing server-side rendering, or creating lightweight UI components without build tooling.
version: "0.2.0"
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
## Overview
A skill for using htm 3.1, a tagged template syntax library that provides JSX-like markup in plain JavaScript without requiring a transpiler. Use when building browser-compatible React/Preact applications with native ES modules, implementing server-side rendering, or creating lightweight UI components without build tooling.

A skill for using **htm** (Hyperscript Tagged Markup), a library that provides JSX-like syntax in plain JavaScript using tagged template literals. No transpiler required - works directly in modern browsers with native ES modules.

## When to Use
- Building React/Preact applications without build tooling
- Developing browser-based prototypes with native ES modules
- Implementing server-side rendering (SSR) without JSX compilation
- Creating lightweight UI components (< 600 bytes when gzipped)
- Working in environments where Babel/transpilation is unavailable
- Needing HTML-style syntax for configuration objects (webpack, etc.)

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.

## Installation / Setup
### Browser Usage (No Build Tool)

```js
import { html, render } from 'https://unpkg.com/htm/preact/standalone.module.js';

const App = () => html`<div>Hello World!</div>`;

render(html`<${App} />`, document.body);
```

### npm Installation

```bash
npm install htm preact
```

```js
import { render } from 'preact';
import { html } from 'htm/preact';

const App = () => html`<div>Hello World!</div>`;

render(html`<${App} />`, document.body);
```

### React Integration

```bash
npm install htm react react-dom
```

```js
import ReactDOM from 'react-dom/client';
import { html } from 'htm/react';

const App = () => html`<div>Hello World!</div>`;

ReactDOM.createRoot(document.getElementById('root')).render(html`<${App} />`);
```

## Core Syntax
See [Core Concepts](reference/01-core-concepts.md) for detailed syntax reference.

### Basic Elements

```js
import htm from 'htm';

const html = htm.bind(someHyperscriptFunction);

// Self-closing tags
html`<div />`;
html`<br />`;

// Elements with content
html`<h1>Hello World</h1>`;

// Attributes (quotes optional for static values)
html`<div id=main class="container">Content</div>`;

// Boolean attributes
html`<input disabled />`;
html`<input readonly />`;
```

### Dynamic Values

```js
const name = 'World';
const items = ['a', 'b', 'c'];

// Interpolated values in content
html`<h1>Hello ${name}!</h1>`;

// Interpolated attributes
html`<div id=${userId}>User Info</div>`;

// List rendering
html`<ul>
  ${items.map(item => html`<li>${item}</li>`)}
</ul>`;

// Dynamic component names
const Button = props => html`<button ...${props} />`;
html`<${Button} onClick=${handleClick}>Click me</${}>`;
```

### Component Syntax

```js
// Functional components
const Header = ({ title }) => html`<h1>${title}</h1>`;

// Using components
html`<${Header} title="My App" />`;

// Component with children using <//> closing syntax
const Card = ({ title, children }) => 
  html`<div class="card">
    <h2>${title}</h2>
    ${children}
  </div>`;

html`<${Card} title="Welcome">
  <p>This is the card content</p>
<//>`;

// Class components (Preact)
import { Component } from 'preact';

class Counter extends Component {
  state = { count: 0 };
  
  increment = () => this.setState({ count: this.state.count + 1 });
  
  render() {
    return html`<button onClick=${this.increment}>
      Count: ${this.state.count}
    </button>`;
  }
}

render(html`<${Counter} />`, document.body);
```

## Key Features
- **No transpiler needed** - Uses native JavaScript tagged templates
- **Multiple root elements** - Fragments without special syntax
- **HTML comments** - `<!-- comment -->` supported and ignored
- **Component end-tags** - `<//>` for components with children
- **Spread props** - `<div ...${props}>` instead of JSX `{...props}`
- **Optional quotes** - `<div class=foo>` works without quotes

See [Advanced Features](reference/02-advanced-features.md) for detailed examples.

## Performance & Size
| Build | Size (gzipped) | Notes |
|-------|---------------|-------|
| `htm` (full) | < 600 bytes | With template caching |
| `htm/preact` | < 500 bytes | Optimized for Preact |
| `htm/mini` | < 450 bytes | No caching, smallest size |
| `babel-plugin-htm` | 0 bytes | Compiles htm away at build time |

## Advanced Topics
## Advanced Topics

- [Core Concepts](reference/01-core-concepts.md)
- [Advanced Features](reference/02-advanced-features.md)
- [Integrations](reference/03-integrations.md)
- [Babel Plugin](reference/04-babel-plugin.md)
- [Migration Guide](reference/05-migration-guide.md)

## Troubleshooting
### Common Issues

**"html is not defined"** - Ensure you've bound htm to a hyperscript function:
```js
import htm from 'htm';
import { h } from 'preact';
const html = htm.bind(h); // Required step
```

**Component not rendering children** - Use `<//>` for component closing tags with content:
```js
// Wrong for components with children
html`<${Footer}>content</Footer>`;

// Correct
html`<${Footer}>content<//>`;
```

**Props not spreading correctly** - Use `...${}` syntax (not `{...}`):
```js
// Wrong (JSX syntax)
html`<div {...props} />`;

// Correct (htm syntax)
html`<div ...${props} />`;
```

**Dynamic tag names require interpolation** - Wrap component references in `${}`:
```js
// Wrong
html`<MyComponent />`;

// Correct
const MyComponent = () => html`<div />`;
html`<${MyComponent} />`;
```

### Browser Compatibility

htm requires browsers that support:
- Template literals (ES6)
- Tagged template functions
- ES modules (for CDN usage)

See [MDN Template Literals](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals#Browser_compatibility) for full compatibility table.

### Caching Behavior

htm caches template strings by default for performance. To disable caching:

```js
// Option 1: Use htm/mini (no caching)
import { html } from 'htm/mini/preact';

// Option 2: Modify the h function
const html = htm.bind(function h() {
  this[0] = 3; // Disable caching
  return originalH.apply(this, arguments);
});

// Option 3: Copy nodes in your h function
const html = htm.bind(function h(type, props, children) {
  if (props) props = { ...props };
  return originalH(type, props, children);
});
```

See [Static Caching Tests](reference/01-core-concepts.md#caching-behavior) for detailed caching semantics.

