# Event Handling

Alpine.js provides comprehensive event handling through the `x-on` directive (shorthand: `@`), supporting all standard browser events with powerful modifiers for common patterns.

## Basic Event Listeners

### Using x-on

```html
<div x-data="{ count: 0 }">
    <button x-on:click="count++">Click me</button>
    <span x-text="count"></span>
</div>
```

### Shorthand with @

```html
<div x-data="{ count: 0 }">
    <button @click="count++">Click me</button>
    <span x-text="count"></span>
</div>
```

The `@` shorthand is preferred for most use cases.

## Common Events

### Mouse Events

```html
<div x-data="{ 
    hovering: false,
    clicked: 0,
    dblClicked: 0
}">
    <div 
        @mouseenter="hovering = true"
        @mouseleave="hovering = false"
        @click="clicked++"
        @dblclick="dblClicked++"
        :class="{ 'hovered': hovering }">
        Hover over me!
        <p>Clicks: <span x-text="clicked"></span></p>
        <p>Double clicks: <span x-text="dblClicked"></span></p>
    </div>
</div>
```

### Keyboard Events

```html
<div x-data="{ keypressed: '' }">
    <input 
        type="text" 
        @keydown="keypressed = $event.key"
        placeholder="Type something...">
    <p>Last key: <span x-text="keypressed"></span></p>
</div>
```

### Form Events

```html
<div x-data="{ submitted: false }">
    <form @submit.prevent="submitted = true">
        <input type="text" required placeholder="Required field">
        <button type="submit">Submit</button>
    </form>
    <p x-show="submitted">Form submitted!</p>
</div>
```

### Focus/Blur Events

```html
<div x-data="{ focused: false }">
    <input 
        type="text" 
        @focus="focused = true"
        @blur="focused = false"
        :class="{ 'focused': focused }"
        placeholder="Focus me">
    <p x-text="focused ? 'Input is focused' : 'Input is not focused'"></p>
</div>
```

### Window and Document Events

```html
<div x-data="{ 
    scrollY: 0,
    windowWidth: window.innerWidth
}">
    <p>Scroll position: <span x-text="scrollY"></span></p>
    <p>Window width: <span x-text="windowWidth"></span></p>
    
    <script x-init="
        $watch('scrollY', value => console.log('Scrolled to:', value))
    "></script>
    <script>
        document.addEventListener('scroll', () => {
            Alpine.store('scrollY', window.scrollY)
        })
    </script>
</div>
```

Use `.window` and `.document` modifiers for binding to global events:

```html
<div x-data="{ scrollY: 0 }">
    <p>Scroll: <span x-text="scrollY"></span></p>
    
    <div @scroll.window="scrollY = window.scrollY"></div>
</div>
```

## Event Modifiers

### .prevent

Calls `event.preventDefault()` automatically:

```html
<!-- Before -->
<form @submit.prevent="submit">
    <button type="submit">Submit</button>
</form>

<!-- Equivalent to -->
<form @submit="($event) => { $event.preventDefault(); submit() }">
    <button type="submit">Submit</button>
</form>
```

### .stop

Calls `event.stopPropagation()` to prevent event bubbling:

```html
<div @click="handleParentClick">
    Parent
    <button @click.stop="handleButtonClick">
        Button (won't trigger parent)
    </button>
</div>
```

### .self

Only triggers handler if event originated from the element itself, not children:

```html
<div @click.self="handleDivClick">
    Click div directly
    <button @click="handleButtonClick">Button click won't trigger div</button>
</div>
```

### .once

Triggers handler only once:

```html
<button @click.once="init">Initialize (only works once)</button>
```

### .passive

Adds `{ passive: true }` to event listener (improves scroll performance):

```html
<div @scroll.passive="handleScroll"></div>
```

Use for scroll events where you won't call `preventDefault()`.

### .capture

Uses capture phase instead of bubble phase:

