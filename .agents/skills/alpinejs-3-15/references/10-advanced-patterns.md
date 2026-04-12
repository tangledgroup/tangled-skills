# Advanced Patterns

This guide covers advanced Alpine.js patterns for building complex, production-ready applications including async operations, state management, performance optimization, and integration with other libraries.

## Async Operations

### Fetching Data

```html
<div x-data="{ 
    users: [],
    loading: false,
    error: null,
    
    async fetchUsers() {
        this.loading = true
        this.error = null
        
        try {
            const response = await fetch('/api/users')
            
            if (!response.ok) {
                throw new Error('Failed to fetch users')
            }
            
            this.users = await response.json()
        } catch (err) {
            this.error = err.message
        } finally {
            this.loading = false
        }
    }
}" x-init="fetchUsers()">
    
    <template x-if="loading">
        <div class="loading">Loading users...</div>
    </template>
    
    <template x-if="error">
        <div class="error" x-text="error"></div>
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

### Form Submission with Loading State

```html
<div x-data="{ 
    form: { name: '', email: '' },
    submitting: false,
    success: false,
    error: null,
    
    async submit() {
        this.submitting = true
        this.error = null
        
        try {
            const response = await fetch('/api/subscribe', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.form)
            })
            
            if (!response.ok) {
                throw new Error('Subscription failed')
            }
            
            this.success = true
            this.form = { name: '', email: '' }
            
            // Reset success message after 3 seconds
            setTimeout(() => this.success = false, 3000)
        } catch (err) {
            this.error = err.message
        } finally {
            this.submitting = false
        }
    }
}">
    <form @submit.prevent="submit">
        <input type="text" x-model="form.name" placeholder="Name" required :disabled="submitting">
        <input type="email" x-model="form.email" placeholder="Email" required :disabled="submitting">
        
        <button type="submit" :disabled="submitting">
            <span x-show="!submitting">Subscribe</span>
            <span x-show="submitting">Subscribing...</span>
        </button>
    </form>
    
    <div x-show="success" class="success">Successfully subscribed!</div>
    <div x-show="error" class="error" x-text="error"></div>
</div>
```

### Debounced Search with API

```html
<div x-data="{
    query: '',
    results: [],
    loading: false,
    
    async performSearch(value) {
        if (!value || value.length < 2) {
            this.results = []
            return
        }
        
        this.loading = true
        
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(value)}`)
            this.results = await response.json()
        } catch (err) {
            console.error('Search failed:', err)
        } finally {
            this.loading = false
        }
    }
}"
x-init="$watch('query', debounce(performSearch, 300))">
    
    <input 
        type="text" 
        x-model="query" 
        placeholder="Search (type 2+ characters)...">
    
    <div x-show="loading" class="loading">Searching...</div>
    
    <ul x-show="results.length">
        <template x-for="result in results">
            <li x-text="result.name"></li>
        </template>
    </ul>
</div>

<script>
function debounce(fn, delay) {
    let timeout
    return (...args) => {
        clearTimeout(timeout)
        timeout = setTimeout(() => fn.apply(this, args), delay)
    }
}
</script>
```

### Pagination with Infinite Scroll

```html
<div x-data="{
    items: [],
    page: 1,
    loading: false,
    noMore: false,
    
    async loadMore() {
        if (this.loading || this.noMore) return
        
        this.loading = true
        
        try {
            const response = await fetch(`/api/items?page=${this.page}`)
            const data = await response.json()
            
            this.items.push(...data.items)
            this.page++
            this.noMore = data.items.length === 0
        } finally {
            this.loading = false
        }
    }
}" x-init="loadMore()">
    
    <ul>
        <template x-for="item in items">
            <li x-text="item.name"></li>
        </template>
    </ul>
    
    <!-- Intersection Observer for infinite scroll -->
    <div 
        x-intersect.once="loadMore()"
        class="py-4 text-center"
        x-show="!noMore">
        <span x-show="loading">Loading more...</span>
        <span x-show="!loading && !noMore">Scroll for more</span>
    </div>
    
    <p x-show="noMore">No more items to load</p>
</div>
```

