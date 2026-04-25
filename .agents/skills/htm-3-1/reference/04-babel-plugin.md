# babel-plugin-htm Configuration Guide

Complete guide to using babel-plugin-htm for production builds that compile htm syntax away.

## Installation

```bash
npm install --save-dev babel-plugin-htm
# or
yarn add -D babel-plugin-htm
```

## Basic Configuration

### .babelrc

```json
{
  "plugins": [
    ["htm", {
      "pragma": "React.createElement"
    }]
  ]
}
```

### babel.config.js

```js
module.exports = {
  plugins: [
    ['htm', {
      pragma: 'React.createElement'
    }]
  ]
};
```

### package.json

```json
{
  "babel": {
    "plugins": [
      ["htm", {
        "pragma": "h"
      }]
    ]
  }
}
```

## Usage Examples

### Default Configuration (Preact-style h)

```js
// Input
import { html } from 'htm/preact';

export default html`<div id="foo">hello ${you}</div>`;

// Output (compiled by babel-plugin-htm)
import { html } from 'htm/preact';

export default h("div", { id: "foo" }, "hello ", you);
```

### React Configuration

```js
// .babelrc
{
  "plugins": [
    ["htm", {
      "pragma": "React.createElement"
    }]
  ]
}

// Input
import { html } from 'htm/react';

export default html`<div id="foo">hello ${you}</div>`;

// Output
import { html } from 'htm/react';
import React from 'react';

export default React.createElement("div", { id: "foo" }, "hello ", you);
```

## Configuration Options

### pragma (default: "h")

The target hyperscript function to compile elements to:

```js
// Default: h
{
  "plugins": [["htm", { "pragma": "h" }]]
}

// React
{
  "plugins": [["htm", { "pragma": "React.createElement" }]]
}

// Custom function
{
  "plugins": [["htm", { "pragma": "myCustomH" }]]
}

// Plain objects (no function call)
{
  "plugins": [["htm", { "pragma": false }]]
}
```

**Example with React:**

```js
// Input
html`<div class="foo">Hello</div>`;

// Output with pragma: "React.createElement"
React.createElement("div", { class: "foo" }, "Hello");
```

### tag (default: "html")

Specify the tag function name to transform:

```js
// Default: transforms `html` tagged templates
{
  "plugins": [["htm", { "tag": "html" }]]
}

// Custom tag name
{
  "plugins": [["htm", { "tag": "myHtml" }]]
}

// Multiple tags using plugin multiple times
{
  "plugins": [
    ["htm", { "tag": "html" }],
    ["htm", { "tag": "jsx" }]
  ]
}
```

**Example:**

```js
// With tag: "myHtml"
import { myHtml } from './html';

export default myHtml`<div>Only myHtml is transformed</div>`;
// html`<div>This is NOT transformed</div>`; // unchanged
```

### import (default: false)

Auto-import the pragma function:

#### String Import

```js
{
  "plugins": [
    ["htm", {
      "pragma": "h",
      "tag": "$$html",
      "import": "htm/preact"
    }]
  ]
}
```

**Input:**
```js
import { html as $$html } from 'htm/preact';

export default $$html`<div>Hello</div>`;
```

**Output:**
```js
import { h } from 'preact';
import { html as $$html } from 'htm/preact';

export default h("div", null, "Hello");
```

#### Object Import (Named Export)

```js
{
  "plugins": [
    ["htm", {
      "pragma": "React.createElement",
      "tag": "$$html",
      "import": {
        "module": "react",
        "export": "default"
      }
    }]
  ]
}
```

**Input:**
```js
import { html as $$html } from 'htm/react';

export default $$html`<div>Hello</div>`;
```

**Output:**
```js
import React from 'react';
import { html as $$html } from 'htm/react';

export default React.createElement("div", null, "Hello");
```

### useBuiltIns (default: false)

Use native `Object.assign` instead of Babel's `_extends` helper:

```js
{
  "plugins": [
    ["htm", {
      "useBuiltIns": true
    }]
  ]
}
```

**Input:**
```js
html`<div ...${props} id="foo">`;
```

**Output (useBuiltIns: false):**
```js
_BabelHelpers._extends({}, props, { id: "foo" });
```

**Output (useBuiltIns: true):**
```js
Object.assign({}, props, { id: "foo" });
```

### useNativeSpread (default: false)

Use native object spread syntax instead of Babel helpers:

```js
{
  "plugins": [
    ["htm", {
      "useNativeSpread": true
    }]
  ]
}
```

