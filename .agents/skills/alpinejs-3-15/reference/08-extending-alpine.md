# Extending Alpine

Alpine.js is highly extensible. You can create custom directives, magics, stores, and even entire plugins. This guide covers how to extend Alpine's core functionality.

## Extension Timing

All extensions must be registered AFTER Alpine loads but BEFORE it initializes:

### Via Script Tag

```html
<script src="/alpine.js" defer></script>
<script>
document.addEventListener('alpine:init', () => {
    // Register extensions here
    Alpine.directive('foo', ...)
    Alpine.magic('bar', ...)
})
</script>
```

### Via Module Import

```javascript
import Alpine from 'alpinejs'

// Register before starting
Alpine.directive('foo', ...)
Alpine.magic('bar', ...)

Alpine.start()
```

## Custom Directives

Custom directives extend HTML with new `x-` prefixed attributes.

### Basic Directive

```javascript
document.addEventListener('alpine:init', () => {
    Alpine.directive('uppercase', (el) => {
        el.textContent = el.textContent.toUpperCase()
    })
})
```

```html
<div x-data>
    <span x-uppercase>Hello World</span>
    <!-- Outputs: HELLO WORLD -->
</div>
```

### Directive with Expression

```javascript
document.addEventListener('alpine:init', () => {
    Alpine.directive('bind-class', (el, { expression }) => {
        el.className = expression
    })
})
```

```html
<div x-data="{ className: 'active selected' }">
    <div x-bind-class="className">Dynamic classes</div>
</div>
```

### Reactive Directive with effect()

```javascript
document.addEventListener('alpine:init', () => {
    Alpine.directive('track-scroll', (el, { expression }, { effect }) => {
        effect(() => {
            const target = document.querySelector(expression)
            if (target) {
                el.textContent = `Scroll: ${window.scrollY}px`
            }
        })
    })
})
```

```html
<div x-data>
    <div x-track-scroll="#content">Updates on scroll</div>
    <div id="content" style="height: 2000px;"></div>
</div>
```

### Directive with Cleanup

```javascript
document.addEventListener('alpine:init', () => {
    Alpine.directive('auto-focus', (el, { expression }, { cleanup }) => {
        const handler = () => el.focus()
        document.addEventListener('keydown', handler)
        
        // Cleanup on element removal
        cleanup(() => {
            document.removeEventListener('keydown', handler)
        })
    })
})
```

```html
<div x-data="{ show: false }">
    <button @click="show = true">Show</button>
    
    <div x-show="show">
        <input x-auto-focus="true" placeholder="Auto-focused">
    </div>
</div>
```

### Directive with Modifier

```javascript
document.addEventListener('alpine:init', () => {
    Alpine.directive('confirm', (el, { expression, modifiers }, { effect }) => {
        el.addEventListener('click', (e) => {
            const message = modifiers[0] || 'Are you sure?'
            if (!confirm(message)) {
                e.preventDefault()
                return
            }
            
            // Execute the original click handler
            if (expression) {
                new Function('return ' + expression).call(el)
            }
        })
    })
})
```

```html
<div x-data="{ item: { id: 1 } }">
    <!-- Simple confirm -->
    <button x-confirm="deleteItem()">Delete</button>
    
    <!-- Custom message -->
    <button x-confirm."Really delete this?">Delete with custom message</button>
</div>
```

### Complete Example: Tooltip Directive

```javascript
document.addEventListener('alpine:init', () => {
    Alpine.directive('tooltip', (el, { expression }, { effect, cleanup }) => {
        // Create tooltip element
        const tooltip = document.createElement('div')
        tooltip.className = 'tooltip'
        document.body.appendChild(tooltip)
        
        effect(() => {
            tooltip.textContent = expression
        })
        
        // Show tooltip on hover
        const show = () => {
            const rect = el.getBoundingClientRect()
            tooltip.style.top = `${rect.bottom + 5}px`
            tooltip.style.left = `${rect.left}px`
            tooltip.style.display = 'block'
        }
        
        const hide = () => {
            tooltip.style.display = 'none'
        }
        
        el.addEventListener('mouseenter', show)
        el.addEventListener('mouseleave', hide)
        
        cleanup(() => {
            el.removeEventListener('mouseenter', show)
            el.removeEventListener('mouseleave', hide)
            tooltip.remove()
        })
    })
})
```

```html
<style>
.tooltip {
    position: absolute;
    background: #333;
    color: white;
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 14px;
    pointer-events: none;
    z-index: 1000;
}
</style>

<div x-data="{ message: 'Hello!' }">
    <button x-tooltip="message">Hover for tooltip</button>
</div>
```

## Custom Magics

Custom magics add new `$` prefixed functions available in templates.

### Simple Magic

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

### Magic with Parameters

