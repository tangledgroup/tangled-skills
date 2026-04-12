# htm Integrations

Complete guide to integrating htm with React, Preact, and custom hyperscript functions.

## Preact Integration

### Using Pre-built Integration

The easiest way to use htm with Preact:

```js
import { html, render, Component } from 'htm/preact';

const App = () => html`<div>Hello World!</div>`;

render(html`<${App} />`, document.body);
```

This provides:
- `html` - Bound template function
- `render` - Preact's render function
- `Component` - Preact's Component base class

### Standalone Build (All-in-One)

For simple projects without build tools:

```html
<!DOCTYPE html>
<html>
<head>
  <title>htm + Preact App</title>
</head>
<body>
  <div id="app"></div>
  
  <script type="module">
    import { html, render, Component, useState } from 
      'https://unpkg.com/htm/preact/standalone.module.js';
    
    function Counter() {
      const [count, setCount] = useState(0);
      
      return html`<div>
        <p>Count: ${count}</p>
        <button onClick=${() => setCount(c => c + 1)}>+</button>
        <button onClick=${() => setCount(c => c - 1)}>-</button>
      </div>`;
    }
    
    render(html`<${Counter} />`, document.getElementById('app'));
  </script>
</body>
</html>
```

The standalone build includes:
- Preact core (h, render, Component)
- Preact hooks (useState, useEffect, useContext, etc.)
- htm bound to Preact's h function

### Manual Integration with npm

```js
import { h, render, Component } from 'preact';
import htm from 'htm';

// Bind htm to Preact's h function
const html = htm.bind(h);

export { html, render, Component };
```

### Using Hooks

```js
import { html } from 'htm/preact';
import { useState, useEffect, useCallback, useMemo } from 'preact/hooks';

function DataFetcher({ url }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    let cancelled = false;
    
    async function fetchData() {
      try {
        const response = await fetch(url);
        const json = await response.json();
        
        if (!cancelled) {
          setData(json);
          setLoading(false);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err);
          setLoading(false);
        }
      }
    }
    
    fetchData();
    
    return () => { cancelled = true; };
  }, [url]);
  
  // Memoized derived state
  const itemCount = useMemo(() => data?.items?.length || 0, [data]);
  
  // Memoized callback
  const handleRefresh = useCallback(() => {
    setLoading(true);
    setData(null);
  }, []);
  
  if (loading) return html`<div>Loading...</div>`;
  if (error) return html`<div>Error: ${error.message}</div>`;
  
  return html`<div>
    <h2>Data (${itemCount} items)</h2>
    <button onClick=${handleRefresh}>Refresh</button>
    <pre>${JSON.stringify(data, null, 2)}</pre>
  </div>`;
}
```

## React Integration

### Using Pre-built Integration

```js
import ReactDOM from 'react-dom/client';
import { html } from 'htm/react';

const App = () => html`<div>Hello World!</div>`;

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(html`<${App} />`);
```

### Manual Integration

```js
import React from 'react';
import htm from 'htm';

// Bind htm to React.createElement
const html = htm.bind(React.createElement);

export { html, React };
```

### Using React Hooks

```js
import { useState, useEffect, useContext } from 'react';
import { html } from 'htm/react';

function Counter() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    document.title = `Count: ${count}`;
  }, [count]);
  
  return html`<div>
    <p>Current count: ${count}</p>
    <button onClick=${() => setCount(c => c + 1)}>Increment</button>
    <button onClick=${() => setCount(c => c - 1)}>Decrement</button>
    <button onClick=${() => setCount(0)}>Reset</button>
  </div>`;
}
```

### React Context with htm

```js
import { createContext, useContext, useState } from 'react';
import { html } from 'htm/react';

// Create context
const ThemeContext = createContext('light');

// Provider component
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');
  
  return html`<${ThemeContext.Provider} value=${theme}>
    <div class=${theme}>
      <button onClick=${() => setTheme(t => t === 'light' ? 'dark' : 'light')}>
        Toggle Theme
      </button>
      ${children}
    </div>
  <//>`;
}

