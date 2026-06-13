# Advanced Topics

## CSP Build

Alpine's standard build uses `Function()` declarations to evaluate expressions from HTML attributes, which violates the `unsafe-eval` Content Security Policy directive. The CSP build avoids this for environments that enforce strict CSP.

**CDN**:
```html
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/csp@3.x.x/dist/cdn.min.js"></script>
```

**NPM**:
```js
import Alpine from '@alpinejs/csp'
Alpine.start()
```

**With nonce**:
```html
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'nonce-abc123'">
<script defer nonce="abc123" src="https://cdn.jsdelivr.net/npm/@alpinejs/csp@3.x.x/dist/cdn.min.js"></script>
```

**Supported expressions**: Object/array literals, property access, method calls, arithmetic, comparisons, ternary operators, logical operators, template literals.

**Not supported**: Inline function declarations (`function() {}`), arrow functions in attribute values, `new` keyword with inline constructors. Use pre-registered methods instead of inline functions.

## Reactivity Internals

Alpine uses Vue.js's reactivity engine. Two core functions power all reactivity:

### Alpine.reactive()

Wraps a plain JavaScript object in a Proxy that tracks get/set access:

```js
let data = { count: 1 }
let reactiveData = Alpine.reactive(data)

reactiveData.count = 2
console.log(data.count) // 2 — changes propagate through the proxy
```

### Alpine.effect()

Accepts a callback and automatically re-runs it when any reactive data accessed within it changes:

```js
let data = Alpine.reactive({ count: 1 })

Alpine.effect(() => {
    console.log('Count is:', data.count)
})

data.count = 2  // Logs: "Count is: 2"
data.count = 3  // Logs: "Count is: 3"
```

**Building a counter without Alpine syntax**:

```html
<button>Increment</button>
<span></span>
```

```js
let button = document.querySelector('button')
let span = document.querySelector('span')
let data = Alpine.reactive({ count: 0 })

Alpine.effect(() => {
    span.textContent = data.count
})

button.addEventListener('click', () => data.count++)
```

This demonstrates that Alpine's directives are essentially syntactic sugar over `Alpine.reactive()` and `Alpine.effect()`.

## Extending Alpine

Register custom directives, magics, and other extensions before Alpine initializes.

### Via Script Tag

Use the `alpine:init` event:

```html
<script src="/js/extensions.js" defer></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
```

```js
// extensions.js
document.addEventListener('alpine:init', () => {
    Alpine.directive('foo', ...)
})
```

### Via NPM Module

Register between import and `Alpine.start()`:

```js
import Alpine from 'alpinejs'

Alpine.directive('foo', ...)

Alpine.start()
```

### Custom Directives

```js
Alpine.directive('name', (el, { value, modifiers, expression }, { Alpine, effect, cleanup }) => {
    // value: the directive's value (e.g., 'bar' in x-foo.bar="baz")
    // modifiers: array of modifier names
    // expression: the raw expression string

    // Register cleanup functions that run when the element is destroyed
    cleanup(() => {
        // teardown logic
    })

    // Use effect() for reactive updates
    effect(() => {
        // re-runs when reactive dependencies change
    })
})
```

### Custom Magics

```js
Alpine.magic('name', (el) => {
    return () => {
        // logic here
    }
})

// Usage in template: $name()
```

### Custom Interceptors

Interceptors wrap values inside `x-data` to transform them:

```js
Alpine.intercept('log', (value, key, el) => {
    return new Proxy(value, {
        set(target, property, value) {
            console.log(`Setting ${String(key)}.${String(property)} to`, value)
            target[property] = value
            return true
        }
    })
})

// Usage: x-data="{ count: $log(0) }"
```

## Computed Properties with Getters

Use JavaScript getters inside `x-data` for computed values that reactively update:

```html
<div x-data="{
    items: ['apple', 'banana', 'apricot'],
    search: '',
    get filtered() {
        return this.items.filter(i => i.includes(this.search))
    }
}">
    <input x-model="search">
    <template x-for="item in filtered" :key="item">
        <li x-text="item"></li>
    </template>
</div>
```

Note: inside the getter function, use `this.propertyName` to reference other data properties (not just `propertyName` as in template expressions).

## Lifecycle Events

Alpine dispatches custom events at key lifecycle points:

- `alpine:init` — fired after Alpine loads but before it walks the DOM. Use for registering extensions.
- `alpine:initialized` — fired after Alpine has fully initialized all components on the page.
- `alpine:before-processing` — fired before Alpine processes a specific element.
- `Alpine.addScopeProperty()` — add properties to all component scopes.

```js
document.addEventListener('alpine:initialized', () => {
    console.log('All Alpine components are ready')
})
```

## Working with External Libraries

Use `x-init` and `$nextTick` to integrate third-party libraries:

```html
<div x-data="{ date: null }"
     x-init="$nextTick(() => {
         new Pikaday({ field: $refs.input, onSelect: d => date = d })
     })">
    <input x-ref="input">
    <span x-text="date"></span>
</div>
```

Use `$watch` to react to data changes from external sources:

```html
<div x-data="{ chartData: [] }"
     x-init="$watch('chartData', value => {
         myChart.update(value)
     })">
```

## Key Differences from Other Frameworks

- **No build step required** — works directly in the browser with a script tag
- **HTML-first** — behavior is declared inline with markup, not in separate JS files
- **No virtual DOM** — Alpine manipulates the real DOM directly using targeted updates
- **Component scope via x-data** — no need for custom elements or Web Components API
- **Lightweight** — ~7KB gzipped vs React (~42KB), Vue (~33KB)
- **Interoperable** — can coexist with other frameworks, jQuery, or any library on the same page