```html
<div @click.capture="parentHandler">
    Parent (captures first)
    <button @click="childHandler">Child</button>
</div>
```

Event flow: `parent (capture)` → `child` → `parent (bubble)`

### .window and .document

Binds event to window or document instead of element:

```html
<div x-data="{ 
    active: false,
    clickedOutside: false
}">
    <button @click="active = true">Toggle</button>
    
    <div x-show="active" @click.away="active = false">
        Click outside to close
    </div>
</div>
```

Note: `.away` is a special Alpine modifier that triggers when clicking outside the element.

## Keyboard Event Modifiers

### Key-Specific Handlers

```html
<input 
    type="text"
    @keydown.enter="submit"
    @keydown.escape="cancel"
    @keydown.tab="handleTab"
    placeholder="Press Enter to submit, Escape to cancel">
```

Supported keys: `enter`, `tab`, `esc` (escape), `space`, `up`, `down`, `left`, `right`, `delete`, etc.

### Multiple Keys

```html
<input 
    @keydown.enter.stop.prevent="submit"
    @keydown.esc="cancel">
```

### Key Combination Detection

```html
<div x-data="{ ctrlS: false, ctrlZ: false }">
    <div @keydown.ctrl.s.prevent="ctrlS = true; undo()">Ctrl+S pressed</div>
    <div @keydown.ctrl.z.prevent="ctrlZ = true; redo()">Ctrl+Z pressed</div>
    
    <p x-show="ctrlS">Saved!</p>
    <p x-show="ctrlZ">Undone!</p>
</div>
```

## Special Modifiers

### .away

Triggers when clicking outside the element:

```html
<div x-data="{ dropdownOpen: false }">
    <button @click="dropdownOpen = !dropdownOpen">Toggle Dropdown</button>
    
    <div x-show="dropdownOpen" 
         x-transition
         @click.away="dropdownOpen = false">
        <!-- Click outside closes dropdown -->
        <p>Dropdown content</p>
    </div>
</div>
```

### .outside (Alias for .away)

```html
<div @click.outside="closeModal"></div>
```

### .debounce(n)

Debounces handler by n milliseconds:

```html
<input 
    type="text" 
    x-model="query"
    @input.debounce.300="search">
    
<script>
function search() {
    console.log('Searching for:', query)
}
</script>
```

Only triggers after 300ms of no input.

### .throttle(n)

Limits handler to once every n milliseconds:

```html
<div @scroll.throttle.100="handleScroll">
    <p>Scroll position throttled to 100ms</p>
</div>
```

### .self with Events

```html
<div @click.self="close" style="padding: 2rem; background: #eee;">
    Click outside content to close
    <div style="background: white; padding: 1rem;">
        Content (clicking here won't close)
    </div>
</div>
```

## Event Object Access

Access the native event object via `$event`:

```html
<div x-data="{ 
    clickedX: 0,
    clickedY: 0,
    targetTag: ''
}">
    <div @click="handleClick($event)">Click anywhere</div>
    
    <p>X: <span x-text="clickedX"></span></p>
    <p>Y: <span x-text="clickedY"></span></p>
    <p>Target: <span x-text="targetTag"></span></p>
    
    <script>
        function handleClick(event) {
            clickedX = event.clientX
            clickedY = event.clientY
            targetTag = event.target.tagName
        }
    </script>
</div>
```

### Event Properties in Expressions

```html
<div x-data="{ color: 'red' }">
    <button 
        @click="color = $event.target.dataset.color"
        data-color="blue">
        Click to change color
    </button>
    
    <div :style="{ backgroundColor: color }"></div>
</div>
```

## Advanced Event Patterns

### Conditional Event Handlers

```html
<div x-data="{ disabled: false, count: 0 }">
    <button 
        @click="!disabled && count++"
        :disabled="disabled">
        Click (disabled: <span x-text="disabled"></span>)
    </button>
    <span x-text="count"></span>
</div>
```