**Input:**
```js
html`<div ...${props} id="foo">`;
```

**Output (useNativeSpread: false):**
```js
_BabelHelpers._extends({}, props, { id: "foo" });
```

**Output (useNativeSpread: true):**
```js
{ ...props, id: "foo" };
```

**Note:** This option takes precedence over `useBuiltIns`.

### variableArity (default: true)

Control whether to use variadic children or array:

#### variableArity: true (default)

Matches JSX output - children as separate arguments:

```js
{
  "plugins": [["htm", { "variableArity": true }]]
}
```

**Input:**
```js
html`<div />`;
html`<div a />`;
html`<div>b</div>`;
html`<div a>b</div>`;
```

**Output:**
```js
h("div", null);
h("div", { a: true });
h("div", null, "b");
h("div", { a: true }, "b");
```

#### variableArity: false

Always pass exactly 3 arguments (type, props, children array):

```js
{
  "plugins": [["htm", { "variableArity": false }]]
}
```

**Input:**
```js
html`<div />`;
html`<div a />`;
html`<div>b</div>`;
html`<div a>b</div>`;
```

**Output:**
```js
h("div", null, []);
h("div", { a: true }, []);
h("div", null, ["b"]);
h("div", { a: true }, ["b"]);
```

### pragma: false (Experimental)

Output plain objects instead of function calls:

```js
{
  "plugins": [["htm", { "pragma": false }]]
}
```

**Input:**
```js
html`<div id="foo">hello ${you}</div>`;
```

**Output:**
```js
{ tag: "div", props: { id: "foo" }, children: ["hello ", you] };
```

### monomorphic (Experimental)

Convert all content to uniform object structure:

```js
{
  "plugins": [["htm", { "monomorphic": true }]]
}
```

**Input:**
```js
html`<div id="foo">hello ${you}</div>`;
```

**Output:**
```js
{
  type: 1,
  tag: "div",
  props: { id: "foo" },
  text: null,
  children: [
    { type: 3, tag: null, props: null, text: "hello ", children: null },
    you
  ]
}
```

## Presets and Environments

### Environment-Specific Config

```js
// babel.config.js
module.exports = {
  presets: ['@babel/preset-env'],
  plugins: [
    ['htm', {
      pragma: 'h'
    }]
  ],
  env: {
    development: {
      plugins: [
        ['htm', {
          pragma: 'h',
          // Keep htm in dev for debugging
        }]
      ]
    },
    production: {
      plugins: [
        ['htm', {
          pragma: 'h',
          useNativeSpread: true,
          useBuiltIns: true
        }]
      ]
    }
  }
};
```

### Multiple Presets Setup

```js
module.exports = {
  presets: [
    '@babel/preset-react',  // For any remaining JSX
    '@babel/preset-env'
  ],
  plugins: [
    ['htm', {
      pragma: 'React.createElement',
      tag: 'html',
      import: {
        module: 'react',
        export: 'default'
      }
    }]
  ]
};
```

## Framework-Specific Configurations

### Preact Configuration

```js
module.exports = {
  plugins: [
    ['htm', {
      pragma: 'h',
      import: 'preact'
    }]
  ]
};
```

**Input:**
```js
import { html } from 'htm/preact';
export default html`<div>Hello</div>`;
```

**Output:**
```js
import { h } from 'preact';
import { html } from 'htm/preact';
export default h("div", null, "Hello");
```

### React Configuration

```js
module.exports = {
  plugins: [
    ['htm', {
      pragma: 'React.createElement',
      import: {
        module: 'react',
        export: 'default'
      }
    }]
  ]
};
```

**Input:**
```js
import { html } from 'htm/react';
export default html`<div>Hello</div>`;
```

**Output:**
```js
import React from 'react';
import { html } from 'htm/react';
export default React.createElement("div", null, "Hello");
```

### Inferno Configuration

```js
module.exports = {
  plugins: [
    ['htm', {
      pragma: 'h',
      import: 'inferno'
    }]
  ]
};
```

## Advanced Configurations

### Conditional Transform Based on File Path

```js
// babel.config.js
module.exports = {
  plugins: [
    ['htm', {
      pragma: 'h',
      // Only transform in src/components
      filter: ({ filename }) => filename.includes('/src/components/')
    }]
  ]
};
```

### Custom Tag Names for Different Modules

