# Reactivity and Lifecycle

Understanding Alpine.js's reactivity system and component lifecycle is essential for building efficient, bug-free applications. This guide covers how Alpine tracks state changes, when code runs, and how to manage component initialization and cleanup.

## Alpine's Reactivity System

Alpine uses a reactive system that automatically tracks dependencies and updates the DOM when data changes. Unlike frameworks with virtual DOM diffing, Alpine directly manipulates the DOM for better performance.

### How Reactivity Works

```html
<div x-data="{ count: 0 }">
    <!-- These elements depend on 'count' -->
    <span x-text="count"></span>
    <span x-text="count * 2"></span>
    <div x-show="count > 5">Shown when count > 5</div>
    
    <button @click="count++">Increment</button>
</div>
```

When `count` changes, Alpine automatically updates:
- Both `<span>` elements displaying `count`
- The visibility of the `<div>` with `x-show`

### Dependency Tracking

Alpine tracks which data properties each directive uses:

```html
<div x-data="{ 
    firstName: 'John',
    lastName: 'Doe'
}">
    <!-- This only depends on firstName -->
    <span x-text="firstName"></span>
    
    <!-- This depends on both firstName and lastName -->
    <span x-text="firstName + ' ' + lastName"></span>
</div>
```

Changing `lastName` only re-renders the second span, not the first.

### Reactive Arrays and Objects

Arrays and objects are also reactive:

```html
<div x-data="{ 
    items: ['Apple', 'Banana'],
    user: { name: 'John', age: 30 }
}">
    <template x-for="item in items">
        <span x-text="item"></span>
    </template>
    
    <p>Name: <span x-text="user.name"></span></p>
    <p>Age: <span x-text="user.age"></span></p>
    
    <button @click="items.push('Cherry')">Add Item</button>
    <button @click="user.age++">Age Up</button>
</div>
```

### Replacing Arrays/Objects

To maintain reactivity, replace entire arrays/objects rather than modifying in place:

```html
<div x-data="{ 
    items: [1, 2, 3]
}">
    <template x-for="item in items">
        <span x-text="item"></span>
    </template>
    
    <!-- Good: Replace entire array -->
    <button @click="items = [4, 5, 6]">Replace</button>
    
    <!-- Also good: Use array methods that return new arrays -->
    <button @click="items = items.filter(i => i > 1)">Filter</button>
    <button @click="items = [...items, 4]">Spread add</button>
</div>
```

## Component Lifecycle

Alpine components go through several lifecycle stages. Understanding when code runs helps prevent bugs and manage side effects.

### x-init (Initialization)

The `x-init` directive runs after the component's `x-data` is initialized:

```html
<div x-data="{ count: 0 }" x-init="count = 5; fetchData()">
    <span x-text="count"></span>
</div>
```

Common uses for `x-init`:
- Set initial values from external sources
- Make API calls to fetch data
- Initialize third-party libraries
- Set up event listeners

### Lifecycle Hooks in x-data

Alpine provides lifecycle methods you can define in your `x-data` object:

```html
<div x-data="{
    count: 0,
    
    // Called when component is initialized
    init() {
        console.log('Component initialized')
        this.count = 5
    },
    
    // Called when component is destroyed
    $destroy() {
        console.log('Component destroyed')
        // Cleanup here
    }
}">
    <span x-text="count"></span>
</div>
```

**Note:** The `$destroy()` method is called automatically when elements are removed from DOM.

### $watch (Reactive Watching)

Watch specific data properties for changes:

```html
<div x-data="{
    count: 0,
    
    init() {
        this.$watch('count', (value) => {
            console.log('Count changed to:', value)
            // Side effect here
        })
    }
}">
    <button @click="count++">Increment</button>
    <span x-text="count"></span>
</div>
```

### Deep Watching

Watch nested properties with dot notation:

```html
<div x-data="{
    user: { name: 'John', prefs: { theme: 'light' } },
    
    init() {
        // Watch nested property
        this.$watch('user.prefs.theme', (value) => {
            console.log('Theme changed to:', value)
            document.body.className = value
        })
    }
}">
    <button @click="user.prefs.theme = 'dark'">Switch Theme</button>
</div>
```

### $effect (Reactive Effect)

Run code whenever any accessed reactive property changes:

```html
<div x-data="{
    firstName: '',
    lastName: '',
    
    init() {
        this.$effect(() => {
            // Automatically runs when firstName or lastName changes
            console.log('Full name:', this.firstName + ' ' + this.lastName)
        })
    }
}">
    <input x-model="firstName" placeholder="First name">
    <input x-model="lastName" placeholder="Last name">
</div>
```

**Key difference from $watch:** `$effect` automatically tracks all reactive properties it accesses, while `$watch` requires explicit property names.

## Lifecycle Event Hooks

Alpine dispatches custom events at key lifecycle moments:

### alpine:init

Fires before Alpine initializes any components. Use for global setup:

```html
<script defer src="/alpine.js"></script>
<script>
document.addEventListener('alpine:init', () => {
    // Register custom directives, magics, stores
    Alpine.directive('foo', ...)
    Alpine.magic('bar', ...)
    console.log('Alpine is initializing...')
})
</script>
```

### alpine:initialized

Fires after all components are initialized:

```html
<script>
document.addEventListener('alpine:initialized', () => {
    console.log('All Alpine components are ready')
    // Safe to interact with Alpine components here
})
</script>
```

### alpine:beforeUpdate, alpine:updated

Fires before/after DOM updates:

```html
<div x-data="{ count: 0 }">
    <span 
        x-text="count"
        @alpine:beforeUpdate="console.log('Before update:', $el)"
        @alpine:updated="console.log('After update:', $el)">
    </span>
    <button @click="count++">Increment</button>
</div>
```

### alpine:componentInitialized

Fires when a specific component is initialized:

```html
<div x-data="{ name: 'test' }" x-init="$dispatch('alpine:componentInitialized', { name: this.name })">
    Component with name: <span x-text="name"></span>
</div>
```

## Initialization Order

Understanding initialization order helps debug complex components:

```html
<div x-data="outerData()">
    <!-- 1. Outer x-data object created -->
    <!-- 2. Outer x-init runs -->
    
    <div x-data="innerData()">
        <!-- 3. Inner x-data object created -->
        <!-- 4. Inner x-init runs -->
        
        <span x-text="message"></span>
        <!-- 5. x-text directive evaluates -->
    </div>
</div>

<script>
function outerData() {
    return {
        message: 'outer',
        init() {
            console.log('Outer init')
        }
    }
}

function innerData() {
    return {
        init() {
            console.log('Inner init')
        }
    }
}
</script>
```

Console output:
1. "Outer init"
2. "Inner init"

## Cleanup and Memory Management

Properly clean up resources to prevent memory leaks:

### Removing Event Listeners

```html
<div x-data="{
    handler: null,
    
    init() {
        this.handler = (e) => console.log('Scroll:', e.target.scrollY)
        window.addEventListener('scroll', this.handler)
    },
    
    $destroy() {
        window.removeEventListener('scroll', this.handler)
    }
}">
    Scrollable content
</div>
```

### Clearing Timeouts and Intervals

```html
<div x-data="{
    timer: null,
    count: 0,
    
    init() {
        this.timer = setInterval(() => {
            this.count++
        }, 1000)
    },
    
    $destroy() {
        clearInterval(this.timer)
    }
}">
    <span x-text="count"></span>
</div>
```

### Cleaning Up Third-Party Libraries

```html
<div x-data="{
    chart: null,
    
    init() {
        this.chart = Chart.js($el.querySelector('canvas'), { ... })
    },
    
    $destroy() {
        if (this.chart) {
            this.chart.destroy()
        }
    }
}">
    <canvas></canvas>
</div>
```