### Multiple Handlers

```html
<button 
    @click="log('clicked')"
    @dblclick="log('double clicked')">
    Click or double-click
</button>

<script>
function log(msg) { console.log(msg) }
</script>
```

### Method Calls with Arguments

```html
<div x-data="{ 
    items: [1, 2, 3],
    remove(index) { this.items.splice(index, 1) },
    add(value) { this.items.push(value) }
}">
    <button @click="add(4)">Add 4</button>
    <template x-for="(item, index) in items">
        <span x-text="item + ' '"></span>
        <button @click="remove(index)">×</button>
    </template>
</div>
```

### Inline Expressions

```html
<div x-data="{ count: 0 }">
    <button @click="count = count + 1">+</button>
    <button @click="count--">-</button>
    <button @click="count = 0">Reset</button>
    <span x-text="count"></span>
</div>
```

### Ternary Expressions

```html
<div x-data="{ admin: true }">
    <button @click="admin ? deleteItem() : showPermissionError()">
        Delete Item
    </button>
</div>
```

## Drag and Drop Events

```html
<div x-data="{ 
    draggedItem: null,
    items: ['Item 1', 'Item 2', 'Item 3']
}">
    <template x-for="(item, index) in items">
        <div 
            draggable="true"
            @dragstart="draggedItem = item"
            @dragover.prevent
            @drop="items.splice(items.indexOf($event.dataTransfer.getData('text')), 1); items.push(draggedItem)"
            style="padding: 0.5rem; margin: 0.25rem; cursor: grab;">
            <span x-text="item"></span>
        </div>
    </template>
</div>
```

## Touch Events (Mobile)

```html
<div x-data="{ 
    touchX: 0,
    touchY: 0,
    swiped: ''
}">
    <div 
        @touchstart="touchX = $event.touches[0].clientX; touchY = $event.touches[0].clientY"
        @touchend="handleSwipe($event)"
        style="height: 200px; background: #eee;">
        Touch and swipe
    </div>
    
    <p x-text="swiped">
    
    <script>
        function handleSwipe(event) {
            const endX = event.changedTouches[0].clientX
            const endY = event.changedTouches[0].clientY
            const diffX = endX - touchX
            const diffY = endY - touchY
            
            if (Math.abs(diffX) > Math.abs(diffY)) {
                swiped = diffX > 50 ? 'Right' : 'Left'
            } else {
                swiped = diffY > 50 ? 'Down' : 'Up'
            }
        }
    </script>
</div>
```

## Best Practices

1. **Use `@` shorthand** for cleaner syntax (e.g., `@click` not `x-on:click`)
2. **Prevent default on forms** with `.prevent` modifier to avoid page reloads
3. **Stop propagation selectively** with `.stop` when needed
4. **Use `.self`** to distinguish between element and child clicks
5. **Debounced search inputs** with `.debounce(300)` for better performance
6. **Keyboard accessibility** - always include keyboard handlers for interactive elements
7. **Event cleanup** - remove event listeners in component cleanup if added manually

## Common Event Patterns

### Click Outside to Close

```html
<div x-data="{ open: false }">
    <button @click="open = true">Open</button>
    
    <div x-show="open" 
         x-transition
         @click.away="open = false"
         style="position: absolute; background: white; border: 1px solid #ccc;">
        Click outside to close
    </div>
</div>
```

### Enter Key Submits Form

```html
<form @submit.prevent="submit">
    <input type="text" x-model="query" @keydown.enter.prevent>
    <button type="submit">Search</button>
</form>
```

### Escape to Cancel

```html
<div x-data="{ editing: false }">
    <button @click="editing = true">Edit</button>
    
    <div x-show="editing" @keydown.escape.window="editing = false">
        <input type="text" x-model="value" autofocus>
        <p>Press Escape to cancel</p>
    </div>
</div>
```

See [Common Components](09-common-components.md) for complete component examples using these event patterns.
