# htm Core Concepts

Complete syntax reference for htm (Hyperscript Tagged Markup) version 3.1.

## Element Syntax

### Basic Elements

```js
import htm from 'htm';
const html = htm.bind(h); // h is your hyperscript function

// Self-closing tags
html`<div />`;
html`<br/>`;
html`<input />`;

// Elements with text content
html`<h1>Hello World</h1>`;
html`<p>Paragraph text</p>`;

// Nested elements
html`<div>
  <p>Nested paragraph</p>
</div>`;
```

### Attributes

**Static attributes (quotes optional):**
```js
// With quotes
html`<div id="main" class="container">`;

// Without quotes (htm feature)
html`<div id=main class=container>`;

// Mixed
html`<div id=main class="container active">`;
```

**Dynamic attributes:**
```js
const userId = 123;
const isActive = true;

html`<div id=${userId} active=${isActive}>`;
```

**Boolean attributes:**
```js
// Boolean props (set to true)
html`<input disabled />`;
html`<input readonly />`;
html`<input multiple />`;

// Multiple boolean props
html`<input disabled readonly type="text" />`;
```

**Empty string values:**
```js
html`<input value="" />`;
html`<div data-empty=""></div>`;
```

### Spread Props

Spread operators use `...${}` syntax (not JSX `{...}`):

```js
const props = { id: 'main', class: 'container' };

// Spread at start
html`<div ...${props}>Content</div>`;

// Spread in middle
html`<div id="wrapper" ...${props}>Content</div>`;

// Spread at end
html`<div id="wrapper" ...${props} />`;

// Multiple spreads
html`<div ...${baseProps} ...${overrideProps} />`;

// Mixed with static props
html`<div disabled ...${props} />`;
```

**Important:** Spread order matters - later props override earlier ones:

```js
html`<div ...${{ id: 'a' }} ...${{ id: 'b' }}>`; 
// Results in id="b"
```

## Dynamic Content

### Text Interpolation

```js
const name = 'World';
const count = 42;

// Simple interpolation
html`<h1>Hello ${name}!</h1>`;

// Multiple interpolations
html`<p>You have ${count} items</p>`;

// Mixed static and dynamic text
html`<p>Welcome, ${name}! You have ${count} messages.</p>`;

// Interpolation with expressions
html`<p>Total: ${(price * quantity).toFixed(2)}</p>`;
```

### Attribute Interpolation

```js
const url = '/profile';
const isActive = true;

// Full dynamic attribute
html`<a href=${url}>Profile</a>`;

// Concatenated attributes (static + dynamic)
html`<a href="/user/${userId}">User</a>`;

// Multiple interpolations in one attribute
html`<div class="item ${isActive ? 'active' : ''}">`;

// Dynamic without quotes
html`<a href=/users/${id}>`;  // Works!
```

### Child Element Interpolation

```js
const items = ['Apple', 'Banana', 'Cherry'];

// Map to elements
html`<ul>
  ${items.map(item => html`<li>${item}</li>`)}
</ul>`;

// Conditional rendering
html`<div>
  ${user && html`<span>${user.name}</span>`}
  ${isAdmin ? html`<AdminPanel />` : html`<UserView />`}
</div>`;

// Array of mixed content
html`<div>
  ${[
    html`<span>First</span>`,
    ' text ',
    html`<span>Last</span>`
  ]}
</div>`;
```

## Component Syntax

### Functional Components

```js
// Define component
const Button = ({ label, onClick, disabled }) => 
  html`<button 
    onClick=${onClick} 
    disabled=${disabled}>
    ${label}
  </button>`;

// Use component (wrap in ${})
html`<${Button} label="Click" onClick=${handleClick} />`;

// Component with children
const Card = ({ title, children }) => 
  html`<div class="card">
    <h2>${title}</h2>
    <div class="content">${children}</div>
  </div>`;

html`<${Card} title="Welcome">
  <p>Card content here</p>
<//>`;  // Note: <//> closing tag for components with children
```

### Component Closing Tags

htm supports multiple syntaxes for component end-tags:

```js
const Footer = props => html`<footer ...${props} />`;

// Self-closing (no children)
html`<${Footer} />`;

// With children using <//>
html`<${Footer}>content<//>`;

// Traditional closing (also works)
html`<${Footer}>content</Footer>`;
```

### Dynamic Component Selection

```js
const components = {
  Button: ButtonComponent,
  Link: LinkComponent,
  Input: InputComponent
};

const componentName = 'Button';
const Component = components[componentName];

html`<${Component} someProp="value" />`;

// Conditional component
html`<${isLoading ? Spinner : Content} />`;
```

### Class Components (Preact/React)

```js
import { Component } from 'preact';

class Counter extends Component {
  // Initial state
  state = { count: 0 };
  
  // Lifecycle methods
  componentDidMount() {
    console.log('Mounted');
  }
  
  // Event handler (arrow function preserves `this`)
  increment = () => {
    this.setState({ count: this.state.count + 1 });
  };
  
  // render method returns htm template
  render({ initialCount = 0 }) {
    return html`<div>
      <p>Count: ${this.state.count}</p>
      <button onClick=${this.increment}>+</button>
    </div>`;
  }
}

// Using the component
render(html`<${Counter} initialCount=5 />`, document.body);
```

## Multiple Root Elements (Fragments)

htm supports multiple root elements without special fragment syntax:

```js
// Multiple roots return an array
const fragment = html`
  <div>First</div>
  <div>Second</div>
  <div>Third</div>
`;
// Returns: [h('div', ...), h('div', ...), h('div', ...)]

