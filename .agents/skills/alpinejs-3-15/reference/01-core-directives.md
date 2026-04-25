# Core Directives

Core directives are the foundation of Alpine.js, enabling reactive data binding and DOM manipulation directly in HTML.

## x-data

Declares a reactive data object that powers an Alpine component. All child elements can access this data.

### Basic Usage

```html
<div x-data="{ count: 0, message: 'Hello' }">
    <span x-text="message"></span>
    <button @click="count++">Count: <span x-text="count"></span></button>
</div>
```

### Methods in x-data

```html
<div x-data="{ 
    count: 0,
    increment() { this.count++ },
    decrement() { this.count-- },
    get doubled() { return this.count * 2 }
}">
    <button @click="decrement">-</button>
    <span x-text="count"></span>
    <button @click="increment">+</button>
    <p>Doubled: <span x-text="doubled"></span></p>
</div>
```

### Scope and Inheritance

Child elements inherit parent's data. Nested `x-data` can override or extend:

```html
<div x-data="{ foo: 'parent' }">
    <span x-text="foo"></span> <!-- "parent" -->
    
    <div x-data="{ bar: 'child' }">
        <span x-text="foo"></span> <!-- "parent" (inherited) -->
        <span x-text="bar"></span> <!-- "child" (local) -->
        
        <div x-data="{ foo: 'nested' }">
            <span x-text="foo"></span> <!-- "nested" (overridden) -->
        </div>
    </div>
</div>
```

### Using External JavaScript Objects

```html
<script>
    function counterData() {
        return {
            count: 0,
            increment() { this.count++ },
            init() {
                console.log('Component initialized')
            }
        }
    }
</script>

<div x-data="counterData">
    <button @click="increment">Count: <span x-text="count"></span></button>
</div>
```

## x-text

Sets the text content of an element to the result of a JavaScript expression.

```html
<div x-data="{ name: 'Alpine' }">
    <span x-text="name"></span>
    <span x-text="'Hello, ' + name + '!']></span>
    <span x-text="name.length"></span>
</div>
```

**Shorthand:** Use `:` for text binding (equivalent to `x-text`):

```html
<span :text="name"></span>
```

## x-html

Sets the inner HTML of an element. Use cautiously with untrusted input to prevent XSS.

```html
<div x-data="{ html: '<strong>Bold text</strong>' }">
    <div x-html="html"></div>
</div>
```

**Security:** Always sanitize user-generated content before using `x-html`.

## x-show

Toggles element visibility by setting `display: none` when false.

```html
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>
    <div x-show="open">Visible when open is true</div>
</div>
```

### With Transitions

```html
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>
    <div x-show="open" x-transition>
        Content fades in/out
    </div>
</div>
```

## x-if vs x-show

Use `x-if` to conditionally render elements (add/remove from DOM), not just hide them.

### x-if (DOM Manipulation)

```html
<div x-data="{ show: false }">
    <button @click="show = !show">Toggle</button>
    
    <template x-if="show">
        <div>This is completely removed from DOM when false</div>
    </template>
</div>
```

**Key Differences:**
- `x-show`: Element stays in DOM, CSS `display: none` applied
- `x-if`: Element added/removed from DOM (use with `<template>` tag)
- Use `x-if` for expensive components or when you need lifecycle hooks

## x-for

Renders a list of items by iterating over arrays or objects.

### Iterating Arrays

```html
<div x-data="{ items: ['Apple', 'Banana', 'Cherry'] }">
    <ul>
        <template x-for="fruit in items">
            <li x-text="fruit"></li>
        </template>
    </ul>
</div>
```

### With Index

```html
<div x-data="{ items: ['Apple', 'Banana', 'Cherry'] }">
    <template x-for="(fruit, index) in items">
        <div x-text="index + 1 + '. ' + fruit"></div>
    </template>
</div>
```

### Iterating Objects

```html
<div x-data="{ user: { name: 'John', age: 30, city: 'NYC' } }">
    <template x-for="(value, key) in user">
        <div><span x-text="key"></span>: <span x-text="value"></span></div>
    </template>
</div>
```

### Keyed Lists (Important for Performance)

Always provide a unique key for list items to help Alpine track elements:

```html
<div x-data="{ todos: [
    { id: 1, text: 'Learn Alpine' },
    { id: 2, text: 'Build something' }
] }">
    <template x-for="todo in todos" :key="todo.id">
        <div>
            <span x-text="todo.text"></span>
            <button @click="todos = todos.filter(t => t.id !== todo.id)">Delete</button>
        </div>
    </template>
</div>
```

### Filtering and Transforming

