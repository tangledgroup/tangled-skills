# htm Advanced Features

Advanced patterns, state management, and optimization techniques for htm.

## State Management Patterns

### Preact State with htm

```js
import { Component, h, render } from 'preact';
import htm from 'htm';

const html = htm.bind(h);

class TodoApp extends Component {
  state = {
    todos: [],
    filter: 'all'
  };
  
  addTodo = () => {
    const text = prompt('New todo:');
    if (text) {
      this.setState({
        todos: [...this.state.todos, { id: Date.now(), text, done: false }]
      });
    }
  };
  
  toggleTodo = (id) => {
    this.setState({
      todos: this.state.todos.map(todo =>
        todo.id === id ? { ...todo, done: !todo.done } : todo
      )
    });
  };
  
  deleteTodo = (id) => {
    this.setState({
      todos: this.state.todos.filter(todo => todo.id !== id)
    });
  };
  
  getFilteredTodos() {
    const { todos, filter } = this.state;
    switch (filter) {
      case 'active': return todos.filter(t => !t.done);
      case 'completed': return todos.filter(t => t.done);
      default: return todos;
    }
  }
  
  render() {
    const filteredTodos = this.getFilteredTodos();
    
    return html`<div class="todo-app">
      <h1>Todo List</h1>
      
      <div class="input-row">
        <input 
          type="text" 
          placeholder="New todo..."
          onKeyup=${(e) => e.key === 'Enter' && this.addTodo()}
        />
        <button onClick=${this.addTodo}>Add</button>
      </div>
      
      <div class="filters">
        <button 
          class=${this.state.filter === 'all' ? 'active' : ''}
          onClick=${() => this.setState({ filter: 'all' })}>
          All
        </button>
        <button 
          class=${this.state.filter === 'active' ? 'active' : ''}
          onClick=${() => this.setState({ filter: 'active' })}>
          Active
        </button>
        <button 
          class=${this.state.filter === 'completed' ? 'active' : ''}
          onClick=${() => this.setState({ filter: 'completed' })}>
          Completed
        </button>
      </div>
      
      <ul class="todos">
        ${filteredTodos.map(todo => html`
          <li class=${todo.done ? 'done' : ''}>
            <input 
              type="checkbox" 
              checked=${todo.done}
              onChange=${() => this.toggleTodo(todo.id)}
            />
            <span>${todo.text}</span>
            <button onClick=${() => this.deleteTodo(todo.id)}>×</button>
          </li>
        `)}
      </ul>
      
      <p class="summary">
        ${filteredTodos.length} of ${this.state.todos.length} todos
      </p>
    </div>`;
  }
}

render(html`<${TodoApp} />`, document.getElementById('app'));
```

### React Hooks with htm

```js
import { useState, useEffect, useCallback } from 'react';
import { html } from 'htm/react';

function Counter() {
  const [count, setCount] = useState(0);
  
  // Memoized callback to prevent unnecessary re-renders
  const increment = useCallback(() => {
    setCount(c => c + 1);
  }, []);
  
  return html`<div>
    <p>Count: ${count}</p>
    <button onClick=${increment}>+</button>
    <button onClick=${() => setCount(0)}>Reset</button>
  </div>`;
}

function UseEffectDemo() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch('/api/data');
        const json = await response.json();
        setData(json);
      } finally {
        setLoading(false);
      }
    }
    
    fetchData();
  }, []);
  
  if (loading) return html`<div>Loading...</div>`;
  
  return html`<div>
    <h2>Data Loaded</h2>
    <pre>${JSON.stringify(data, null, 2)}</pre>
  </div>`;
}
```

### Custom Hooks with htm

```js
import { useState, useEffect } from 'react';
import { html } from 'htm/react';

// Custom hook for local storage persistence
function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(error);
      return initialValue;
    }
  });
  
  const setValue = (value) => {
    try {
      const valueToStore = value instanceof Function 
        ? value(storedValue) 
        : value;
      
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(error);
    }
  };
  
  return [storedValue, setValue];
}

// Usage
function ThemeToggle() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');
  
  useEffect(() => {
    document.body.className = theme;
  }, [theme]);
  
  return html`<button 
    class="theme-toggle"
    onClick=${() => setTheme(t => t === 'light' ? 'dark' : 'light')}>
    Toggle to ${theme === 'light' ? 'dark' : 'light'} mode
  </button>`;
}
```

## Form Handling Patterns

### Controlled Components