```js
module.exports = {
  plugins: [
    // Transform html`...` to React
    ['htm', {
      tag: 'html',
      pragma: 'React.createElement',
      import: { module: 'react', export: 'default' }
    }],
    
    // Transform gql`...` for GraphQL queries
    ['htm', {
      tag: 'gql',
      pragma: false  // Output as objects
    }]
  ]
};
```

### Development vs Production Optimizations

```js
module.exports = api => ({
  presets: [
    '@babel/preset-env',
    api.env(['development']) && ['@babel/preset-react', { runtime: 'automatic' }]
  ],
  plugins: [
    api.env('production') && ['htm', {
      pragma: 'h',
      useNativeSpread: true,
      useBuiltIns: true,
      variableArity: false  // Optimize for smaller bundle
    }],
    api.env(['development', 'test']) && ['htm', {
      pragma: 'h',
      // Keep debug-friendly output in dev
    }]
  ].filter(Boolean)
});
```

## Troubleshooting

### Plugin Not Transforming Code

**Check tag name matches:**

```js
// If using custom tag name
import { myHtml } from './html';

myHtml`<div>This won't transform with default config</div>`;

// Config must match:
{
  "plugins": [["htm", { "tag": "myHtml" }]]
}
```

### Import Not Working

**Ensure module path is correct:**

```js
// For React
{
  "import": {
    "module": "react",
    "export": "default"  // React.createElement is default export
  }
}

// For Preact
{
  "import": "preact"  // 'h' is named export, plugin handles this
}
```

### Spread Props Not Working

**Enable appropriate option:**

```js
// For native spread syntax (modern browsers)
{
  "useNativeSpread": true
}

// For Object.assign (older browsers)
{
  "useBuiltIns": true
}
```

### Multiple Root Elements

**Ensure variableArity matches your h function:**

```js
// If h expects array for multiple children:
{
  "variableArity": false
}

// If h expects variadic arguments (like React.createElement):
{
  "variableArity": true
}
```

## Performance Tips

### Production Optimizations

```js
module.exports = {
  plugins: [
    ['htm', {
      pragma: 'h',
      useNativeSpread: true,     // Smaller than _extends helper
      useBuiltIns: true,          // No additional helpers
      variableArity: false,       // Consistent function signature
      import: 'preact'            // Auto-import, no manual imports
    }]
  ]
};
```

### Bundle Size Reduction

Using babel-plugin-htm eliminates the need to ship htm runtime:

**Without plugin:** ~600 bytes (htm library)
**With plugin:** 0 bytes (compiled away at build time)

## Migration from Runtime htm

### Before (Runtime htm)

```js
import { html } from 'htm/preact';

export default html`<div id="foo">Hello ${name}</div>`;
```

### After (Compiled with Babel)

```js
// Same source code
import { html } from 'htm/preact';

export default html`<div id="foo">Hello ${name}</div>`;

// Compiles to:
import { h } from 'preact';

export default h("div", { id: "foo" }, "Hello ", name);
```

**Benefits:**
- No runtime dependency on htm
- Smaller bundle size
- Same developer experience
- Production-optimized output

## Complete Example Project Setup

### package.json

```json
{
  "name": "htm-project",
  "scripts": {
    "build": "babel src --out-dir dist",
    "dev": "babel src --out-dir dist --watch"
  },
  "devDependencies": {
    "@babel/core": "^7.22.0",
    "@babel/cli": "^7.22.0",
    "babel-plugin-htm": "^1.3.0"
  },
  "dependencies": {
    "preact": "^10.13.0"
  }
}
```

### babel.config.js

```js
module.exports = {
  presets: [
    ['@babel/preset-env', {
      targets: { browsers: ['last 2 versions'] }
    }]
  ],
  plugins: [
    ['htm', {
      pragma: 'h',
      import: 'preact',
      useNativeSpread: true,
      useBuiltIns: true
    }]
  ]
};
```

### src/index.js

```js
import { html, render, Component } from 'htm/preact';

class App extends Component {
  render() {
    return html`<div class="app">
      <h1>Hello World!</h1>
      <p>This is compiled by babel-plugin-htm</p>
    </div>`;
  }
}

render(html`<${App} />`, document.getElementById('root'));
```

### dist/index.js (Compiled Output)

```js
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _preact = require("preact");

class App extends _preact.Component {
  render() {
    return (0, _preact.h)("div", {
      class: "app"
    }, (0, _preact.h)("h1", null, "Hello World!"), (0, _preact.h)("p", null, "This is compiled by babel-plugin-htm"));
  }

}

(0, _preact.render)((0, _preact.h)(App, null), document.getElementById('root'));
```
