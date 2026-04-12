# Migrating from JSX to htm

Complete guide for migrating React/Preact applications from JSX to htm syntax.

## Why Migrate to htm?

### Benefits

1. **No Build Tool Required** - Works directly in browsers with ES modules
2. **Smaller Bundle Size** - Compile away with babel-plugin-htm (0 bytes runtime)
3. **Better DX for Prototyping** - Edit HTML files directly, no compilation step
4. **Server-Side Rendering** - Easier SSR without special JSX configuration
5. **Native JavaScript** - Uses standard tagged templates, not syntax extensions

### Trade-offs

1. **Spread Syntax** - `...${props}` instead of `{...props}`
2. **Component Tags** - `<${Component}>` instead of `<Component>`
3. **Comments** - `<!-- -->` instead of `{/* */}`
4. **Learning Curve** - Team needs to learn new syntax

## Syntax Comparison

### Element Syntax

| Feature | JSX | htm |
|---------|-----|-----|
| Self-closing | `<div />` | `<div />` |
| Attributes | `<div className="foo" />` | `<div class=foo />` |
| Quotes | Required | Optional for static values |
| Boolean attrs | `<input disabled />` | `<input disabled />` |

### Dynamic Values

| Feature | JSX | htm |
|---------|-----|-----|
| Interpolation | `{value}` | `${value}` |
| Expressions | `{a + b}` | `${a + b}` |
| Functions | `{() => handler()}` | `${() => handler()}` |

### Components

| Feature | JSX | htm |
|---------|-----|-----|
| Component tag | `<Component />` | `<${Component} />` |
| Props | `<Comp prop={val} />` | `<${Comp} prop=${val} />` |
| Children | `<Comp>text</Comp>` | `<${Comp}>text<//>` or `</Comp>` |

### Other Features

| Feature | JSX | htm |
|---------|-----|-----|
| Spread props | `{...props}` | `...${props}` |
| Comments | `{/* comment */}` | `<!-- comment -->` |
| Fragments | `<Fragment>` or `<>` | Multiple roots (no wrapper) |
| Conditional | `{cond && <div />}` | `${cond && html`<div />`}` |

## Step-by-Step Migration

### Step 1: Set Up htm

Install htm and configure for your framework:

```bash
npm install htm
```

**For Preact:**
```js
import { h } from 'preact';
import htm from 'htm';

const html = htm.bind(h);
export { html };
```

**For React:**
```js
import React from 'react';
import htm from 'htm';

const html = htm.bind(React.createElement);
export { html };
```

### Step 2: Migrate Simple Components

**Before (JSX):**
```jsx
function Header({ title }) {
  return (
    <header className="header">
      <h1>{title}</h1>
      <nav>
        <a href="/">Home</a>
        <a href="/about">About</a>
      </nav>
    </header>
  );
}
```

**After (htm):**
```js
function Header({ title }) {
  return html`<header class="header">
    <h1>${title}</h1>
    <nav>
      <a href="/">Home</a>
      <a href="/about">About</a>
    </nav>
  </header>`;
}
```

**Key changes:**
- Wrap template in `html` tagged template
- `{title}` → `${title}`
- `className` → `class` (use standard HTML attribute names)
- Remove parentheses wrapper

### Step 3: Migrate Components with Props Spreading

**Before (JSX):**
```jsx
function UserCard({ user, ...restProps }) {
  return (
    <div className="card" {...restProps}>
      <h2>{user.name}</h2>
      <p>{user.bio}</p>
    </div>
  );
}
```

**After (htm):**
```js
function UserCard({ user, ...restProps }) {
  return html`<div class="card" ...${restProps}>
    <h2>${user.name}</h2>
    <p>${user.bio}</p>
  </div>`;
}
```

**Key changes:**
- `{...restProps}` → `...${restProps}`
- Note the different position: before the closing `>`

### Step 4: Migrate Components with Children

**Before (JSX):**
```jsx
function Card({ title, children }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      <div className="content">{children}</div>
    </div>
  );
}

// Usage:
<Card title="Welcome">
  <p>Card content here</p>
</Card>
```

**After (htm):**
```js
function Card({ title, children }) {
  return html`<div class="card">
    <h2>${title}</h2>
    <div class="content">${children}</div>
  </div>`;
}

// Usage:
html`<${Card} title="Welcome">
  <p>Card content here</p>
<//>`;
```

**Key changes:**
- Component tag: `<Card>` → `<${Card}>`
- Closing tag: `</Card>` → `<//>` (or keep `</Card>`, both work)
- Children interpolation: `{children}` → `${children}`