```javascript
document.addEventListener('alpine:init', () => {
    Alpine.magic('format', (value, format = 'currency') => {
        const num = parseFloat(value)
        if (isNaN(num)) return value
        
        switch (format) {
            case 'currency':
                return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(num)
            case 'percent':
                return (num * 100).toFixed(2) + '%'
            case 'integer':
                return Math.floor(num)
            default:
                return value
        }
    })
})
```

```html
<div x-data="{ price: 19.99, ratio: 0.75, count: 42 }">
    <p>Price: <span x-text="$format(price)"></span></p>
    <p>Ratio: <span x-text="$format(ratio, 'percent')"></span></p>
    <p>Count: <span x-text="$format(count, 'integer')"></span></p>
</div>
```

### Magic that Returns Reactive Data

```javascript
document.addEventListener('alpine:init', () => {
    Alpine.magic('counter', () => {
        let count = 0
        return {
            get() { return count },
            increment() { count++ },
            decrement() { count-- },
            reset() { count = 0 }
        }
    })
})
```

```html
<div x-data>
    <button @click="$counter().decrement">-</button>
    <span x-text="$counter().get()"></span>
    <button @click="$counter().increment">+</button>
    <button @click="$counter().reset()">Reset</button>
</div>
```

### Magic with Element Context

```javascript
document.addEventListener('alpine:init', () => {
    Alpine.magic('sibling', (direction = 'next') => {
        return Alpine.closestData($el).$el[direction + 'ElementSibling']
    })
})
```

## Custom Stores

Stores provide global state accessible across all components.

### Basic Store

```javascript
Alpine.store('theme', {
    current: 'light',
    
    toggle() {
        this.current = this.current === 'light' ? 'dark' : 'light'
    },
    
    set(value) {
        this.current = value
    }
})
```

```html
<div x-data>
    <button @click="$store.theme.toggle()">Toggle Theme</button>
    <p>Current: <span x-text="$store.theme.current"></span></p>
</div>
```

### Store with Watchers

```javascript
Alpine.store('cart', {
    items: [],
    
    add(product) {
        this.items.push({ ...product, quantity: 1 })
        this.$dispatch('cart-updated', { total: this.total })
    },
    
    remove(index) {
        this.items.splice(index, 1)
    },
    
    get total() {
        return this.items.reduce((sum, item) => sum + item.price * item.quantity, 0)
    },
    
    init() {
        this.$watch('items', (items) => {
            localStorage.setItem('cart', JSON.stringify(items))
        })
    }
})
```

### Store with Persistence

```javascript
Alpine.store('settings', {
    theme: localStorage.getItem('theme') || 'light',
    language: localStorage.getItem('language') || 'en',
    fontSize: parseInt(localStorage.getItem('fontSize')) || 16,
    
    $watch('theme', value => {
        localStorage.setItem('theme', value)
        document.documentElement.className = value
    }),
    
    $watch('language', value => {
        localStorage.setItem('language', value)
    }),
    
    $watch('fontSize', value => {
        localStorage.setItem('fontSize', value)
        document.body.style.fontSize = value + 'px'
    })
})
```

## Creating Plugins

Plugins bundle multiple extensions (directives, magics, stores) into a reusable package.

### Basic Plugin Structure

```javascript
function myPlugin({ magic, directive, store, data }) {
    // Add a store
    store('myStore', {
        value: 0,
        increment() { this.value++ }
    })
    
    // Add a magic
    magic('myMagic', () => {
        return 'Hello from myMagic!'
    })
    
    // Add a directive
    directive('myDirective', (el, { expression }) => {
        el.textContent = expression.toUpperCase()
    })
    
    // Add component data
    data('myComponent', () => ({
        count: 0,
        increment() { this.count++ }
    }))
}

Alpine.plugin(myPlugin)
```

### Complete Plugin Example: Form Validation

```javascript
function formValidationPlugin({ magic, directive }) {
    // Magic for validation rules
    magic('validate', (rules) => {
        return (value, fieldName) => {
            const rule = rules[fieldName]
            if (!rule) return true
            
            const validators = {
                required: val => val && val.trim() !== '',
                email: val => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val),
                min: val => {
                    const [_, minLength] = rule.split(':')
                    return val.length >= parseInt(minLength)
                },
                max: val => {
                    const [_, maxLength] = rule.split(':')
                    return val.length <= parseInt(maxLength)
                }
            }
            
            const [ruleName, ...params] = rule.split(':')
            return validators[ruleName](value)
        }
    })
    
    // Directive for error display
    directive('error', (el, { expression }, { effect }) => {
        effect(() => {
            const errors = Alpine.store('formErrors')
            const error = errors[expression]
            
            el.textContent = error || ''
            el.style.display = error ? 'block' : 'none'
            
            if (error) {
                el.classList.add('error-visible')
            } else {
                el.classList.remove('error-visible')
            }
        })
    })
    
    // Initialize errors store
    Alpine.store('formErrors', {})
}

Alpine.plugin(formValidationPlugin)
```