```js
import { useState } from 'preact/hooks';
import { html } from 'htm/preact';

function LoginForm() {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    remember: false
  });
  
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
  };
  
  return html`<form onSubmit=${handleSubmit}>
    <div>
      <label>Username:</label>
      <input 
        type="text" 
        name="username"
        value=${formData.username}
        onInput=${handleChange}
        required
      />
    </div>
    
    <div>
      <label>Password:</label>
      <input 
        type="password" 
        name="password"
        value=${formData.password}
        onInput=${handleChange}
        required
      />
    </div>
    
    <div>
      <label>
        <input 
          type="checkbox" 
          name="remember"
          checked=${formData.remember}
          onChange=${handleChange}
        />
        Remember me
      </label>
    </div>
    
    <button type="submit">Login</button>
  </form>`;
}
```

### Form Validation

```js
import { useState } from 'preact/hooks';
import { html } from 'htm/preact';

function ValidatedForm() {
  const [formData, setFormData] = useState({ email: '', age: '' });
  const [errors, setErrors] = useState({});
  
  const validate = (name, value) => {
    switch (name) {
      case 'email':
        if (!value) return 'Email is required';
        if (!/\S+@\S+\.\S+/.test(value)) return 'Invalid email format';
        break;
      case 'age':
        if (!value) return 'Age is required';
        const num = parseInt(value, 10);
        if (isNaN(num) || num < 0 || num > 150) return 'Invalid age';
        break;
    }
    return '';
  };
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    const error = validate(name, value);
    
    setFormData(prev => ({ ...prev, [name]: value }));
    setErrors(prev => ({ ...prev, [name]: error }));
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    const hasErrors = Object.values(errors).some(Boolean);
    
    if (!hasErrors) {
      console.log('Valid form data:', formData);
    }
  };
  
  return html`<form onSubmit=${handleSubmit} noValidate>
    <div class=${errors.email ? 'error' : ''}>
      <label>Email:</label>
      <input 
        type="email" 
        name="email"
        value=${formData.email}
        onInput=${handleChange}
      />
      ${errors.email && html`<span class="error-msg">${errors.email}</span>`}
    </div>
    
    <div class=${errors.age ? 'error' : ''}>
      <label>Age:</label>
      <input 
        type="text" 
        name="age"
        value=${formData.age}
        onInput=${handleChange}
      />
      ${errors.age && html`<span class="error-msg">${errors.age}</span>`}
    </div>
    
    <button type="submit" disabled=${Object.values(errors).some(Boolean)}>
      Submit
    </button>
  </form>`;
}
```

## Conditional Rendering Patterns

### Ternary Expressions

```js
const UserGreeting = ({ user }) => html`<div>
  ${user 
    ? html`<h1>Welcome back, ${user.name}!</h1>`
    : html`<p>Please log in to continue</p>`
  }
</div>`;
```

### Logical AND for Conditionals

```js
const AdminPanel = ({ isAdmin, children }) => html`<div>
  <h2>Main Content</h2>
  
  ${isAdmin && html`<div class="admin-controls">${children}</div>`}
  
  ${isAdmin && html`<AdminSettings />`}
  
  ${!isAdmin && html`<p>Some features require admin access</p>`}
</div>`;
```

### Nullish Coalescing for Defaults

```js
const Profile = ({ user, loading }) => {
  if (loading) return html`<Spinner />`;
  
  const displayName = user?.name ?? 'Anonymous';
  const avatarUrl = user?.avatar ?? '/default-avatar.png';
  
  return html`<div class="profile">
    <img src=${avatarUrl} alt=${displayName} />
    <h2>${displayName}</h2>
    ${user?.bio && html`<p>${user.bio}</p>`}
  </div>`;
};
```

### Early Returns for Complex Conditions

```js
const Dashboard = ({ user, permissions, loading, error }) => {
  if (loading) return html`<LoadingScreen />`;
  
  if (error) return html`<ErrorMessage message=${error} />`;
  
  if (!user) return html`<LoginPrompt />`;
  
  if (!permissions?.canAccessDashboard) {
    return html`<UnauthorizedMessage />`;
  }
  
  // Main dashboard content
  return html`<div class="dashboard">
    <${Header} user=${user} />
    <${StatsWidget} data=${user.stats} />
    <${RecentActivity} activities=${user.activities} />
    <${SettingsPanel} permissions=${permissions} />
  </div>`;
};
```

## List Rendering Patterns

### Basic Map

```js
const ItemList = ({ items }) => html`<ul>
  ${items.map(item => html`<li key=${item.id}>${item.name}</li>`)}
</ul>`;
```

### Map with Index