```html
<div x-data="{ 
    items: [1, 2, 3, 4, 5],
    get evens() { return this.items.filter(n => n % 2 === 0) }
}">
    <template x-for="num in evens">
        <span x-text="num"></span>
    </template>
</div>
```

## x-bind

Dynamically binds HTML attributes to expressions.

### Basic Attribute Binding

```html
<div x-data="{ href: '/about', disabled: false }">
    <a :href="href" :class="{'is-active': true}">Link</a>
    <button :disabled="disabled" :aria-label="'Submit form'">Submit</button>
</div>
```

### Shorthand Syntax

Use `:` prefix for attribute binding:

```html
<img :src="imageUrl" :alt="imageAlt">
<input :value="defaultValue" :placeholder="hint">
```

### Class Binding

```html
<div x-data="{ active: true, error: false }">
    <div 
        :class="{
            'active': active,
            'error': error,
            'disabled': !active && !error
        }">
        Dynamic classes
    </div>
</div>
```

### Style Binding

```html
<div x-data="{ color: 'red', size: 20 }">
    <div 
        :style="{
            'color': color,
            'font-size': size + 'px'
        }">
        Styled text
    </div>
</div>
```

## x-model

Two-way data binding for form inputs. See [Form Handling](02-form-handling.md) for detailed coverage.

### Basic Usage

```html
<div x-data="{ text: '' }">
    <input type="text" x-model="text">
    <span x-text="text"></span>
</div>
```

## x-init

Executes JavaScript when an element is initialized by Alpine.

```html
<div x-data="{ count: 0 }" x-init="count = 5; fetchData()">
    <span x-text="count"></span>
</div>
```

### With External Functions

```html
<div x-init="initComponent($el)"></div>

<script>
function initComponent(element) {
    console.log('Element initialized:', element)
}
</script>
```

## x-ref

Creates a reference to an element accessible via `$refs`:

```html
<div x-data="{ focused: false }">
    <input x-ref="nameInput" type="text">
    <button @click="$refs.nameInput.focus()">Focus Input</button>
</div>
```

## x-id

Generates unique, consistent IDs for elements (useful for accessibility labels):

```html
<div x-data>
    <input x-ref="email" type="email">
    <label :for="$id('email')">Email</label>
</div>
```

This ensures the `for` attribute matches the input's generated ID.

## x-cloak

Prevents "flash of unstyled content" by hiding elements until Alpine loads:

```html
<style>
    [x-cloak] { display: none !important; }
</style>

<div x-data="{ loaded: false }" x-cloak>
    <div x-show="loaded">Content after Alpine loads</div>
</div>
```

Add the CSS rule to hide any element with `x-cloak` attribute until Alpine removes it.

## x-ignore / x-ignore.self

Prevents Alpine from processing an element and its children (or just the element itself):

```html
<div x-data="{ count: 0 }">
    <!-- This won't be processed by Alpine -->
    <div x-ignore>
        <span x-text="count"></span> <!-- Won't update -->
    </div>
    
    <!-- Only this element is ignored, children are processed -->
    <div x-ignore.self>
        <span x-text="count"></span> <!-- Will update -->
    </div>
</div>
```

## Directive Modifiers

Many directives support modifiers to alter behavior:

### Event Modifiers (x-on / @)

```html
<button @click.prevent="submit">Submit</button>
<button @click.stop="close">Close</button>
<button @click.self="handle">Handle if clicked directly</button>
<input @keyup.enter="submit">
<input @keydown.esc="cancel">
```

Common modifiers:
- `.prevent`: Calls `event.preventDefault()`
- `.stop`: Calls `event.stopPropagation()`
- `.self`: Only triggers if event originated from element itself
- `.once`: Triggers only once
- `.passive`: Adds `{ passive: true }` to event listener
- `.capture`: Uses capture phase for event
- `.window`: Binds to window instead of element
- `.document`: Binds to document instead of element
- `.debounce(300)`: Debounces handler by 300ms
- `.throttle(100)`: Throttles handler to once per 100ms

### Model Modifiers (x-model)

```html
<input x-model.lazy="value">       <!-- Update on blur, not input -->
<input x-model.number="quantity">  <!-- Auto-convert to number -->
<input x-model.boolean="flag">     <!-- Convert to boolean -->
<textarea x-model.trim="text">     <!-- Trim whitespace -->
<select x-model="selected">        <!-- Bind select value -->
```

### Transition Modifiers (x-transition)

```html
<div x-show="open" x-transition.opacity>
    Fades in/out
</div>

<div x-show="open" x-transition.duration.500ms>
    500ms transition
</div>

<div x-show="open" x-transition.enter.start="opacity: 0">
    Custom enter animation
</div>
```

See [Transitions and Effects](03-transitions-effects.md) for detailed transition documentation.