### Step 5: Migrate Conditional Rendering

**Before (JSX):**
```jsx
function UserDisplay({ user }) {
  return (
    <div>
      {user ? (
        <h1>Welcome, {user.name}!</h1>
      ) : (
        <p>Please log in</p>
      )}
      
      {user && user.isAdmin && (
        <AdminPanel />
      )}
      
      {/* Show count if greater than zero */}
      {user.messageCount > 0 && (
        <span>{user.messageCount} new messages</span>
      )}
    </div>
  );
}
```

**After (htm):**
```js
function UserDisplay({ user }) {
  return html`<div>
    ${user 
      ? html`<h1>Welcome, ${user.name}!</h1>`
      : html`<p>Please log in</p>`
    }
    
    ${user && user.isAdmin && html`<${AdminPanel} />`}
    
    <!-- Show count if greater than zero -->
    ${user.messageCount > 0 && html`<span>${user.messageCount} new messages</span>`}
  </div>`;
}
```

**Key changes:**
- Conditional elements need their own `html` tagged template
- Comments: `{/* */}` → `<!-- -->`
- Each branch of ternary needs `html``...`` wrapper

### Step 6: Migrate List Rendering

**Before (JSX):**
```jsx
function TodoList({ todos }) {
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id} className={todo.completed ? 'completed' : ''}>
          <input 
            type="checkbox" 
            checked={todo.completed}
            onChange={() => toggleTodo(todo.id)}
          />
          <span>{todo.text}</span>
          <button onClick={() => deleteTodo(todo.id)}>Delete</button>
        </li>
      ))}
    </ul>
  );
}
```

**After (htm):**
```js
function TodoList({ todos }) {
  return html`<ul>
    ${todos.map(todo => html`<li 
      class=${todo.completed ? 'completed' : ''}
      key=${todo.id}>
      <input 
        type="checkbox" 
        checked=${todo.completed}
        onChange=${() => toggleTodo(todo.id)}
      />
      <span>${todo.text}</span>
      <button onClick=${() => deleteTodo(todo.id)}>Delete</button>
    </li>`)}
  </ul>`;
}
```

**Key changes:**
- Each mapped element needs its own `html` tagged template
- Inline event handlers: `{() => fn()}` → `${() => fn()}`

### Step 7: Migrate Components with State

**Before (JSX - React):**
```jsx
function Counter() {
  const [count, setCount] = useState(0);
  
  const increment = () => setCount(c => c + 1);
  const decrement = () => setCount(c => c - 1);
  
  return (
    <div className="counter">
      <p>Count: {count}</p>
      <button onClick={decrement}>-</button>
      <button onClick={increment}>+</button>
      <button onClick={() => setCount(0)}>Reset</button>
    </div>
  );
}
```

**After (htm - React):**
```js
function Counter() {
  const [count, setCount] = useState(0);
  
  const increment = () => setCount(c => c + 1);
  const decrement = () => setCount(c => c - 1);
  
  return html`<div class="counter">
    <p>Count: ${count}</p>
    <button onClick=${decrement}>-</button>
    <button onClick=${increment}>+</button>
    <button onClick=${() => setCount(0)}>Reset</button>
  </div>`;
}
```

**Key changes:**
- Same hooks API, just different template syntax
- Interpolated values: `{count}` → `${count}`

### Step 8: Migrate Class Components

**Before (JSX):**
```jsx
class UserForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = { name: '', email: '' };
  }
  
  handleChange = (e) => {
    const { name, value } = e.target;
    this.setState({ [name]: value });
  };
  
  handleSubmit = (e) => {
    e.preventDefault();
    this.props.onSubmit(this.state);
  };
  
  render() {
    const { name, email } = this.state;
    
    return (
      <form onSubmit={this.handleSubmit}>
        <input 
          type="text" 
          name="name"
          value={name}
          onChange={this.handleChange}
          placeholder="Name"
        />
        <input 
          type="email" 
          name="email"
          value={email}
          onChange={this.handleChange}
          placeholder="Email"
        />
        <button type="submit">Submit</button>
      </form>
    );
  }
}
```

**After (htm):**
```js
class UserForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = { name: '', email: '' };
  }
  
  handleChange = (e) => {
    const { name, value } = e.target;
    this.setState({ [name]: value });
  };
  
  handleSubmit = (e) => {
    e.preventDefault();
    this.props.onSubmit(this.state);
  };
  
  render() {
    const { name, email } = this.state;
    
    return html`<form onSubmit=${this.handleSubmit}>
      <input 
        type="text" 
        name="name"
        value=${name}
        onChange=${this.handleChange}
        placeholder="Name"
      />
      <input 
        type="email" 
        name="email"
        value=${email}
        onChange=${this.handleChange}
        placeholder="Email"
      />
      <button type="submit">Submit</button>
    </form>`;
  }
}
```

### Step 9: Migrate Context Usage

**Before (JSX):**
```jsx
const ThemeContext = React.createContext('light');