// Useful in map operations
html`<ul>
  ${items.map(item => html`
    <li>${item.label}</li>
    <hr />
  `)}
</ul>`;

// Component returning multiple elements
const Row = ({ label, value }) => html`
  <dt>${label}</dt>
  <dd>${value}</dd>
`;

html`<dl>
  <${Row} label="Name" value="John" />
  <${Row} label="Age" value="30" />
</dl>`;
```

## HTML Comments

HTML-style comments are supported and ignored:

```js
html`<div>
  <!-- This is a comment -->
  <p>Visible content</p>
  <!-- Another comment -->
</div>`;

// Comments with dynamic content (still ignored)
html`<div>
  <!-- Debug: ${someValue} -->
  <p>Content</p>
</div>`;

// Multi-line comments
html`<div>
  <!-- 
    Multi-line
    comment
    here
  -->
  <p>Content</p>
</div>`;
```

## Special Characters and Edge Cases

### Hyphens in Attribute Names

```js
// Custom attributes with hyphens
html`<div data-id="123" aria-label="Menu">`;
html`<my-custom-element prop-value="test">`;
```

### NUL Characters

```js
// NUL characters are preserved
html`<input value="\0null" />`;
html`<div>\0text</div>`;
```

### Slash in Attribute Values

```js
// Slashes in values don't self-close (unless followed by >)
html`<a href="/path/to/page">Link</a>`;  // Works fine
html`<div data-ratio="16/9">Aspect Ratio</div>`;  // Works fine

// But this WILL self-close early:
html`<abba pr/op=value>`;  // Interpreted as <abba pr /> + /op=value
```

### Event Handlers

```js
// Pass functions directly (no string conversion)
const handleClick = (e) => {
  e.preventDefault();
  console.log('Clicked');
};

html`<button onClick=${handleClick}>Click me</button>`;

// Inline arrow functions
html`<button onClick=${(e) => handleItemClick(e, itemId)}>
  Item ${itemId}
</button>`;

// Multiple handlers
html`<input 
  onFocus=${handleFocus}
  onBlur=${handleBlur}
  onChange=${handleChange}
/>`;
```

## Caching Behavior

htm caches template strings by default for performance optimization:

### How Caching Works

```js
const html = htm.bind(h);

// Same template string returns same object reference
const a = html`<div>Hello</div>`;
const b = html`<div>Hello</div>`;
console.log(a === b);  // true (cached)

// Different templates are different objects
const c = html`<div>World</div>`;
console.log(a === c);  // false

// Dynamic content breaks cache
const name = 'World';
const x = html`<div>${name}</div>`;
const y = html`<div>${name}</div>`;
console.log(x === y);  // false (dynamic, not cached)
```

### Cache Staticness Bits

The `h` function receives staticness information via `this[0]`:

```js
const html = htm.bind(function(type, props, ...children) {
  const staticness = this[0];
  
  // staticness bits:
  // 0 = completely static (can cache reference)
  // 1 = dynamic tag or props, static children
  // 2 = static tag/props, some dynamic children
  // 3 = fully dynamic
  
  console.log(`Staticness: ${staticness}`);
  return h(type, props, ...children);
});

html`<div></div>`;        // this[0] = 0 (static)
html`<div id=${id}></div>`;  // this[0] = 1 (dynamic props)
html`<div>${name}</div>`;    // this[0] = 2 (dynamic children)
```

### Disabling Cache

**Option 1: Use htm/mini**
```js
import { html } from 'htm/mini/preact';  // No caching, smaller size
```

**Option 2: Disable via h function**
```js
const html = htm.bind(function() {
  this[0] = 3;  // Mark as fully dynamic
  return originalH.apply(this, arguments);
});
```

**Option 3: Copy nodes in h function**
```js
const html = htm.bind(function(type, props, children) {
  if (props) props = { ...props };  // Shallow copy
  return originalH(type, props, children);
});
```

## Output Format

htm compiles to hyperscript format: `h(type, props, ...children)`

```js
// Input
html`<div id="main" class="container">Hello ${name}</div>`;

// Output (hyperscript call)
h('div', 
  { id: 'main', class: 'container' }, 
  'Hello ', 
  name
);

// Multiple roots return array
html`<div /> <span />`;
// Returns: [h('div'), h('span')]

// Empty template returns undefined
html``;  // undefined
```

## Comparison with JSX

| Feature | JSX | htm |
|---------|-----|-----|
| Transpiler required | Yes (Babel) | No |
| Tagged template | No | Yes |
| Spread syntax | `{...props}` | `...${props}` |
| Component tag | `<Component />` | `<${Component} />` |
| Quotes for attributes | Required | Optional |
| Multiple roots | Need `<Fragment>` | Native support |
| Comments | `{/* comment */}` | `<!-- comment -->` |
| Component end-tag | `</Component>` | `<//>` or `</Component>` |

## Type Definitions

TypeScript support via declaration files:

```typescript
import htm from 'htm';

declare const htm: {
  bind<HResult>(
    h: (type: any, props: Record<string, any>, ...children: any[]) => HResult
  ): (strings: TemplateStringsArray, ...values: any[]) => HResult | HResult[];
};

// Usage with Preact
import { h } from 'preact';
const html = htm.bind(h);

// Usage with React
import React from 'react';
const html = htm.bind(React.createElement);
```
