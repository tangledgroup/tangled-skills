# Swapping and Settling

How htmx inserts server responses into the DOM, with support for animations, transitions, and fine-grained content selection.

## Swap Styles

`hx-swap` controls how response content replaces the target.

| Style | Description |
|-------|-------------|
| `innerHTML` | Replace inner HTML of target (default) |
| `outerHTML` | Replace the entire target element |
| `beforebegin` | Insert before the target |
| `afterbegin` | Insert at start of target |
| `beforeend` | Append to end of target |
| `afterend` | Insert after the target |
| `delete` | Remove the target regardless of response |
| `none` | Do not swap (useful with events only) |
| `morph` | DOM morphing via idiomorph extension |
| `morph:outerHTML` | Morph outer HTML via idiomorph |
| `morph:innerHTML` | Morph inner children via idiomorph |

```html
<!-- Default: innerHTML -->
<div hx-get="/data" hx-swap="innerHTML"></div>

<!-- Replace entire element -->
<tr hx-get="/row" hx-swap="outerHTML"></tr>

<!-- Append to list -->
<ul hx-get="/items/next" hx-swap="beforeend"></ul>

<!-- Delete row after request completes -->
<button hx-delete="/item/1" hx-swap="delete" hx-target="closest tr">Remove</button>
```

## Swap Options (Modifiers)

Append options to `hx-swap` with spaces:

| Option | Syntax | Description |
|--------|--------|-------------|
| Transition | `transition:true/false` | Enable CSS transitions on swap targets |
| Swap Delay | `swap:<ms>` | Delay before swapping content |
| Settle Delay | `settle:<ms>` | Delay after swap before settling changes |
| Ignore Title | `ignoreTitle:true` | Don't extract `<title>` from response |
| Scroll | `scroll:<target>:<behavior>` | Scroll target into view after swap |
| Show | `show:<element>` | Scroll specified element into view |

```html
<!-- Smooth transition with delay -->
<div hx-get="/data" hx-swap="innerHTML transition:true swap:100ms"></div>

<!-- Swap, then scroll result into view -->
<div hx-get="/search" hx-swap="innerHTML scroll:top"></div>

<!-- Show a specific element after swap -->
<div hx-get="/form" hx-swap="innerHTML show:#error-message:true"></div>
```

### Scroll Options
- `scroll:top` — scroll window to top
- `scroll:bottom` — scroll window to bottom
- `scroll:target` — scroll target element into view
- `scroll:target:smooth` — smooth scroll target into view

## CSS Transitions

htmx supports CSS transitions on swap targets using the `transition:true` modifier.

### Swap Transition Model

1. htmx adds `.htmx-swapping` to the target
2. After `swap:` delay, content is swapped
3. htmx adds `.htmx-settling` and removes `.htmx-swapping`
4. Settling occurs (attributes updated, scripts run)
5. htmx removes `.htmx-settling`

```css
/* Fade out during swap, fade in after */
.htmx-swapping {
  opacity: 0;
  transition: opacity 500ms ease-in;
}

.htmx-settling {
  opacity: 1;
  transition: opacity 500ms ease-in;
}
```

### Settle Transition Model

For attribute changes (not full swaps), use the settle classes:

```css
/* Flash green on successful update */
.htmx-settling {
  background-color: lightgreen;
  transition: background-color 0.5s;
}
```

## View Transitions API

htmx supports the native View Transitions API for smooth page transitions:

```html
<button hx-get="/page" hx-swap="innerHTML transition:true">
  Navigate
</button>
```

With `htmx.config.viewTransitionsEnabled = true`, htmx wraps swaps in `document.startViewTransition()`. Style with `::view-transition-old()` and `::view-transition-new()`.

## Out of Band Swaps (`hx-swap-oob`)

Update elements outside the target by including them in the server response.

### Full Element Replace
```html
<!-- Server response includes: -->
<div id="clock" hx-swap-oob="true">3:00 PM</div>
```

The element with `id="clock"` is found and replaced, regardless of where it appears in the response.

### OOB Swap Styles
```html
<!-- Replace innerHTML -->
<div id="notifications" hx-swap-oob="innerHTML">
  <p>New notification</p>
</div>

<!-- Append to element -->
<ul id="items" hx-swap-oob="beforeend">
  <li>New item</li>
</ul>

<!-- Replace outerHTML -->
<tr id="row-1" hx-swap-oob="outerHTML">
  <td>Updated cell</td>
</tr>
```

### Template for Table Rows

Use `<template>` to swap table rows without breaking structure:

```html
<!-- Server response: -->
<template hx-swap-oob="true">
  <tr id="row-1">
    <td>Updated data</td>
  </tr>
</template>
```

## Selecting Content (`hx-select`)

Select a subset of the response before swapping. Uses CSS selectors.

```html
<!-- Only swap the .content div from the response -->
<div hx-get="/page" hx-target="#result" hx-select=".content"></div>
```

### `hx-select-oob`

Select content for out-of-band swaps:

```html
<div hx-get="/dashboard" hx-select="#main-content"
     hx-select-oob="#clock #notifications">
</div>
```

## Preserving Content (`hx-preserve`)

Keep certain elements unchanged during a swap. Uses CSS selectors on the response content.

```html
<!-- Server returns full form, but preserve the file input -->
<form hx-post="/save" hx-target="#form-container" hx-preserve="input[type=file]">
  <input name="name" />
  <input type="file" name="attachment" />
</form>
```

The `input[type=file]` in the response is ignored; the existing one stays.

## Settle Workflow

After swapping, htmx performs "settling":
1. Computes diff between old and new DOM attributes
2. Fires `htmx:beforeSettle` event
3. Applies attribute changes
4. Runs any `<script>` tags in response (if `htmx.config.allowScriptTags = true`)
5. Fires `htmx:afterSettle` event
6. Fires `htmx:load` event on the target

Override settle behavior with `hx-on::before-settle` or `hx-on::after-settle`.