function ThemedButton() {
  const theme = useContext(ThemeContext);
  
  return (
    <button className={`btn-${theme}`}>
      Themed Button
    </button>
  );
}

function App() {
  const [theme, setTheme] = useState('light');
  
  return (
    <ThemeContext.Provider value={theme}>
      <div className="app">
        <button onClick={() => setTheme(t => t === 'light' ? 'dark' : 'light')}>
          Toggle Theme
        </button>
        <ThemedButton />
      </div>
    </ThemeContext.Provider>
  );
}
```

**After (htm):**
```js
const ThemeContext = React.createContext('light');

function ThemedButton() {
  const theme = useContext(ThemeContext);
  
  return html`<button class={`btn-${theme}`}>
    Themed Button
  </button>`;
}

function App() {
  const [theme, setTheme] = useState('light');
  
  return html`<${ThemeContext.Provider} value=${theme}>
    <div class="app">
      <button onClick=${() => setTheme(t => t === 'light' ? 'dark' : 'light')}>
        Toggle Theme
      </button>
      <${ThemedButton} />
    </div>
  <//>`;
}
```

### Step 10: Migrate Fragments

**Before (JSX):**
```jsx
function Row({ label, value }) {
  return (
    <>
      <dt>{label}</dt>
      <dd>{value}</dd>
    </>
  );
}

// Or with explicit Fragment:
return (
  <Fragment>
    <dt>{label}</dt>
    <dd>{value}</dd>
  </Fragment>
);
```

**After (htm):**
```js
function Row({ label, value }) {
  return html`
    <dt>${label}</dt>
    <dd>${value}</dd>
  `;
}
```

**Key changes:**
- htm supports multiple root elements natively
- No need for `<Fragment>` or `<>` wrappers
- Multiple roots return an array automatically

## Common Patterns Migration

### Event Handlers

**JSX:**
```jsx
<button onClick={handleClick}>Click</button>
<button onClick={() => handleItemClick(id)}>Click</button>
<input onChange={this.handleChange} />
```

**htm:**
```js
html`<button onClick=${handleClick}>Click</button>`;
html`<button onClick=${() => handleItemClick(id)}>Click</button>`;
html`<input onChange=${this.handleChange} />`;
```

### Dynamic Class Names

**JSX:**
```jsx
<div className={`btn btn-${size} ${disabled ? 'disabled' : ''}`} />
<div className={classNames('btn', { disabled })} />
```

**htm:**
```js
html`<div class={`btn btn-${size} ${disabled ? 'disabled' : ''}`}`;
html`<div class=${classNames('btn', { disabled })}>`;
```

### Inline Styles

**JSX:**
```jsx
<div style={{ color: 'red', fontSize: '16px' }} />
<div style={{ ...baseStyles, ...overrideStyles }} />
```

**htm:**
```js
html`<div style=${{ color: 'red', fontSize: '16px' }}>`;
html`<div style=${{ ...baseStyles, ...overrideStyles }}>`;
```

### Refs

**JSX (React):**
```jsx
function Input() {
  const inputRef = useRef(null);
  
  return (
    <input ref={inputRef} type="text" />
  );
}
```

**htm (React):**
```js
function Input() {
  const inputRef = useRef(null);
  
  return html`<input ref=${inputRef} type="text" />`;
}
```

## Migration Checklist

- [ ] Install htm package
- [ ] Create html export bound to framework's createElement/h function
- [ ] Update import statements in component files
- [ ] Convert `{interpolation}` to `${interpolation}`
- [ ] Convert `<Component>` to `<${Component}>`
- [ ] Convert `{...props}` to `...${props}`
- [ ] Convert `{/* comments */}` to `<!-- comments -->`
- [ ] Remove `<Fragment>` wrappers (use multiple roots)
- [ ] Update className to class (React only)
- [ ] Add html`` wrapper around conditional elements
- [ ] Add html`` wrapper around map callbacks
- [ ] Test all components for functionality
- [ ] Check event handlers are working
- [ ] Verify state updates work correctly
- [ ] Test prop passing and spreading
- [ ] Review and fix any syntax errors

## Automated Migration (Find & Replace)

### Basic Regex Replacements

**Note:** Use with caution - manual review required!

```bash
# Replace interpolation braces (be careful with nested cases)
# {value} -> ${value}
sed -i 's/{\([a-zA-Z_][a-zA-Z0-9_]*\)}/$\1/g' file.js

