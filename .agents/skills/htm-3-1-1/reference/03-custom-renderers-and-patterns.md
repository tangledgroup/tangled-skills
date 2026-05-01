# Custom Renderers and Patterns

## The Hyperscript Contract

htm is framework-agnostic because it only requires a function matching the hyperscript pattern:

```js
h(type, props, ...children) => any
```

- `type` — A string (HTML tag name) or a component function
- `props` — An object of attributes/properties, or `null`
- `...children` — Zero or more children (strings, values, or nested VNodes)

htm never inspects the return value of `h`. This means you can bind it to anything that accepts this signature.

## Binding to Custom Renderers

### String HTML Output (vhtml)

[vhtml](https://github.com/developit/vhtml) converts hyperscript calls to HTML strings:

```js
import htm from 'htm';
import vhtml from 'vhtml';

const html = htm.bind(vhtml);

console.log(html`<h1 id=hello>Hello world!</h1>`);
// '<h1 id="hello">Hello world!</h1>'
```

### Object Configuration (jsxobj)

[jsxobj](https://github.com/developit/jsxobj) converts hyperscript to nested JavaScript objects:

```js
import htm from 'htm';
import jsxobj from 'jsxobj';

const html = htm.bind(jsxobj);

console.log(html`
  <webpack watch mode=production>
    <entry path="src/index.js" />
  </webpack>
`);
// {
//   watch: true,
//   mode: 'production',
//   entry: { path: 'src/index.js' }
// }
```

### Custom Tree Builder

Build your own data structure:

```js
import htm from 'htm';

function h(type, props, ...children) {
  return { type, props, children };
}

const html = htm.bind(h);

console.log(html`<h1 id=hello>Hello world!</h1>`);
// { type: 'h1', props: { id: 'hello' }, children: ['Hello world!'] }
```

### DOM Creation

Direct DOM manipulation without Virtual DOM:

```js
import htm from 'htm';

function h(type, props, ...children) {
  const el = document.createElement(type);
  if (props) {
    for (const [key, value] of Object.entries(props)) {
      if (value === true) {
        el.setAttribute(key, '');
      } else {
        el.setAttribute(key, value);
      }
    }
  }
  for (const child of children) {
    if (typeof child === 'string') {
      el.appendChild(document.createTextNode(child));
    } else if (child instanceof Node) {
      el.appendChild(child);
    }
  }
  return el;
}

const html = htm.bind(h);

document.body.appendChild(
  html`<h1 id=title>Hello World</h1>`
);
```

## Server-Side Rendering Patterns

### SSR with vhtml

vhtml produces HTML strings, making it ideal for server-side rendering:

```js
import htm from 'htm';
import vhtml from 'vhtml';

const html = htm.bind(vhtml);

function Page({ title, body }) {
  return html`
    <!DOCTYPE html>
    <html>
      <head><title>${title}</title></head>
      <body>${body}</body>
    </html>
  `;
}

// On the server:
const response = Page({ title: 'Hello', body: '<p>World</p>' });
// Returns a complete HTML string
```

### SSR with Preact

htm works with Preact's `render` function for SSR via `preact-render-to-string`:

```js
import { html } from 'htm/preact';
import renderToString from 'preact-render-to-string';

const App = () => html`<h1>Hello from server</h1>`;
const htmlString = renderToString(html`<${App} />`);
```

## Caching Behavior

### Default Build (with caching)

The default htm build caches template strings. This means identical templates can return the same JavaScript object at multiple points in the tree, enabling efficient comparison and deduplication:

```js
import htm from 'htm';
const html = htm.bind(h);

const a = html`<div>Hello</div>`;
const b = html`<div>Hello</div>`;
// a === b (same cached object)
```

### Disabling Caching

Three options to disable caching:

**Option 1**: Use `htm/mini`, which disables caching by default:

```js
import htm from 'htm/mini';
```

**Option 2**: Add `this[0] = 3;` at the beginning of your `h` function:

```js
function h(type, props, ...children) {
  this[0] = 3;  // Disables caching for this element
  return { type, props, children };
}
```

**Option 3**: Make your `h` function copy nodes when needed:

```js
function h(type, props, ...children) {
  return {
    type,
    props: props ? { ...props } : null,
    children: [...children]
  };
}
```

### htm/mini

The `htm/mini` variant (~450 bytes) disables caching and uses a simpler internal representation. Use it when you don't need the caching optimization:

```js
import htm from 'htm/mini';
const html = htm.bind(h);
```

## Standalone Preact Bundle

The `htm/preact/standalone` entry point bundles htm + Preact + Preact hooks into a single import. This is ideal for zero-config browser development:

```html
<!DOCTYPE html>
<html lang="en">
  <title>htm Demo</title>
  <script type="module">
    import { html, Component, render } from 'https://unpkg.com/htm/preact/standalone.module.js';

    class App extends Component {
      addTodo() {
        const { todos = [] } = this.state;
        this.setState({ todos: todos.concat(`Item ${todos.length}`) });
      }
      render({ page }, { todos = [] }) {
        return html`
          <div class="app">
            <${Header} name="ToDo's (${page})" />
            <ul>
              ${todos.map(todo => html`
                <li key=${todo}>${todo}</li>
              `)}
            </ul>
            <button onClick=${() => this.addTodo()}>Add Todo</button>
            <${Footer}>footer content here<//>
          </div>
        `;
      }
    }

    const Header = ({ name }) => html`<h1>${name} List</h1>`;
    const Footer = props => html`<footer ...${props} />`;

    render(html`<${App} page="All" />`, document.body);
  </script>
</html>
```

The standalone bundle exports: `h`, `html`, `render`, `Component`, `createContext`, `createRef`, and all Preact hooks (`useState`, `useReducer`, `useEffect`, `useLayoutEffect`, `useRef`, `useImperativeHandle`, `useMemo`, `useCallback`, `useContext`, `useDebugValue`, `useErrorBoundary`).

## TypeScript Support

htm provides TypeScript declarations:

```ts
declare const htm: {
  bind<HResult>(
    h: (type: any, props: Record<string, any>, ...children: any[]) => HResult
  ): (strings: TemplateStringsArray, ...values: any[]) => HResult | HResult[];
};
export default htm;
```

For the Preact integration:

```ts
import { h, VNode, Component } from 'preact';
export * from 'preact/hooks';
declare function render(tree: VNode, parent: HTMLElement): void;
declare const html: (strings: TemplateStringsArray, ...values: any[]) => VNode;
export { h, html, render, Component };
```

## Package Exports

htm provides multiple entry points via conditional exports:

- `htm` — Main library (with caching)
- `htm/mini` — Minimal variant (no caching, ~450 bytes)
- `htm/preact` — Pre-bound to Preact's `h`
- `htm/preact/standalone` — Preact + hooks + htm bundled together
- `htm/react` — Pre-bound to React's `createElement`

Each entry point supports ESM (`import`), CommonJS (`require`), UMD, and browser module formats.
