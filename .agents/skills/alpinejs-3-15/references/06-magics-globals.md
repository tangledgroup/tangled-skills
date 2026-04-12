# Magics and Globals

Alpine.js provides "magic" functions (prefixed with `$`) that extend component functionality, and global APIs for interacting with Alpine from outside components.

## Magic Functions

Magic functions are available within Alpine templates and provide utilities for common tasks. They're accessed via the `$` prefix.

### $el

Reference to the current element:

```html
<div x-data="{ focused: false }">
    <input 
        x-ref="myInput"
        @focus="$el.classList.add('focused')"
        @blur="$el.classList.remove('focused')">
</div>
```

Useful for:
- Direct DOM manipulation
- Integrating with third-party libraries
- Accessing element properties

### $refs

Access elements referenced with `x-ref`:

```html
<div x-data="{ 
    focusInput() {
        this.$refs.searchInput.focus()
    },
    clearForm() {
        this.$refs.form.reset()
    }
}">
    <form x-ref="form">
        <input type="text" x-ref="searchInput" placeholder="Search">
    </form>
    
    <button @click="focusInput">Focus Input</button>
    <button @click="clearForm">Clear Form</button>
</div>
```

### $dispatch

Dispatch custom events:

```html
<div x-data="{ 
    submitForm() {
        this.$dispatch('form-submitted', { name: this.name })
    }
}">
    <form @submit.prevent="submitForm">
        <input type="text" x-model="name">
        <button type="submit">Submit</button>
    </form>
</div>

<!-- Listen elsewhere -->
<div @form-submitted.window="handleFormSubmitted($event.detail)">
    <p x-text="lastSubmission"></p>
</div>
```

### $listeners

Access event listeners on current element:

```html
<div x-data>
    <div 
        @custom-event="handleEvent"
        x-init="$watch('listeners', () => {
            console.log('Listeners:', Object.keys($listeners))
        })">
        Element with listeners
    </div>
</div>
```

### $parent

Access parent component's data:

```html
<div x-data="{ count: 0 }">
    <div x-data="{ 
        incrementParent() {
            this.$parent.count++
        }
    }">
        <button @click="incrementParent">Increment Parent</button>
    </div>
    
    <span x-text="count"></span>
</div>
```

Chain `$parent` to access multiple levels up: `$parent.$parent.count`

### $root

Access the root Alpine element (element with top-level `x-data`):

```html
<div x-data="{ globalCount: 0 }">
    <div x-data>
        <div x-data>
            <button @click="$root.globalCount++">Increment Root</button>
        </div>
    </div>
    
    <span x-text="globalCount"></span>
</div>
```

### $data

Reference to the component's data object:

```html
<div x-data="{ count: 0, name: 'test' }">
    <button @click="console.log($data)">Log Data</button>
    <pre x-text="JSON.stringify($data, null, 2)"></pre>
</div>
```

### $nextTick

Schedule code to run after next DOM update:

```html
<div x-data="{ 
    show: false,
    showModal() {
        this.show = true
        this.$nextTick(() => {
            this.$refs.modalContent.focus()
        })
    }
}">
    <button @click="showModal">Show Modal</button>
    
    <div x-show="show" x-ref="modal">
        <div x-ref="modalContent">Modal content</div>
    </div>
</div>
```

### $watch

Watch a specific property for changes:

```html
<div x-data="{
    count: 0,
    
    init() {
        this.$watch('count', (value) => {
            console.log('Count changed to:', value)
            localStorage.setItem('lastCount', value)
        })
    }
}">
    <button @click="count++">Increment</button>
    <span x-text="count"></span>
</div>
```

### $effect

Run code whenever any accessed reactive property changes:

```html
<div x-data="{
    firstName: '',
    lastName: '',
    
    init() {
        this.$effect(() => {
            // Auto-runs when firstName or lastName changes
            const fullName = this.firstName + ' ' + this.lastName
            console.log('Full name:', fullName)
        })
    }
}">
    <input x-model="firstName" placeholder="First">
    <input x-model="lastName" placeholder="Last">
</div>
```

### $id

Generate unique, consistent IDs for elements:

```html
<div x-data="{ 
    labelFor() {
        return this.$id('email-input')
    }
}">
    <label :for="labelFor()">Email:</label>
    <input :id="labelFor()" type="email">
</div>
```

Ensures consistent IDs for accessibility (matching `for` and `id` attributes).

### $store

Access global stores:

```html
<!-- Define store -->
<script>
Alpine.store('theme', {
    current: 'light',
    toggle() {
        this.current = this.current === 'light' ? 'dark' : 'light'
    }
})
</script>

<!-- Access in template -->
<div x-data>
    <button @click="$store.theme.toggle()">Toggle Theme</button>
    <p>Current theme: <span x-text="$store.theme.current"></span></p>
</div>
```

### $entangle

Two-way bind to parent component's data (used in nested components):

```html
<!-- Parent -->
<div x-data="{ title: 'Hello' }">
    <!-- Child with entangled data -->
    <div x-data="{ 
        localTitle: $entangle('title')
    }">
        <input x-model="localTitle">
        <p x-text="localTitle"></p>
    </div>
    
    <p x-text="title"></p>
</div>
```

Changes to `localTitle` update parent's `title`, and vice versa.

### $modify

Modify a value before it's set:

```html
<div x-data="{ 
    count: 0,
    increment() {
        this.$modify('count', value => value + 1)
    }
}">
    <button @click="increment">Increment</button>
    <span x-text="count"></span>
</div>
```

Useful for custom setters or validation.

## Global APIs

Global Alpine APIs accessible from anywhere in your JavaScript code.

### Alpine.data()

Define reusable component data:

```javascript
Alpine.data('counter', () => ({
    count: 0,
    increment() { this.count++ },
    decrement() { this.count-- }
}))
```

```html
<div x-data="counter">
    <button @click="decrement">-</button>
    <span x-text="count"></span>
    <button @click="increment">+</button>
</div>
```

### Alpine.store()

Define global state stores:

```javascript
Alpine.store('cart', {
    items: [],
    add(item) { this.items.push(item) },
    remove(index) { this.items.splice(index, 1) },
    get total() { return this.items.length }
})
```

```html
<div x-data>
    <button @click="$store.cart.add({ name: 'Product' })">Add to Cart</button>
    <p>Cart total: <span x-text="$store.cart.total"></span> items</p>
</div>
```

### Alpine.magic()

Define custom magic functions:

```javascript
document.addEventListener('alpine:init', () => {
    Alpine.magic('time', () => {
        return new Date().toLocaleTimeString()
    })
})
```

```html
<div x-data>
    <p>Current time: <span x-text="$time()"></span></p>
</div>
```

### Alpine.directive()

Define custom directives:

```javascript
document.addEventListener('alpine:init', () => {
    Alpine.directive('tooltip', (el, { expression }, { effect }) => {
        el.setAttribute('title', expression)
        
        // Or more complex behavior
        effect(() => {
            el.title = expression
        })
    })
})
```

```html
<div x-data="{ message: 'Hello!' }">
    <button x-tooltip="message">Hover for tooltip</button>
</div>
```

See [Extending Alpine](08-extending-alpine.md) for detailed custom directive examples.

### Alpine.plugin()

Register plugins that can add directives, magics, stores:

```javascript
function myPlugin({ magic, directive, store }) {
    magic('hello', () => 'World')
    
    directive('uppercase', (el, { expression }, { effect }) => {
        effect(() => {
            el.textContent = el.textContent.toUpperCase()
        })
    })
    
    store('pluginData', { value: 0 })
}

Alpine.plugin(myPlugin)
```

### Alpine.clone()

Clone a component's data:

```javascript
const template = { count: 0, increment() { this.count++ } }

const instance1 = Alpine.clone(template, document.getElementById('el1'))
const instance2 = Alpine.clone(template, document.getElementById('el2'))
```

Useful for dynamically creating components with same structure.

### Alpine.start()

Manually start Alpine (when not using CDN):

```javascript
import Alpine from 'alpinejs'

// Configure Alpine before starting
Alpine.data('...', ...)
Alpine.store('...', ...)

// Then start
Alpine.start()
```

## Magic Function Patterns

### API Integration Pattern