# Replace component tags
# <Component -> <${Component}
sed -i 's/<\([A-Z][a-zA-Z0-9_]*\)/<\${\1}/g' file.js

# Replace spread props
# {...props} -> ...${props}
sed -i 's/{\.\.\.\([^}]*\)}/\.\.\.${\1}/g' file.js

# Replace comments
# {/* comment */} -> <!-- comment -->
sed -i 's/{\/\*\(.*\)\*\/}/<!-- \1 -->/g' file.js
```

### Using sed for Simple Files

```bash
# Backup original
cp component.jsx component.jsx.bak

# Apply transformations
sed -E \
  -e 's/\{([a-zA-Z_][a-zA-Z0-9_]*)\}/$\1/g' \
  -e 's/<([A-Z][a-zA-Z0-9_]*)/\${\1}/g' \
  -e 's/\{\.\.\.([^}]*)\}/\.\.\.$\1/g' \
  component.jsx.bak > component.js
```

## Testing After Migration

### Visual Regression Testing

```js
// Test that components render correctly
import { html } from 'htm/preact';
import { mount } from 'enzyme';
import App from './App';

describe('Migrated Components', () => {
  it('renders without errors', () => {
    const wrapper = mount(html`<${App} />`);
    expect(wrapper.exists()).toBe(true);
  });
  
  it('displays correct content', () => {
    const wrapper = mount(html`<${App} />`);
    expect(wrapper.text()).toContain('Expected text');
  });
});
```

### Manual Testing Checklist

- [ ] All components render without errors
- [ ] Interactive elements (buttons, inputs) work correctly
- [ ] State updates trigger re-renders
- [ ] Props are passed correctly between components
- [ ] Event handlers receive correct parameters
- [ ] Conditional rendering shows/hides elements properly
- [ ] List rendering displays all items
- [ ] Forms submit with correct data
- [ ] Navigation/routing works (if applicable)
- [ ] API calls and data fetching work

## Rollback Strategy

If issues arise, maintain ability to rollback:

1. **Keep JSX files in git history** - Don't squash commits during migration
2. **Migrate incrementally** - One component at a time
3. **Feature flag new syntax** - Allow toggling between old and new
4. **Keep both imports temporarily:**
   ```js
   import { html } from 'htm/preact';
   // Keep JSX working during transition
   ```

## Common Pitfalls

### Missing html`` Wrapper

**Wrong:**
```js
function Component() {
  return <div>Missing html tagged template</div>;
}
```

**Right:**
```js
function Component() {
  return html`<div>Has html tagged template</div>`;
}
```

### Incorrect Spread Syntax

**Wrong (JSX syntax):**
```js
html`<div {...props}>`;  // This won't work!
```

**Right:**
```js
html`<div ...${props}>`;  // Correct htm syntax
```

### Forgetting to Interpolate Components

**Wrong:**
```js
html`<ChildComponent prop="value" />`;  // Treated as string "ChildComponent"
```

**Right:**
```js
html`<${ChildComponent} prop="value" />`;  // Correct component reference
```

### Missing html`` in Conditionals

**Wrong:**
```js
html`<div>
  {condition && <Child />}  // Won't work - needs html wrapper
</div>`;
```

**Right:**
```js
html`<div>
  ${condition && html`<${Child} />`}
</div>`;
```

## Performance Considerations

### After Migration

1. **Bundle Size** - Should decrease (no JSX transform overhead)
2. **Runtime Performance** - Similar to JSX (both compile to hyperscript)
3. **Development Speed** - Faster iteration (no build step needed for browser dev)

### Optimization Tips

- Use `htm/mini` for smallest size (no caching)
- Consider babel-plugin-htm for production builds
- Enable template caching for static content
- Memoize components that re-render frequently

## Resources

- [htm GitHub Repository](https://github.com/developit/htm)
- [babel-plugin-htm Documentation](references/04-babel-plugin.md)
- [Preact Integration Guide](references/03-integrations.md)
- [React Integration Guide](references/03-integrations.md)
