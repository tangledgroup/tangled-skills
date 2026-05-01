# Events & Modifiers

## x-on (shorthand: `@`)

Listens for DOM events and executes a JavaScript expression. Works with any browser event name.

```html
<button @click="doSomething()">Click</button>
<input @keyup.enter="submit()">
<div @mouseenter="hovered = true" @mouseleave="hovered = false">
```

Event names must be lowercase (HTML attributes are case-insensitive). For camelCase custom events, use the `.camel` modifier.

**Accessing the event object**: Use `$event` magic property:

```html
<button @click="$event.target.remove()">Remove Me</button>
```

**Method reference without parentheses**: Alpine passes the event object as the first argument:

```html
<button @click="handleClick">...</button>
<script>
    function handleClick(e) {
        console.log(e.target)
    }
</script>
```

## Keyboard Event Modifiers

Listen for specific keys on `keydown`/`keyup`:

```html
<input @keyup.enter="submit()">
<input @keyup.shift.enter="submitWithShift()">
<input @keyup.page-down="scrollDown()">
```

Common key modifiers:

- `.shift`, `.ctrl`, `.alt`, `.meta` (Cmd/Win key)
- `.enter`, `.escape`, `.tab`, `.space`
- `.up`, `.down`, `.left`, `.right` (arrow keys)
- `.caps-lock`, `.equal`, `.period`, `.comma`, `.slash`

Any valid `KeyboardEvent.key` value works as a modifier in kebab-case.

## Mouse Event Modifiers

Filter click events by modifier key state:

```html
<button @click="selectItem()"
        @click.shift="addToSelection()"
        @click.ctrl="multiSelect()">
```

Works on `click`, `auxclick`, `contextmenu`, `dblclick`, `mouseover`, `mousemove`, `mouseenter`, `mouseleave`, `mouseout`, `mouseup`, `mousedown`.

## Event Modifiers

### .prevent

Equivalent to `event.preventDefault()`:

```html
<form @submit.prevent="handleSubmit">
    <button>Submit</button>
</form>
```

### .stop

Equivalent to `event.stopPropagation()`:

```html
<div @click="parentClick()">
    <button @click.stop>Stops bubbling to parent</button>
</div>
```

### .self

Only fires if the event target is the element itself (not a child):

```html
<button @click.self="handleClick">
    Click me, not the image inside
    <img src="...">
</button>
```

### .once

Handler executes only once:

```html
<button @click.once="init()">Initialize</button>
```

### .outside

Fires when a click happens outside the element. Essential for dropdowns and modals:

```html
<div x-show="open" @click.outside="open = false">
    Close when clicking elsewhere
</div>
```

Note: the expression only evaluates when the element is visible, preventing race conditions.

### .window

Registers the listener on `window` instead of the element:

```html
<div @keyup.escape.window="modalOpen = false">
    Closes modal on Escape from anywhere on the page
</div>
```

### .document

Same as `.window` but registers on `document`:

```html
<div @click.document="handleClick">...</div>
```

### .debounce

Delay handler until after a period of inactivity (default: 250ms):

```html
<input @input.debounce="search()">
<input @input.debounce.500ms="search()">
```

### .throttle

Limit handler to fire at most once per interval (default: 250ms):

```html
<div @scroll.window.throttle="handleScroll">...</div>
<div @scroll.window.throttle.750ms="handleScroll">...</div>
```

### .passive

Optimize scroll/touch performance by marking the listener as passive:

```html
<div @touchstart.passive="handleTouch">...</div>
```

### .passive.false

Explicitly set `passive: false` (needed when calling `preventDefault()` in touch handlers):

```html
<div @touchmove.passive.false="handleTouch">...</div>
```

### .camel

Convert kebab-case event name to camelCase internally:

```html
<div @custom-event.camel="handleEvent()">
    <!-- Listens for 'customEvent' -->
</div>
```

### .dot

Preserve dots in event names (dots are otherwise treated as modifier separators):

```html
<div @custom-event.dot="handleEvent()">
    <!-- Listens for 'custom.event' -->
</div>
```

## Combining Modifiers

Modifiers chain together with dots:

```html
<form @submit.prevent.once="submitOnce">
<input @keyup.shift.enter="submitWithShift">
<div @scroll.window.throttle.500ms.passive="onScroll">
```

## Custom Events

Alpine can listen for any DOM event including custom ones. Combine with `$dispatch`:

```html
<div x-data @item-selected="handleSelection($event.detail)">
    <button @click="$dispatch('item-selected', { id: 42 })">
        Select Item
    </button>
</div>
```

For nested components where event bubbling causes issues, use `.window` to capture at the window level instead.
