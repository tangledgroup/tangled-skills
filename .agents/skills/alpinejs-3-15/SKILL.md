---
name: alpinejs-3-15
description: A skill for building reactive user interfaces with Alpine.js 3.15, a minimal JavaScript framework that uses HTML-first declarative syntax with directives like x-data, x-model, and x-show. Use when creating interactive web components, forms, dropdowns, modals, and dynamic UI elements without build tools or complex setup.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "3.15.11"
tags:
  - javascript
  - frontend
  - reactive
  - html
  - directives
  - web-components
  - lightweight-framework
category: frontend-development
external_references:
  - https://alpinejs.dev/
  - https://github.com/alpinejs/alpine
---

# Alpine.js 3.15

## Overview

Alpine.js is a rugged, minimal framework for composing behavior directly in your markup. Think of it like jQuery for the modern web — drop in a script tag and start building reactive components. It uses HTML attributes (directives) to declare interactivity inline with your markup, requiring no build step, no virtual DOM, and no JavaScript component files.

Alpine provides 15+ directives, 6 magic properties, and 2 global methods for building everything from simple toggles to complex stateful UIs. It uses Vue.js's reactivity engine under the hood but exposes it through a declarative HTML-first API. At approximately 7KB gzipped, it is one of the smallest reactive frameworks available.

## When to Use

- Adding interactivity to static HTML pages without a build step
- Building dropdowns, modals, tabs, accordions, and form components
- Sprinkling reactive behavior into server-rendered templates (Laravel Blade, Django, etc.)
- Prototyping UI interactions quickly
- Replacing jQuery-based DOM manipulation with declarative reactive syntax
- Adding client-side interactivity alongside backend frameworks
- Building accessible components with focus trapping (`x-trap`)
- Creating reusable component patterns with `Alpine.data()`

## Core Concepts

**Directives** are HTML attributes prefixed with `x-` that declare reactive behavior. For example, `x-data` defines a component's state, `x-show` toggles visibility, and `@click` (shorthand for `x-on:click`) listens for events.

**Components** are scoped by `x-data`. Every Alpine component starts with an `x-data` directive that declares reactive data. Child elements within the `x-data` scope can reference and modify this data through other directives.

**Reactivity** means when data changes, everything that depends on it updates automatically. Alpine tracks property access through JavaScript Proxies (via Vue's reactivity engine) and re-evaluates dependent expressions.

**Magics** are special `$`-prefixed properties available within Alpine expressions, such as `$el` (current DOM element), `$store` (global state), `$dispatch` (event dispatching), and `$watch` (reactive watchers).

## Installation / Setup

### From a CDN Script Tag

The simplest approach. Add Alpine to your HTML with `defer`:

```html
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.15.11/dist/cdn.min.js"></script>
```

The `defer` attribute is required — Alpine must initialize after the DOM is parsed. For production, pin to a specific version rather than using `@3.x.x`.

### As an NPM Module

For projects with a build step:

```js
import Alpine from 'alpinejs'

window.Alpine = Alpine  // optional, useful for devtools debugging
Alpine.start()
```

Register any plugins or extensions between the import and `Alpine.start()`. Call `Alpine.start()` only once per page.

### Plugins

Official plugins are loaded before Alpine's core script:

```html
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/collapse@3.x.x/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/persist@3.x.x/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
```

Via NPM:

```js
import Alpine from 'alpinejs'
import collapse from '@alpinejs/collapse'
import persist from '@alpinejs/persist'

Alpine.plugin(collapse)
Alpine.plugin(persist)
Alpine.start()
```

Available plugins: Mask, Intersect, Resize, Persist, Collapse, Focus (formerly Trap), Anchor, Morph, Sort.

## Usage Examples

### Counter Component

```html
<div x-data="{ count: 0 }">
    <button @click="count++">Increment</button>
    <span x-text="count"></span>
</div>
```

### Dropdown with Click-Outside

```html
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>
    <div x-show="open" @click.outside="open = false">
        Dropdown contents...
    </div>
</div>
```

### Search with Filtering

```html
<div x-data="{
    search: '',
    items: ['apple', 'banana', 'apricot'],
    get filtered() {
        return this.items.filter(i => i.startsWith(this.search))
    }
}">
    <input x-model="search" placeholder="Search...">
    <ul>
        <template x-for="item in filtered" :key="item">
            <li x-text="item"></li>
        </template>
    </ul>
</div>
```

### Reusable Component with Alpine.data()

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

## Advanced Topics

**Directives Reference**: All 15+ directives with syntax, modifiers, and examples → [Directives](reference/01-directives.md)

**Magics and Globals**: `$el`, `$store`, `$watch`, `$dispatch`, `$nextTick`, `$refs`, `Alpine.data()`, `Alpine.store()`, `Alpine.bind()` → [Magics & Globals](reference/02-magics-globals.md)

**Plugins Guide**: Mask, Intersect, Resize, Persist, Collapse, Focus, Anchor, Morph, Sort with installation and usage → [Plugins](reference/03-plugins.md)

**Event Modifiers**: `.prevent`, `.stop`, `.outside`, `.window`, `.debounce`, `.throttle`, `.once`, `.self`, `.camel`, `.passive` and more → [Events & Modifiers](reference/04-events-modifiers.md)

**Advanced Patterns**: CSP build, reactivity internals (`Alpine.reactive()`, `Alpine.effect()`), extending Alpine with custom directives/magics → [Advanced Topics](reference/05-advanced-topics.md)