```js
const NumberedList = ({ items }) => html`<ol>
  ${items.map((item, index) => html`
    <li key=${index}>
      <span class="number">${index + 1}.</span>
      ${item.text}
    </li>
  `)}
</ol>`;
```

### Map with Multiple Elements per Item

```js
const CardList = ({ cards }) => html`<div class="card-grid">
  ${cards.map(card => html`
    <div class="card" key=${card.id}>
      <img src=${card.image} alt=${card.title} />
      <h3>${card.title}</h3>
      <p>${card.description}</p>
      <button onClick=${() => handleSelect(card)}>Select</button>
    </div>
  `)}
</div>`;
```

### Map with Separators

```js
const TagList = ({ tags }) => html`<div class="tags">
  ${tags.map((tag, index) => [
    html`<span class="tag" key=${tag.id}>${tag.name}</span>`,
    index < tags.length - 1 && html`<span class="separator" key={`sep-${index}`}> • </span>`
  ])}
</div>`;
```

### Paginated Lists

```js
const PaginatedList = ({ items, pageSize = 10 }) => {
  const [page, setPage] = useState(0);
  
  const totalPages = Math.ceil(items.length / pageSize);
  const startIndex = page * pageSize;
  const endIndex = startIndex + pageSize;
  const currentItems = items.slice(startIndex, endIndex);
  
  return html`<div>
    <ul>
      ${currentItems.map(item => html`<li key=${item.id}>${item.name}</li>`)}
    </ul>
    
    <div class="pagination">
      <button 
        onClick=${() => setPage(p => Math.max(0, p - 1))}
        disabled=${page === 0}>
        Previous
      </button>
      
      <span>Page ${page + 1} of ${totalPages}</span>
      
      <button 
        onClick=${() => setPage(p => Math.min(totalPages - 1, p + 1))}
        disabled=${page === totalPages - 1}>
        Next
      </button>
    </div>
  </div>`;
};
```

## Performance Optimization

### Memoization with Components

```js
import { memo } from 'preact';
import { html } from 'htm/preact';

// Memoize component to prevent unnecessary re-renders
const ExpensiveWidget = memo(({ data, config }) => {
  console.log('Rendering ExpensiveWidget');
  
  // Heavy computation here
  const processedData = data.map(item => complexTransform(item));
  
  return html`<div class="widget">
    ${processedData.map(item => html`<div>${item.value}</div>`)}
  </div>`;
}, (prevProps, nextProps) => {
  // Custom comparison function
  return prevProps.data === nextProps.data && 
         prevProps.config === nextProps.config;
});
```

### Debounced Input Handling

```js
import { useState, useCallback } from 'preact/hooks';
import { html } from 'htm/preact';

function useDebouncedCallback(callback, delay) {
  const [debouncedCallback, setDebouncedCallback] = useState(null);
  
  useEffect(() => {
    const handler = setTimeout(() => {
      callback();
    }, delay);
    
    setDebouncedCallback(() => clearTimeout(handler));
    return () => clearTimeout(handler);
  }, [callback, delay]);
  
  return debouncedCallback;
}

function SearchBox() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  
  const search = useCallback(async () => {
    if (!query.trim()) {
      setResults([]);
      return;
    }
    
    const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
    const data = await response.json();
    setResults(data);
  }, [query]);
  
  const debouncedSearch = useDebouncedCallback(search, 300);
  
  const handleInput = (e) => {
    setQuery(e.target.value);
    debouncedSearch && debouncedSearch();
  };
  
  return html`<div>
    <input 
      type="search" 
      placeholder="Search..."
      value=${query}
      onInput=${handleInput}
    />
    
    <ul class="results">
      ${results.map(result => html`<li key=${result.id}>${result.name}</li>`)}
    </ul>
  </div>`;
}
```

### Virtual Scrolling for Large Lists

```js
import { useState, useRef } from 'preact/hooks';
import { html } from 'htm/preact';

function VirtualList({ items, itemHeight = 50, visibleCount = 10 }) {
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef(null);
  
  const totalHeight = items.length * itemHeight;
  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = Math.min(startIndex + visibleCount, items.length);
  const visibleItems = items.slice(startIndex, endIndex);
  const offsetTop = startIndex * itemHeight;
  
  const handleScroll = (e) => {
    setScrollTop(e.target.scrollTop);
  };
  
  return html`<div 
    class="virtual-list"
    ref=${containerRef}
    style=${`height: ${visibleCount * itemHeight}px; overflow-y: auto;`}
    onScroll=${handleScroll}>
    
    <div style=${`transform: translateY(${offsetTop}px);`}>
      ${visibleItems.map((item, index) => html`
        <div 
          class="list-item" 
          key=${item.id}
          style=${`height: ${itemHeight}px;`}
        >
          ${item.name}
        </div>
      `)}
    </div>
    
    <!-- Spacer for total height -->
    <div style=${`height: ${totalHeight - visibleItems.length * itemHeight}px;`} />
  </div>`;
}
```