## State Management Patterns

### Local Storage Persistence

```html
<div x-data="{
    settings: JSON.parse(localStorage.getItem('settings')) || {
        theme: 'light',
        language: 'en',
        notifications: true
    },
    
    init() {
        this.$watch('settings', (value) => {
            localStorage.setItem('settings', JSON.stringify(value))
        })
    }
}">
    <select x-model="settings.theme">
        <option value="light">Light</option>
        <option value="dark">Dark</option>
    </select>
    
    <select x-model="settings.language">
        <option value="en">English</option>
        <option value="es">Spanish</option>
    </select>
    
    <label>
        <input type="checkbox" x-model="settings.notifications">
        Enable notifications
    </label>
</div>
```

### Session-based State

```html
<div x-data="{
    sessionData: JSON.parse(sessionStorage.getItem('session')) || {
        steps: [],
        currentStep: 0
    },
    
    init() {
        this.$watch('sessionData', (value) => {
            sessionStorage.setItem('session', JSON.stringify(value))
        })
    },
    
    addStep(step) {
        this.sessionData.steps.push(step)
        this.sessionData.currentStep = this.sessionData.steps.length - 1
    }
}">
    <button @click="addStep({ name: 'New Step', done: false })">
        Add Step
    </button>
    
    <template x-for="(step, index) in sessionData.steps">
        <div :class="{ 'active': index === sessionData.currentStep }">
            <span x-text="step.name"></span>
        </div>
    </template>
</div>
```

### Global Event Bus

```javascript
// Setup event bus
Alpine.data('eventBus', () => ({
    listeners: {},
    
    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = []
        }
        this.listeners[event].push(callback)
        
        // Return unsubscribe function
        return () => {
            this.listeners[event] = this.listeners[event].filter(cb => cb !== callback)
        }
    },
    
    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data))
        }
    }
}))

// Make available globally
document.addEventListener('alpine:init', () => {
    Alpine.store('events', new Event Bus())
})
```

Usage:

```html
<!-- Publisher -->
<div x-data>
    <button @click="$store.events.emit('user-created', { id: 1, name: 'John' })">
        Create User
    </button>
</div>

<!-- Subscriber -->
<div x-data="{ users: [] }" 
     x-init="$store.events.on('user-created', user => users.push(user))">
    <template x-for="user in users">
        <p x-text="user.name"></p>
    </template>
</div>
```

### Flux-like State Management

```javascript
// Store definition
Alpine.store('counter', {
    count: 0,
    
    // Getters
    get doubled() {
        return this.count * 2
    },
    
    // Actions
    increment() {
        this.count++
        this.$dispatch('counter-updated', { count: this.count })
    },
    
    decrement() {
        this.count--
        this.$dispatch('counter-updated', { count: this.count })
    },
    
    reset() {
        this.count = 0
        this.$dispatch('counter-reset')
    }
})

// Subscribe to changes elsewhere
document.addEventListener('alpine:init', () => {
    document.addEventListener('counter-updated', (e) => {
        console.log('Counter updated:', e.detail.count)
    })
})
```

## Performance Optimization

### Lazy Component Initialization

```html
<div x-data="{ initialized: false }">
    <button @click="initialized = true">Load Heavy Component</button>
    
    <template x-if="initialized">
        <div x-data="{ 
            expensiveData: [],
            
            init() {
                // Only fetch when component is shown
                this.fetchExpensiveData()
            },
            
            async fetchExpensiveData() {
                this.expensiveData = await fetch('/api/heavy-data').then(r => r.json())
            }
        }">
            <template x-for="item in expensiveData">
                <div x-text="item.name"></div>
            </template>
        </div>
    </template>
</div>
```

### Virtual Scrolling for Large Lists

