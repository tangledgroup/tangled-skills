# Magics & Globals

## Magic Properties

Magic properties are special `$`-prefixed values available within Alpine expressions.

### $el

Reference to the current DOM element:

```html
<button @click="$el.textContent = 'Clicked!'">Click me</button>
<div x-init="new SomeLibrary($el)"></div>
```

### $store

Access global stores registered with `Alpine.store()`:

```html
<button @click="$store.darkMode.toggle()">Toggle Dark Mode</button>
<div :class="$store.darkMode.on && 'bg-black'">Content</div>
```

Stores are defined in an `alpine:init` listener (script tag) or before `Alpine.start()` (module):

```js
// Script tag approach
document.addEventListener('alpine:init', () => {
    Alpine.store('darkMode', {
        on: false,
        toggle() { this.on = !this.on }
    })
})

// Module approach
import Alpine from 'alpinejs'
Alpine.store('darkMode', { on: false, toggle() { this.on = !this.on } })
Alpine.start()
```

**Single-value stores**: Store simple values directly:

```js
Alpine.store('count', 0)
// Usage: $store.count, $store.count++
```

**Store init() method**: Automatically called when the store is registered:

```js
Alpine.store('darkMode', {
    init() {
        this.on = window.matchMedia('(prefers-color-scheme: dark)').matches
    }
})
```

**External access**: Read a store value from outside Alpine:

```js
Alpine.store('darkMode').toggle()
```

### $watch

Watch a property and run a callback when it changes. Receives new value and old value:

```html
<div x-data="{ open: false }"
     x-init="$watch('open', (value, oldValue) => console.log(value, oldValue))">
    <button @click="open = !open">Toggle</button>
</div>
```

**Dot notation** for nested properties:

```html
<div x-data="{ user: { name: 'Alice' } }"
     x-init="$watch('user.name', value => console.log(value))">
```

**Deep watching**: `$watch` detects changes at any nesting level. When watching a parent object, the callback receives the entire new/old object:

```html
<div x-data="{ foo: { bar: 'baz' } }"
     x-init="$watch('foo', (value, oldValue) => console.log(value, oldValue))">
```

Warning: modifying a watched property inside its own `$watch` callback causes an infinite loop.

### $dispatch

Dispatch custom browser events. Shortcut for `element.dispatchEvent(new CustomEvent(...))`:

```html
<div @notify="alert('Notified!')">
    <button @click="$dispatch('notify')">Notify</button>
</div>
```

**Passing data**:

```html
<div @notify="alert($event.detail.message)">
    <button @click="$dispatch('notify', { message: 'Hello!' })">Notify</button>
</div>
```

**Event propagation note**: Because of event bubbling, nested components may need `.window` modifier to capture dispatched events from child nodes.

### $nextTick

Execute code after Alpine finishes reactive DOM updates:

```html
<div x-data="{ title: 'Hello' }">
    <button @click="
        title = 'Hello World!';
        $nextTick(() => { console.log($el.innerText) });
    " x-text="title"></button>
</div>
```

**As a promise** (async/await):

```html
<button @click="
    title = 'Hello World!';
    await $nextTick();
    console.log($el.innerText);
">
```

### $refs

Access DOM elements by key (assigned with `x-ref`):

```html
<button @click="$refs.input.focus()">Focus</button>
<input x-ref="input">
```

### $id

Generates unique IDs for accessibility attribute pairing:

```html
<label :for="$id('input')">Name</label>
<input :id="$id('input')" x-model="name">
```

Calling `$id('input')` multiple times with the same key returns the same ID.

### $nextTick (in x-init)

Commonly used in `x-init` to run code after full component rendering, similar to React's `useEffect(..., [])`:

```html
<div x-init="$nextTick(() => { /* DOM is ready */ })">
```

## Globals

### Alpine.data()

Register reusable component definitions. Components are referenced by name in `x-data`:

```html
<div x-data="dropdown()">
    <button @click="toggle()">Toggle</button>
    <div x-show="open">Contents...</div>
</div>

<script>
    document.addEventListener('alpine:init', () => {
        Alpine.data('dropdown', () => ({
            open: false,
            toggle() { this.open = !this.open }
        }))
    })
</script>
```

**From a module bundle**:

```js
import Alpine from 'alpinejs'

Alpine.data('dropdown', () => ({
    open: false,
    toggle() { this.open = !this.open }
}))

Alpine.start()
```

**Initial parameters**: Pass arguments when referencing as a function:

```html
<div x-data="counter(10)">
```

```js
Alpine.data('counter', (start = 0) => ({
    count: start,
    increment() { this.count++ }
}))
```

**init() functions**: Automatically executed before rendering:

```js
Alpine.data('fetcher', (url) => ({
    data: null,
    init() {
        fetch(url).then(r => r.json()).then(d => this.data = d)
    }
}))
```

### Alpine.store()

Register global reactive state accessible from any component via `$store`:

```js
document.addEventListener('alpine:init', () => {
    Alpine.store('cart', {
        items: [],
        add(item) { this.items.push(item) },
        get total() { return this.items.length }
    })
})
```

```html
<span x-text="$store.cart.total"> items in cart</span>
<button x-data @click="$store.cart.add({ name: 'Widget' })">Add</button>
```

### Alpine.bind()

Register reusable attribute bundles for `x-bind`:

```html
<button x-bind="buttonAttrs"></button>

<script>
    document.addEventListener('alpine:init', () => {
        Alpine.bind('buttonAttrs', () => ({
            'type': 'button',
            '@click'() { this.doSomething() },
            ':disabled'() { return this.shouldDisable }
        }))
    })
</script>
```

Each key in the returned object is treated as an Alpine directive. Values can be static strings or functions that return dynamic values.