```html
<div x-data="{
    users: [],
    loading: false,
    error: null,
    
    async fetchUsers() {
        this.loading = true
        try {
            const response = await fetch('/api/users')
            this.users = await response.json()
        } catch (e) {
            this.error = e.message
        } finally {
            this.loading = false
        }
    }
}" x-init="fetchUsers()">
    
    <template x-if="loading">
        <p>Loading...</p>
    </template>
    
    <template x-if="error">
        <p class="error" x-text="error"></p>
    </template>
    
    <template x-if="users.length">
        <ul>
            <template x-for="user in users">
                <li x-text="user.name"></li>
            </template>
        </ul>
    </template>
    
    <button @click="fetchUsers" :disabled="loading">Refresh</button>
</div>
```

### Event Bus Pattern

```javascript
// Global event handling
document.addEventListener('alpine:init', () => {
    Alpine.data('eventBus', () => ({
        listeners: {},
        
        on(event, callback) {
            if (!this.listeners[event]) {
                this.listeners[event] = []
            }
            this.listeners[event].push(callback)
        },
        
        emit(event, data) {
            if (this.listeners[event]) {
                this.listeners[event].forEach(cb => cb(data))
            }
        }
    }))
})
```

```html
<!-- Emitter -->
<div x-data>
    <button @click="$dispatch('user-created', { id: 1, name: 'John' })">
        Create User
    </button>
</div>

<!-- Listener -->
<div x-data="{ users: [] }" 
     @user-created.window="users.push($event.detail)">
    <template x-for="user in users">
        <p x-text="user.name"></p>
    </template>
</div>
```

### Form Validation Pattern with Magics

```html
<div x-data="{
    form: { email: '', password: '' },
    errors: {},
    
    validate() {
        this.errors = {}
        
        if (!this.form.email.includes('@')) {
            this.errors.email = 'Invalid email'
        }
        
        if (this.form.password.length < 8) {
            this.errors.password = 'Password too short'
        }
        
        return Object.keys(this.errors).length === 0
    }
}">
    <form @submit.prevent="validate() && $dispatch('form-valid')">
        <div>
            <label>Email</label>
            <input type="email" x-model="form.email">
            <span x-show="errors.email" x-text="errors.email"></span>
        </div>
        
        <div>
            <label>Password</label>
            <input type="password" x-model="form.password">
            <span x-show="errors.password" x-text="errors.password"></span>
        </div>
        
        <button type="submit">Submit</button>
    </form>
</div>
```

## Store Patterns

### Multi-Store Communication

```javascript
Alpine.store('user', {
    name: '',
    loggedIn: false,
    
    login(name) {
        this.name = name
        this.loggedIn = true
        $dispatch('user-logged-in', { name })
    },
    
    logout() {
        this.name = ''
        this.loggedIn = false
        $dispatch('user-logged-out')
    }
})

Alpine.store('notifications', {
    list: [],
    
    init() {
        document.addEventListener('user-logged-in', (e) => {
            this.add(`Welcome, ${e.detail.name}!`)
        })
        
        document.addEventListener('user-logged-out', () => {
            this.add('You have been logged out')
        })
    },
    
    add(message) {
        this.list.push({ message, id: Date.now() })
        setTimeout(() => {
            this.list = this.list.filter(n => n.id !== this.id)
        }, 3000)
    }
})
```

### Persistent Store with localStorage

```javascript
Alpine.store('settings', {
    theme: localStorage.getItem('theme') || 'light',
    language: localStorage.getItem('language') || 'en',
    
    $watch('theme', value => {
        localStorage.setItem('theme', value)
        document.documentElement.className = value
    }),
    
    $watch('language', value => {
        localStorage.setItem('language', value)
    })
})
```

## Best Practices

1. **Use stores for global state** - Keep component-local state in `x-data`, global state in stores
2. **Prefer $dispatch for communication** - Over `$parent` or `$root` references
3. **Use magic functions sparingly** - Don't over-rely on `$el` for DOM manipulation
4. **Initialize in alpine:init** - Register magics, directives, stores during initialization
5. **Keep magics pure** - Magic functions should ideally have no side effects

See [Extending Alpine](08-extending-alpine.md) for creating custom magics and directives.