```html
<div x-data="{
    items: Array.from({ length: 10000 }, (_, i) => ({ id: i, text: `Item ${i}` })),
    visibleItems: [],
    containerHeight: 400,
    itemHeight: 40,
    
    init() {
        this.calculateVisibleItems()
        window.addEventListener('scroll', this.debounce(this.calculateVisibleItems, 16), { passive: true })
    },
    
    calculateVisibleItems() {
        const container = $el.querySelector('.virtual-scroll')
        if (!container) return
        
        const scrollTop = container.scrollTop
        const startIndex = Math.max(0, Math.floor(scrollTop / this.itemHeight) - 2)
        const endIndex = Math.min(
            this.items.length,
            Math.ceil((scrollTop + this.containerHeight) / this.itemHeight) + 2
        )
        
        this.visibleItems = this.items.slice(startIndex, endIndex)
    },
    
    debounce(fn, delay) {
        let timeout
        return (...args) => {
            clearTimeout(timeout)
            timeout = setTimeout(() => fn.apply(this, args), delay)
        }
    }
}">
    <div 
        class="virtual-scroll"
        style="height: 400px; overflow-y: auto; position: relative;"
        @scroll="calculateVisibleItems()">
        
        <div 
            style="position: relative; height: " + (items.length * itemHeight) + "px;">
            
            <template x-for="item in visibleItems" :key="item.id">
                <div 
                    style="position: absolute; top: " + (item.id * itemHeight) + "px; height: " + itemHeight + "px; width: 100%;">
                    <span x-text="item.text"></span>
                </div>
            </template>
        </div>
    </div>
</div>
```

### Memoization for Expensive Computations

```html
<div x-data="{
    data: [],
    filter: '',
    sortField: 'name',
    
    // Memoized computation
    get processedData() {
        // This getter is automatically memoized by Alpine's reactivity
        let result = [...this.data]
        
        if (this.filter) {
            result = result.filter(item => 
                item.name.toLowerCase().includes(this.filter.toLowerCase())
            )
        }
        
        result.sort((a, b) => {
            return a[this.sortField].localeCompare(b[this.sortField])
        })
        
        return result
    }
}">
    <input x-model="filter" placeholder="Filter...">
    <select x-model="sortField">
        <option value="name">Name</option>
        <option value="date">Date</option>
    </select>
    
    <template x-for="item in processedData">
        <div x-text="item.name"></div>
    </template>
</div>
```

## CSP (Content Security Policy) Mode

For environments with strict CSP headers:

```html
<!-- Use the CSP-compliant build -->
<script src="/alpine-csp.js" defer></script>

<!-- Or via CDN -->
<script src="https://cdn.jsdelivr.net/npm/alpinejs@3.15.0/dist/cdn.min.js" defer></script>
```

CSP mode limitations:
- No inline JavaScript expressions
- Use `x-data` with external data functions
- Define all functions in external scripts

```html
<script>
function counterData() {
    return {
        count: 0,
        increment() { this.count++ },
        decrement() { this.count-- }
    }
}
</script>

<div x-data="counterData">
    <button @click="decrement">-</button>
    <span x-text="count"></span>
    <button @click="increment">+</button>
</div>
```

## Integration with Other Libraries

### Chart.js Integration

```html
<div x-data="{
    chart: null,
    data: [10, 20, 30, 40, 50],
    
    init() {
        const ctx = $el.querySelector('canvas').getContext('2d')
        this.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['A', 'B', 'C', 'D', 'E'],
                datasets: [{
                    data: this.data,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)'
                }]
            }
        })
    },
    
    updateChartData(newData) {
        this.data = newData
        this.chart.data.datasets[0].data = newData
        this.chart.update()
    },
    
    $destroy() {
        if (this.chart) {
            this.chart.destroy()
        }
    }
}">
    <canvas class="w-full h-64"></canvas>
    
    <button @click="updateChartData([50, 40, 30, 20, 10])">
        Reverse Data
    </button>
</div>
```

### Flatpickr Date Picker

```html
<div x-data="{
    date: null,
    
    init() {
        flatpickr($el.querySelector('input'), {
            onChange: (date) => {
                this.date = date[0]
            }
        })
    }
}">
    <input type="text" placeholder="Select a date">
    <p x-text="date ? 'Selected: ' + date : 'No date selected'"></p>
</div>
```

### Leaflet Maps

