# Directives Reference

## x-data

Defines a component and its reactive data. All other directives within its scope can access this data.

```html
<div x-data="{ open: false, count: 0 }">
    <!-- child elements can use open and count -->
</div>
```

**Scope**: Properties are available to all children, even inside nested `x-data` components (inner scopes shadow outer ones).

**Methods and getters** can be defined inline:

```html
<div x-data="{
    open: false,
    toggle() { this.open = !this.open },
    get status() { return this.open ? 'open' : 'closed' }
}">
    <button @click="toggle()">Toggle</button>
    <span x-text="status"></span>
</div>
```

**Empty x-data**: `x-data` without a value creates a component scope with no initial data, useful for standalone directives like `x-init`:

```html
<div x-data>
    <span x-init="console.log('initialized')"></span>
</div>
```

## x-init

Runs code when an element is initialized by Alpine. Can be placed on any element inside or outside an `x-data` block.

```html
<div x-data="{ posts: [] }" x-init="posts = await (await fetch('/posts')).json()">
```

**Auto-evaluated init() method**: If the `x-data` object contains an `init()` method, Alpine calls it automatically before rendering:

```html
<div x-data="{
    init() { console.log('component ready') },
    count: 0
}">
```

**$nextTick in x-init**: Wait until after Alpine finishes rendering:

```html
<div x-init="$nextTick(() => { /* DOM is fully updated */ })"></div>
```

## x-show

Toggles element visibility based on a JavaScript expression. Uses inline `display: none` when false.

```html
<div x-show="open">Contents...</div>
```

With transitions (combine with `x-transition`):

```html
<div x-show="open" x-transition>Contents...</div>
```

**.important modifier**: Forces `display: none !important` to override CSS specificity:

```html
<div x-show.important="open">Contents...</div>
```

## x-if

Conditionally adds or removes elements from the DOM entirely (unlike `x-show` which only toggles visibility). Must be used on a `<template>` element with a single root child.

```html
<template x-if="open">
    <div>Contents...</div>
</template>
```

Caveats: does not support `x-transition` transitions, and the template must contain exactly one root element.

## x-bind (shorthand: `:`)

Dynamically sets HTML attributes based on JavaScript expressions.

```html
<input :placeholder="placeholderText">
<div :class="open ? 'visible' : 'hidden'">
```

**Binding classes**: Most common use case is conditional class application:

```html
<!-- Ternary approach -->
<div :class="isOpen ? 'open' : 'closed'">

<!-- Shorthand with logical operators -->
<div :class="isOpen || 'closed'">
<div :class="!isOpen && 'closed'">

<!-- Object syntax (Alpine 3.13+) -->
<div :class="{ 'is-active': isActive, 'is-inactive': !isActive }">
```

**Binding multiple attributes**: Use `x-bind` with an object:

```html
<img x-bind="{ src: imageSrc, alt: imageAlt, title: imageTitle }">
```

## x-text

Sets the text content of an element to the result of a JavaScript expression. Updates reactively.

```html
<span x-text="username"></span>
<span x-text="count * 2"></span>
```

## x-html

Sets the innerHTML of an element. Use only with trusted content — never with user-provided data (XSS risk).

```html
<div x-html="trustedHtmlContent"></div>
```

## x-model

Two-way binds an input element's value to Alpine data. Works with `<input type="text">`, `<textarea>`, `<input type="checkbox">`, `<input type="radio">`, `<select>`, and `<input type="range">`.

```html
<input x-model="message">
<span x-text="message"></span>
```

**Checkbox with boolean**: Binds checked state to a boolean.

```html
<input type="checkbox" x-model="agree">
```

**Multiple checkboxes bound to array**:

```html
<input type="checkbox" value="red" x-model="colors">
<input type="checkbox" value="blue" x-model="colors">
<!-- colors becomes ['red', 'blue'] -->
```

**Radio inputs**:

```html
<input type="radio" value="yes" x-model="answer">
<input type="radio" value="no" x-model="answer">
```

**Select inputs**:

```html
<select x-model="color">
    <option>Red</option>
    <option>Blue</option>
</select>
```

**Multiple select**: Binds to an array.

```html
<select x-model="colors" multiple>
    <option>Red</option>
    <option>Blue</option>
</select>
```

**Dynamically populated options**:

```html
<select x-model="color">
    <template x-for="c in colors" :key="c">
        <option x-text="c"></option>
    </template>
</select>
```

### x-model Modifiers

