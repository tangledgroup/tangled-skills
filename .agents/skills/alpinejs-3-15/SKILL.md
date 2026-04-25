---
name: alpinejs-3-15
description: A skill for building reactive user interfaces with Alpine.js 3.15, a minimal JavaScript framework that uses HTML-first declarative syntax with directives like x-data, x-model, and x-show. Use when creating interactive web components, forms, dropdowns, modals, and dynamic UI elements without build tools or complex setup.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - javascript
  - frontend
  - reactive
  - html
  - directives
  - web-components
  - lightweight-framework
category: frontend-development
required_environment_variables: []

external_references:
  - https://alpinejs.dev/
  - https://github.com/alpinejs/alpine
---
## Overview
A skill for building reactive user interfaces with Alpine.js 3.15, a minimal JavaScript framework that uses HTML-first declarative syntax with directives like x-data, x-model, and x-show. Use when creating interactive web components, forms, dropdowns, modals, and dynamic UI elements without build tools or complex setup.

Alpine.js is a minimal, performant JavaScript framework for building reactive user interfaces using HTML-first declarative syntax. Unlike traditional frameworks that require build steps or complex tooling, Alpine lives directly in your HTML markup using directives like `x-data`, `x-model`, and `x-show`. It's designed to be "just enough JavaScript" for making HTML elements interactive without the overhead of full frameworks.

## When to Use
- Building interactive UI components (dropdowns, modals, tabs, accordions)
- Adding reactivity to static HTML pages without build tools
- Creating forms with two-way data binding and validation
- Implementing real-time updates and live search features
- Prototyping rapid UI interactions in existing projects
- Migrating jQuery codebases to modern reactive patterns
- Building small to medium web applications without complex tooling

## Installation / Setup
### CDN Installation (Quick Start)

Include Alpine.js via CDN with the `defer` attribute:

```html
<html>
<head>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.15.0/dist/cdn.min.js"></script>
</head>
<body>
    <!-- Your Alpine code here -->
</body>
</html>
```

### NPM Installation (For Bundled Projects)

```bash
npm install alpinejs@3.15.0
```

```javascript
import Alpine from 'alpinejs'
Alpine.start()
```

### Plugin Installation

Install plugins BEFORE Alpine core:

```html
<!-- Plugins first -->
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/focus@3.15.0/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/persist@3.15.0/dist/cdn.min.js"></script>

<!-- Then Alpine core -->
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.15.0/dist/cdn.min.js"></script>
```

## Usage Examples
### Basic Counter Component

```html
<div x-data="{ count: 0 }">
    <button @click="count++">Increment</button>
    <span x-text="count"></span>
</div>
```

See [Core Directives](reference/01-core-directives.md) for detailed explanation of `x-data`, `@click`, and `x-text`.

### Two-Way Data Binding with Forms

```html
<div x-data="{ message: '' }">
    <input type="text" x-model="message">
    <p>You typed: <span x-text="message"></span></p>
</div>
```

Refer to [Form Handling](reference/02-form-handling.md) for complex form scenarios.

### Conditional Rendering

```html
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>
    <div x-show="open" x-transition>Content appears here</div>
</div>
```

See [Transitions and Effects](reference/03-transitions-effects.md) for animation details.

### Event Handling

```html
<div x-data="{ name: '' }">
    <input type="text" x-model="name" @keyup.enter="submit()">
    <button @click="submit()">Submit</button>
    
    <script>
        function submit() {
            alert('Name: ' + name)
        }
    </script>
</div>
```

Refer to [Event Directives](reference/04-event-handling.md) for event modifiers and advanced patterns.

## Core Concepts
Alpine.js revolves around these fundamental concepts:

1. **Reactive Data (`x-data`)**: Declares a reactive data object that powers the component
2. **Directives**: HTML attributes starting with `x-` that add behavior (e.g., `x-show`, `x-model`)
3. **Scope**: Child elements inherit parent's data; nested `x-data` can override properties
4. **Lifecycle Hooks**: Functions like `init()`, `x-init`, `$destroy()` for setup/cleanup

See [Reactivity and Lifecycle](reference/05-reactivity-lifecycle.md) for deep dive into Alpine's reactivity system.

## Advanced Topics
## Advanced Topics

- [Core Directives](reference/01-core-directives.md)
- [Form Handling](reference/02-form-handling.md)
- [Transitions Effects](reference/03-transitions-effects.md)
- [Event Handling](reference/04-event-handling.md)
- [Reactivity Lifecycle](reference/05-reactivity-lifecycle.md)
- [Magics Globals](reference/06-magics-globals.md)
- [Official Plugins](reference/07-official-plugins.md)
- [Extending Alpine](reference/08-extending-alpine.md)
- [Common Components](reference/09-common-components.md)
- [Advanced Patterns](reference/10-advanced-patterns.md)

## Troubleshooting
### Alpine not initializing

- Ensure `<script defer>` attribute is present
- Check that Alpine script loads before `x-data` elements render
- Verify no JavaScript errors in browser console

### x-model not updating

- Confirm input has correct `x-model="propertyName"` syntax
- Check that property exists in parent `x-data` object
- For checkboxes, use `x-model="arrayProperty"` for multiple selection

### Transitions not working

- Ensure element has unique key when using with `x-for`
- Add `x-transition:enter` and `x-transition:leave` modifiers explicitly
- Check CSS doesn't override Alpine's transition classes

### Event handlers not firing

- Verify event name matches browser events (e.g., `click`, not `onclick`)
- Use correct modifier syntax (e.g., `@click.prevent`, not `@click-prevent`)
- Ensure function is in scope or use arrow functions in `x-data`

For more solutions, see [Common Components](reference/09-common-components.md) for component-specific issues and [Extending Alpine](reference/08-extending-alpine.md) for custom directive debugging.