Usage:

```html
<div x-data="{ 
    form: { email: '', password: '' },
    rules: {
        email: 'required|email',
        password: 'required|min:8'
    }
}">
    <form @submit.prevent="validateAndSubmit">
        <div>
            <label>Email</label>
            <input type="email" x-model="form.email">
            <span x-error="email"></span>
        </div>
        
        <div>
            <label>Password</label>
            <input type="password" x-model="form.password">
            <span x-error="password"></span>
        </div>
        
        <button type="submit">Submit</button>
    </form>
    
    <script>
        function validateAndSubmit() {
            const validate = $validate(this.rules)
            
            if (!validate(this.form.email, 'email')) {
                $store.formErrors.email = 'Invalid email'
                return
            }
            
            if (!validate(this.form.password, 'password')) {
                $store.formErrors.password = 'Password must be 8+ characters'
                return
            }
            
            // Form is valid
            alert('Form submitted!')
        }
    </script>
</div>
```

## Advanced Extension Patterns

### Directive Factory Pattern

```javascript
document.addEventListener('alpine:init', () => {
    const createObserverDirective = (observerType) => {
        return (el, { expression, modifiers }, { cleanup }) => {
            const options = {
                threshold: modifiers.includes('full') ? 1 : 0.5
            }
            
            const callback = (entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        el.dispatchEvent(new CustomEvent(`${observerType}-entered`))
                    } else {
                        el.dispatchEvent(new CustomEvent(`${observerType}-left`))
                    }
                })
            }
            
            const observer = new IntersectionObserver(callback, options)
            observer.observe(el)
            
            cleanup(() => {
                observer.disconnect()
            })
        }
    }
    
    Alpine.directive('intersect', createObserverDirective('intersect'))
})
```

### Composable Store Pattern

```javascript
const createStore = (name, initialState, options = {}) => {
    const store = { ...initialState }
    
    if (options.watchers) {
        Object.entries(options.watchers).forEach(([key, watcher]) => {
            store[`$watch:${key}`] = watcher
        })
    }
    
    if (options.persistent) {
        const saved = localStorage.getItem(name)
        if (saved) {
            Object.assign(store, JSON.parse(saved))
        }
        
        Object.defineProperty(store, '$watch', {
            value: (key, callback) => {
                const original = store[key]
                store[key] = function(...args) {
                    const result = original.apply(this, args)
                    callback(result)
                    localStorage.setItem(name, JSON.stringify(store))
                    return result
                }
            }
        })
    }
    
    Alpine.store(name, store)
    return store
}

// Usage
createStore('user', {
    name: '',
    email: ''
}, {
    persistent: true,
    watchers: {
        name: (value) => console.log('Name changed:', value)
    }
})
```

## Best Practices

1. **Prefix your extensions** - Use unique prefixes to avoid conflicts (e.g., `x-myapp-tooltip`)
2. **Clean up resources** - Always provide cleanup functions for event listeners and observers
3. **Use effect() for reactivity** - Make directives reactive using the `effect` helper
4. **Document your extensions** - Include usage examples in comments
5. **Test edge cases** - Handle null/undefined values gracefully
6. **Keep extensions focused** - One directive/magic per specific purpose
7. **Use plugin pattern for distribution** - Bundle related extensions as plugins

## Debugging Extensions

### Enable Alpine Debug Mode

```javascript
Alpine.displode = false // Prevent auto-initialization for debugging

// Manually inspect
console.log(Alpine.store('mystore'))
```

### Log Directive Lifecycle

```javascript
Alpine.directive('debug', (el, { expression }, { effect, cleanup }) => {
    console.log('Directive initialized', el, expression)
    
    effect(() => {
        console.log('Effect running', expression)
    })
    
    cleanup(() => {
        console.log('Directive cleaned up')
    })
})
```

## Common Extension Recipes

### Debounce Directive

```javascript
Alpine.directive('debounce', (el, { expression, modifiers }, { effect }) => {
    const delay = parseInt(modifiers[0]) || 300
    let timeout
    
    effect(() => {
        clearTimeout(timeout)
        timeout = setTimeout(() => {
            new Function('return ' + expression).call(el)
        }, delay)
    })
})
```

### Throttle Directive

```javascript
Alpine.directive('throttle', (el, { expression, modifiers }, { effect }) => {
    const interval = parseInt(modifiers[0]) || 100
    let lastRun = 0
    
    const run = () => {
        const now = Date.now()
        if (now - lastRun >= interval) {
            lastRun = now
            new Function('return ' + expression).call(el)
        }
    }
    
    effect(run)
})
```

See [Common Components](09-common-components.md) for complete component examples using these extension patterns.