- `.lazy` — sync on focus-out instead of every keystroke
- `.change` — sync on the native `change` event (value must have changed)
- `.blur` — sync on blur regardless of value change
- `.enter` — sync when Enter key is pressed
- `.number` — coerce value to a JavaScript number
- `.boolean` — coerce value to boolean (accepts "true"/"false" or 1/0)
- `.debounce` or `.debounce.500ms` — delay sync after inactivity
- `.throttle` or `.throttle.500ms` — limit sync to a fixed interval
- `.fill` — use the input's `value` attribute as initial data if bound property is empty

Modifiers can be combined:

```html
<input x-model.blur.enter="search">
<input x-model.debounce.300ms.number="quantity">
```

**Programmatic access**: The `_x_model` property on a bound element exposes `.get()` and `.set()`:

```js
$refs.input._x_model.get()   // returns bound value
$refs.input._x_model.set('new value')  // sets bound value
```

## x-modelable

Exposes an Alpine property as a target for `x-model` from a parent scope. Useful for abstracting components:

```html
<div x-data="{ number: 5 }">
    <div x-data="{ count: 0 }" x-modelable="count" x-model="number">
        <button @click="count++">Increment</button>
    </div>
    <span x-text="number"></span>
</div>
```

## x-for

Iterates over arrays or objects to create DOM elements. Must be on a `<template>` element with a single root child.

```html
<template x-for="item in items" :key="item.id">
    <li x-text="item.name"></li>
</template>
```

**Accessing index**:

```html
<template x-for="(item, index) in items" :key="item.id">
    <li><span x-text="index + ': '"></span> <span x-text="item.name"></span></li>
</template>
```

**Iterating over objects**:

```html
<template x-for="(value, key) in object">
    <li><span x-text="key"></span>: <span x-text="value"></span></li>
</template>
```

**Iterating over a range**:

```html
<template x-for="i in 10" :key="i">
    <li x-text="i"></li>
</template>
```

Keys are important when items can be reordered, added, or removed. Use a unique identifier as the `:key` value.

## x-transition

Adds CSS transitions to elements shown/hidden with `x-show`.

```html
<div x-show="open" x-transition>Contents...</div>
```

**Customizing duration**:

```html
<div x-show="open" x-transition.duration.300ms>
<div x-show="open" x-transition.enter.duration.300ms.leave.duration.150ms>
```

**Custom easing**:

```html
<div x-show="open" x-transition.enter.ease-in.out.ease-out>
```

**Custom CSS classes** (full control):

```html
<div x-show="open"
    x-transition:enter="transition ease-out duration-200"
    x-transition:enter-start="opacity-0 transform scale-90"
    x-transition:enter-end="opacity-100 transform scale-100"
    x-transition:leave="transition ease-in duration-150"
    x-transition:leave-start="opacity-100 transform scale-100"
    x-transition:leave-end="opacity-0 transform scale-90">
```

**Transition styles**:

```html
<div x-show="open"
    x-transition:enter-start="transform translate-y-2"
    x-transition:enter-end="transform translate-y-0">
```

## x-effect

Re-evaluates an expression whenever any of its reactive dependencies change. Unlike `$watch`, it runs immediately on init and auto-detects dependencies.

```html
<div x-data="{ label: 'Hello' }" x-effect="console.log(label)">
    <button @click="label += ' World!'">Change</button>
</div>
```

Differences from `$watch`: runs immediately (not lazy), no access to previous value, auto-detects dependencies instead of requiring a property name.

## x-ref / $refs

`x-ref` assigns a key to an element for direct DOM access via `$refs`:

```html
<button @click="$refs.input.focus()">Focus Input</button>
<input x-ref="input">
```

## x-cloak

Hides an element until Alpine finishes initializing. Requires CSS:

```css
[x-cloak] { display: none !important; }
```

```html
<span x-cloak x-show="false">Won't flicker on load</span>
```

## x-ignore

Prevents Alpine from initializing a section of the DOM. Useful when another framework manages that area.

```html
<div x-data="{ label: 'Hello' }">
    <div x-ignore>
        <span x-text="label"></span>  <!-- This won't be processed by Alpine -->
    </div>
</div>
```

## x-teleport

Moves a template's content to another part of the DOM. Useful for modals that need to escape z-index stacking contexts.

```html
<div x-data="{ open: false }">
    <button @click="open = true">Open Modal</button>
    <template x-teleport="body">
        <div x-show="open">Modal contents...</div>
    </template>
</div>
```

The selector accepts any valid CSS selector string (`body`, `#modal-container`, `.app`).