```html
<div x-data="{
    map: null,
    markers: [],
    
    init() {
        this.map = L.map($el.querySelector('.map')).setView([51.505, -0.09], 13)
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map)
    },
    
    addMarker(lat, lng) {
        const marker = L.marker([lat, lng]).addTo(this.map)
        this.markers.push(marker)
    },
    
    $destroy() {
        if (this.map) {
            this.map.remove()
        }
    }
}" style="height: 400px;">
    
    <div class="map" style="height: 100%;"></div>
    
    <button @click="addMarker(51.505, -0.09)">Add Marker</button>
</div>
```

## Testing Strategies

### Unit Testing with Jest

```javascript
// component.test.js
import { fireEvent, render } from '@testing-library/alpine'

test('counter increments correctly', () => {
    const { container } = render(`
        <div x-data="{ count: 0 }">
            <button @click="count++">Increment</button>
            <span x-text="count"></span>
        </div>
    `)
    
    expect(container.querySelector('span').textContent).toBe('0')
    
    fireEvent.click(container.querySelector('button'))
    expect(container.querySelector('span').textContent).toBe('1')
})
```

### Component Testing Utilities

```javascript
// test-utils.js
export function createAlpineComponent(html, data = {}) {
    const container = document.createElement('div')
    container.innerHTML = html
    
    // Inject Alpine
    const script = document.createElement('script')
    script.src = '/alpine.js'
    script.defer = true
    document.body.appendChild(script)
    
    document.body.appendChild(container)
    
    return {
        el: container,
        data,
        cleanup() {
            document.body.removeChild(container)
            document.body.removeChild(script)
        }
    }
}
```

## Migration from Vue.js

### Equivalent Patterns

```html
<!-- Vue.js -->
<div id="app">
    <input v-model="message">
    <p>{{ message }}</p>
    <button @click="increment">Count: {{ count }}</button>
</div>

<script>
new Vue({
    el: '#app',
    data: {
        message: '',
        count: 0
    },
    methods: {
        increment() { this.count++ }
    }
})
</script>

<!-- Alpine.js equivalent -->
<div x-data="{ message: '', count: 0 }">
    <input x-model="message">
    <p x-text="message"></p>
    <button @click="count++">Count: <span x-text="count"></span></button>
</div>
```

### Key Differences

| Vue.js | Alpine.js |
|--------|-----------|
| `v-model` | `x-model` |
| `{{ expression }}` | `x-text="expression"` |
| `@click` | `@click` (same) |
| `v-if` | `x-if` (with `<template>`) |
| `v-for` | `x-for` (with `<template>`) |
| `v-show` | `x-show` |
| `methods` | functions in `x-data` |
| `computed` | getters in `x-data` |
| `watch` | `$watch()` or `$effect()` |

## Debugging Tips

### Enable Alpine Debug Mode

```javascript
// In development, add this to see Alpine logs
document.addEventListener('alpine:init', () => {
    console.log('Alpine initializing...')
})

document.addEventListener('alpine:initialized', () => {
    console.log('Alpine initialized!')
})
```

### Inspect Component Data

```html
<div x-data="{ count: 0 }">
    <button @click="console.log($data)">Log Component Data</button>
    <span x-text="count"></span>
</div>
```

### Track Reactive Changes

```html
<div x-data="{
    count: 0,
    
    init() {
        this.$watch('count', (value) => {
            console.log('Count changed to:', value)
        })
    }
}">
    <button @click="count++">Increment</button>
    <span x-text="count"></span>
</div>
```

## Production Checklist

- [ ] Use Alpine CDN with specific version for production
- [ ] Enable CSP mode if using strict security headers
- [ ] Minimize inline JavaScript expressions
- [ ] Implement proper error handling for async operations
- [ ] Add loading states for user feedback
- [ ] Ensure keyboard accessibility
- [ ] Test with progressive enhancement (graceful degradation)
- [ ] Clean up event listeners and third-party integrations
- [ ] Use `x-cloak` to prevent flash of unstyled content
- [ ] Implement proper form validation and error messages