// Consumer component using hook
function ThemedComponent() {
  const theme = useContext(ThemeContext);
  
  return html`<div class="themed-content">
    <p>Current theme: ${theme}</p>
    <p style=${`color: ${theme === 'light' ? 'black' : 'white'}`}>
      This text changes color with the theme.
    </p>
  </div>`;
}

// App using context
function App() {
  return html`<${ThemeProvider}>
    <${ThemedComponent} />
  </${ThemeProvider}>`;
}
```

### React Class Components

```js
import React from 'react';
import { html } from 'htm/react';

class UserList extends React.Component {
  state = { users: [], loading: true };
  
  async componentDidMount() {
    try {
      const response = await fetch('/api/users');
      const users = await response.json();
      this.setState({ users, loading: false });
    } catch (error) {
      console.error('Failed to load users:', error);
      this.setState({ loading: false });
    }
  }
  
  handleDelete = (id) => {
    this.setState(prev => ({
      users: prev.users.filter(user => user.id !== id)
    }));
  };
  
  render() {
    const { users, loading } = this.state;
    
    if (loading) return html`<div>Loading users...</div>`;
    
    return html`<div class="user-list">
      <h2>Users ({users.length})</h2>
      <ul>
        ${users.map(user => html`
          <li key=${user.id}>
            <span>${user.name}</span>
            <button onClick=${() => this.handleDelete(user.id)}>Delete</button>
          </li>
        `)}
      </ul>
    </div>`;
  }
}
```

## Custom Hyperscript Functions

### Basic Custom h Function

htm is framework-agnostic and works with any hyperscript-compatible function:

```js
import htm from 'htm';

// Simple tree builder
function h(type, props, ...children) {
  return { type, props, children };
}

const html = htm.bind(h);

const result = html`<div id="main" class="container">Hello</div>`;
console.log(result);
// {
//   type: 'div',
//   props: { id: 'main', class: 'container' },
//   children: ['Hello']
// }
```

### HTML String Generator

```js
import htm from 'htm';