## Context with htm

### Preact Context

```js
import { createContext, useContext } from 'preact';
import { html } from 'htm/preact';

const ThemeContext = createContext('light');

const ThemeProvider = ({ theme, children }) => 
  html`<${ThemeContext.Provider} value=${theme}>
    ${children}
  <//>`;

const useTheme = () => useContext(ThemeContext);

const ThemedButton = () => {
  const theme = useTheme();
  return html`<button class=${`btn-${theme}`}>Themed Button</button>`;
};

const App = () => html`<${ThemeProvider} theme="dark">
  <div class="app">
    <h1>Dark Mode App</h1>
    <${ThemedButton} />
  </div>
<//>`;
```

### React Context

```js
import { createContext, useContext } from 'react';
import { html } from 'htm/react';

const UserContext = createContext(null);

const UserProvider = ({ user, children }) => 
  html`<${UserContext.Provider} value=${user}>
    ${children}
  <//>`;

const useUser = () => {
  const context = useContext(UserContext);
  if (!context) throw new Error('useUser must be used within UserProvider');
  return context;
};

const UserProfile = () => {
  const user = useUser();
  return html`<div>
    <h2>${user.name}'s Profile</h2>
    <p>Email: ${user.email}</p>
  </div>`;
};

const App = ({ user }) => 
  html`<${UserProvider} user=${user}>
    <div class="app">
      <${UserProfile} />
    </div>
  <//>`;
```

## Error Boundaries

### Preact Error Boundary

```js
import { Component } from 'preact';
import { html } from 'htm/preact';

class ErrorBoundary extends Component {
  state = { hasError: false, error: null };
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  
  render({ children }) {
    if (this.state.hasError) {
      return html`<div class="error-boundary">
        <h2>Something went wrong</h2>
        <pre>${this.state.error.message}</pre>
        <button onClick=${() => this.setState({ hasError: false, error: null })}>
          Try again
        </button>
      </div>`;
    }
    
    return children;
  }
}

// Usage
render(html`<${ErrorBoundary}>
  <${UnstableComponent} />
</${ErrorBoundary}>`, document.body);
```

### React Error Boundary

```js
import { Component } from 'react';
import { html } from 'htm/react';

class ErrorBoundary extends Component {
  state = { hasError: false, error: null };
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error, errorInfo) {
    // Log error to monitoring service
    console.error('Error caught:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return html`<div class="error-fallback">
        <h2>Application Error</h2>
        <p>Please refresh the page or contact support.</p>
      </div>`;
    }
    
    return this.props.children;
  }
}

// Usage
export default function App() {
  return html`<${ErrorBoundary}>
    <${MainContent} />
  </${ErrorBoundary}>`;
}
```

## Custom Elements with htm

### Web Components Integration

```js
import { html } from 'htm/preact';

// Define custom element
class GreetingElement extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `<h1>Hello, ${this.getAttribute('name')}!</h1>`;
  }
}

customElements.define('my-greeting', GreetingElement);

// Use in htm
const App = () => html`<div>
  <my-greeting name="World" />
</div>`;
```

### Using Custom Elements as Components

```js
import { html } from 'htm/preact';

// Register custom element
const MyButton = defineCustomElement(({ label, onClick }) => 
  html`<button onClick=${onClick}>${label}</button>`
);

// Use like a regular component
html`<${MyButton} label="Click me" onClick=${handleClick} />`;
```

## Server-Side Rendering (SSR)

Basic SSR pattern with vhtml:

```js
import htm from 'htm';
import vhtml from 'vhtml';

const html = htm.bind(vhtml);

// Component
const UserCard = ({ user }) => html`<div class="user-card">
  <h2>${user.name}</h2>
  <p>${user.bio}</p>
</div>`;

// Render to HTML string on server
const user = { name: 'John Doe', bio: 'Web developer' };
const htmlString = html`<${UserCard} user=${user} />`;

console.log(htmlString);
// '<div class="user-card"><h2>John Doe</h2><p>Web developer</p></div>'
```

See [SSR Patterns](references/03-integrations.md#server-side-rendering) for complete SSR examples.