## Advanced Reactivity Patterns

### Computed Properties

Use getters for derived values:

```html
<div x-data="{
    firstName: 'John',
    lastName: 'Doe',
    
    get fullName() {
        return this.firstName + ' ' + this.lastName
    },
    
    get greeting() {
        return `Hello, ${this.fullName}!`
    }
}">
    <p x-text="greeting"></p>
    <p x-text="fullName.length + ' characters'"></p>
</div>
```

Computed properties are cached and only re-evaluate when dependencies change.

### Reactive Filters

```html
<div x-data="{
    items: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    filter: '',
    
    get filteredItems() {
        if (!this.filter) return this.items
        return this.items.filter(item => 
            item.toString().includes(this.filter)
        )
    }
}">
    <input x-model="filter" placeholder="Filter...">
    
    <template x-for="item in filteredItems">
        <span x-text="item + ' '"></span>
    </template>
    
    <p>Showing <span x-text="filteredItems.length"></span> of <span x-text="items.length"></span> items</p>
</div>
```

### Conditional Reactivity

Temporarily disable reactivity for performance:

```html
<div x-data="{
    bulkUpdating: false,
    items: [],
    
    async loadBulkData() {
        this.bulkUpdating = true
        
        // Bulk update without triggering intermediate renders
        for (let i = 0; i < 1000; i++) {
            this.items.push(i)
        }
        
        // Force single update after bulk operation
        this.$nextTick(() => {
            this.bulkUpdating = false
        })
    }
}">
    <button @click="loadBulkData">Load 1000 items</button>
    <p>Items: <span x-text="items.length"></span></p>
</div>
```

### $nextTick (Next DOM Update)

Schedule code to run after next DOM update:

```html
<div x-data="{ 
    show: false,
    focused: false
}">
    <button @click="show = true">Show Modal</button>
    
    <div x-show="show" x-ref="modal">
        <input 
            x-ref="input"
            x-init="$nextTick(() => $refs.input.focus())">
    </div>
    
    <script>
        // Or using $nextTick in method
        function showModal() {
            show = true
            Alpine.$nextTick(() => {
                document.querySelector('input').focus()
            })
        }
    </script>
</div>
```

Useful for:
- Focusing elements after they appear
- Measuring element dimensions after transitions
- Interacting with third-party libraries that need DOM to be ready

## Performance Optimization

### Minimize x-data Scope

Keep `x-data` objects small and focused:

```html
<!-- Good: Small, focused components -->
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>
    <div x-show="open">Content</div>
</div>

<!-- Avoid: Large monolithic state -->
<div x-data="{ 
    user: {...}, posts: [], comments: [], 
    settings: {...}, theme: '', notifications: []
}">
    <!-- Everything in one component -->
</div>
```

### Use x-show vs x-if Appropriately

- `x-show`: Element stays in DOM, just hidden (faster toggle)
- `x-if`: Element removed from DOM (better for expensive components)

```html
<!-- Frequent toggling: use x-show -->
<div x-data="{ expanded: false }">
    <div x-show="expanded" x-transition>Details</div>
</div>

<!-- Rarely shown, expensive component: use x-if -->
<div x-data="{ showChart: false }">
    <template x-if="showChart">
        <expensive-chart-component></expensive-chart-component>
    </template>
</div>
```

### Debounce Expensive Operations

```html
<div x-data="{
    query: '',
    results: [],
    
    init() {
        this.$watch('query', debounce((value) => {
            this.fetchResults(value)
        }, 300))
    },
    
    async fetchResults(query) {
        // API call here
    }
}">
    <input x-model="query" placeholder="Search...">
</div>

<script>
function debounce(fn, delay) {
    let timeout
    return (...args) => {
        clearTimeout(timeout)
        timeout = setTimeout(() => fn(...args), delay)
    }
}
</script>
```

See [Advanced Patterns](10-advanced-patterns.md) for more performance optimization techniques.