function toHtml(type, props, ...children) {
  if (typeof type !== 'string') {
    // Handle component by recursively calling
    return type({ ...props, children: children.map(c => 
      typeof c === 'object' ? toHtml(c.type, c.props, ...c.children) : c
    });
  }
  
  const propsString = props 
    ? Object.entries(props)
        .map(([key, value]) => ` ${key}="${value}"`)
        .join('')
    : '';
  
  const childrenString = children.map(c => 
    typeof c === 'object' ? toHtml(c.type, c.props, ...c.children) : c
  ).join('');
  
  return `<${type}${propsString}>${childrenString}</${type}>`;
}

const html = htm.bind(toHtml);

console.log(html`<div id="main"><p>Hello World</p></div>`);
// '<div id="main"><p>Hello World</p></div>'
```

### JSON Configuration Builder

```js
import htm from 'htm';

function toConfig(type, props, ...children) {
  if (!props && children.length === 0) {
    return type;
  }
  
  if (!props && children.length === 1) {
    return { [type]: children[0] };
  }
  
  const result = props ? { ...props } : {};
  
  if (children.length > 0) {
    result.children = children;
  }
  
  return { [type]: result };
}

const config = htm.bind(toConfig);

// Build webpack config with HTML-like syntax
const webpackConfig = config`
  <webpack mode="production" watch=${false}>
    <entry src="src/index.js" />
    <output path="dist" filename="bundle.js" />
    <module>
      <rule test="\.(js|jsx)$" use="babel-loader" />
    </module>
  </webpack>
`;

console.log(JSON.stringify(webpackConfig, null, 2));
```

### GraphQL Query Builder

```js
import htm from 'htm';

function toGql(type, props, ...children) {
  if (children.length === 0 && !props) {
    return type;
  }
  
  const fields = children.map(c => 
    typeof c === 'object' ? toGql(c.type, c.props, ...c.children) : c
  ).join(' ');
  
  const argumentsString = props 
    ? `(${Object.entries(props).map(([k, v]) => `${k}: ${JSON.stringify(v)}`).join(', ')})`
    : '';
  
  if (children.length === 0) {
    return `${type}${argumentsString}`;
  }
  
  return `${type}${argumentsString} {\n  ${fields}\n}`;
}

const gql = htm.bind(toGql);

const query = gql`
  query GetUser {
    user(id: "123") {
      name
      email
      posts(first: 10) {
        title
        content
      }
    }
  }
`;

console.log(query);
```

### CSS-in-JS Builder

```js
import htm from 'htm';

function toCss(selector, props, ...children) {
  const declarations = props 
    ? Object.entries(props).map(([prop, value]) => 
        `  ${camelToDash(prop)}: ${value};`
      ).join('\n')
    : '';
  
  const nestedRules = children.map(c => 
    typeof c === 'object' ? toCss(c.type, c.props, ...c.children) : c
  ).join('\n');
  
  if (nestedRules) {
    return `${selector} {\n${declarations}\n${nestedRules}\n}`;
  }
  
  return `${selector} {\n${declarations}\n}`;
}

function camelToDash(str) {
  return str.replace(/([A-Z])/g, '-$1').toLowerCase();
}

const css = htm.bind(toCss);

const styles = css`
  .button backgroundColor: "blue" color: "white" padding: "10px 20px":
    hover backgroundColor: "darkblue":
      active backgroundColor: "navy"
`;

console.log(styles);
```

## vhtml Integration (Server-Side Rendering)

### Basic SSR with vhtml

```js
import htm from 'htm';
import vhtml from 'vhtml';

const html = htm.bind(vhtml);

// Component
function UserCard({ user }) {
  return html`<div class="user-card">
    <h2>${user.name}</h2>
    <p>${user.bio}</p>
    <span class="status ${user.active ? 'active' : 'inactive'}">
      ${user.active ? 'Active' : 'Inactive'}
    </span>
  </div>`;
}

// Render to HTML string
const user = { name: 'John Doe', bio: 'Web Developer', active: true };
const htmlString = html`<${UserCard} user=${user} />`;

console.log(htmlString);
// '<div class="user-card"><h2>John Doe</h2><p>Web Developer</p>...'</div>'
```

### Full SSR Example with Express

```js
import express from 'express';
import htm from 'htm';
import vhtml from 'vhtml';

const html = htm.bind(vhtml);

// Components
function Head({ title }) {
  return html`<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>${title}</title>
  </head>`;
}

function Header({ user }) {
  return html`<header>
    <nav>
      <a href="/">Home</a>
      <a href="/about">About</a>
      ${user ? html`<a href="/profile">${user.name}</a>` : html`<a href="/login">Login</a>`}
    </nav>
  </header>`;
}

function Footer() {
  return html`<footer>
    <p>&copy; ${new Date().getFullYear()} My App</p>
  </footer>`;
}

function Layout({ title, user, children }) {
  return html`<!DOCTYPE html>
<html lang="en">
  <${Head} title=${title} />
  <body>
    <${Header} user=${user} />
    <main>${children}</main>
    <${Footer} />
  </body>
</html>`;
}

// Page component
function HomePage({ user }) {
  return html`<div class="home">
    <h1>Welcome${user ? `, ${user.name}!` : '!'}</h1>
    <p>This is the home page rendered on the server.</p>
  </div>`;
}

// Express route
const app = express();

app.get('/', (req, res) => {
  const user = req.session.user || null;
  
  const htmlString = html`<${Layout} title="Home" user=${user}>
    <${HomePage} user=${user} />
  <//>`;
  
  res.type('html').send(htmlString);
});

app.listen(3000, () => {
  console.log('SSR server running on http://localhost:3000');
});
```

### Partial SSR (Hydration)

```js
// Server-side rendering
import htm from 'htm';
import vhtml from 'vhtml';

const html = htm.bind(vhtml);

function Counter({ initialCount = 0 }) {
  return html`<div data-component="Counter" data-initial="${initialCount}">
    <p>Count: ${initialCount}</p>
    <button>Increment</button>
  </div>`;
}

// Render on server
const htmlString = html`<!DOCTYPE html>
<html>
<body>
  <${Counter} initialCount=5 />
  <script type="module" src="/app.js"></script>
</body>
</html>`;

// Client-side hydration (in app.js)
import { h, render } from 'preact';
import htmClient from 'htm';

const htmlClient = htmClient.bind(h);

function Counter({ initialCount = 0 }) {
  const [count, setCount] = useState(initialCount);
  
  return htmlClient`<div>
    <p>Count: ${count}</p>
    <button onClick=${() => setCount(c => c + 1)}>Increment</button>
  </div>`;
}

// Hydrate the server-rendered content
render(htmlClient`<${Counter} initialCount=5 />`, document.body);
```

## Other Framework Integrations

### Inferno Integration

```js
import { h, render } from 'inferno';
import htm from 'htm';

const html = htm.bind(h);

const App = () => html`<div>Inferno app with htm!</div>`;

render(html`<${App} />`, document.getElementById('app'));
```

### Vue 3 (Custom Renderer)

```js
import { createRenderer } from '@vue/runtime-core';
import htm from 'htm';

// Create custom renderer
const { render, createElement } = createRenderer({
  createElement: (tag, props, children) => ({ tag, props, children }),
  // ... other node ops
});

const html = htm.bind(createElement);

const result = html`<div id="app">Vue with htm</div>`;
```

### Custom Virtual DOM Implementations

```js
import htm from 'htm';

// Simple custom VDOM
function myH(type, props, ...children) {
  return {
    tagName: type,
    attributes: props || {},
    children: children.length === 1 ? children[0] : children
  };
}

const html = htm.bind(myH);

const vnode = html`<div class="container">
  <h1>Title</h1>
  <p>Content</p>
</div>`;

console.log(vnode);
// {
//   tagName: 'div',
//   attributes: { class: 'container' },
//   children: [
//     { tagName: 'h1', attributes: null, children: 'Title' },
//     { tagName: 'p', attributes: null, children: 'Content' }
//   ]
// }
```

## CDN Usage Examples

### unpkg CDN

```html
<!-- Preact standalone -->
<script type="module">
  import { html, render, useState } from 
    'https://unpkg.com/htm/preact/standalone.module.js';
  
  function App() {
    const [count, setCount] = useState(0);
    return html`<div>Count: ${count} <button onClick=${() => setCount(c => c + 1)}>+</button></div>`;
  }
  
  render(html`<${App} />`, document.body);
</script>

<!-- React standalone -->
<script type="module">
  import { html } from 'https://unpkg.com/htm/react?module';
  import React from 'https://unpkg.com/react?module';
  import ReactDOM from 'https://unpkg.com/react-dom?module';
  
  const App = () => html`<div>React app</div>`;
  ReactDOM.createRoot(document.getElementById('root')).render(html`<${App} />`);
</script>
```

### jsDelivr CDN

```html
<script type="module">
  import { html, render } from 
    'https://cdn.jsdelivr.net/npm/htm/preact/standalone.module.js';
  
  const App = () => html`<div>jsDelivr CDN example</div>`;
  render(html`<${App} />`, document.body);
</script>
```

## Migration from JSX

### Syntax Mapping

| JSX | htm |
|-----|-----|
| `<div />` | `<div />` |
| `<div className="foo" />` | `<div class=foo />` |
| `<Component prop={value} />` | `<${Component} prop=${value} />` |
| `{...props}` | `...${props}` |
| `{/* comment */}` | `<!-- comment -->` |
| `<Fragment>` or `<>` | Multiple roots (no wrapper needed) |
| `</Component>` | `<//>` or `</Component>` |

### Before and After Examples

**JSX:**
```jsx
function App({ user, children }) {
  const [count, setCount] = useState(0);
  
  return (
    <div className="app">
      <Header user={user} />
      <div className="content">
        {children}
      </div>
      <button onClick={() => setCount(c => c + 1)}>
        Count: {count}
      </button>
      {/* This is a comment */}
    </div>
  );
}
```

**htm:**
```js
function App({ user, children }) {
  const [count, setCount] = useState(0);
  
  return html`<div class="app">
    <${Header} user=${user} />
    <div class="content">
      ${children}
    </div>
    <button onClick=${() => setCount(c => c + 1)}>
      Count: ${count}
    </button>
    <!-- This is a comment -->
  </div>`;
}
```

See [Migration Guide](references/05-migration-guide.md) for complete migration instructions.
