# Feedback Components

## Alert

Informs users about important events with color-coded severity levels.

### Class Names

- **component**: `alert`
- **style**: `alert-outline`, `alert-dash`, `alert-soft`
- **color**: `alert-info`, `alert-success`, `alert-warning`, `alert-error`
- **direction**: `alert-vertical`, `alert-horizontal`

### Syntax

```html
<div role="alert" class="alert alert-info">
  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
  <span>Information message here.</span>
</div>

<div role="alert" class="alert alert-error alert-outline">
  <span>Error: Something went wrong.</span>
</div>
```

### Rules

- Add `sm:alert-horizontal` for responsive layouts (vertical on mobile, horizontal on desktop)
- Combine one style, one color, and one direction class

## Loading

Animated loading indicators in multiple styles.

### Class Names

- **component**: `loading`
- **style**: `loading-spinner`, `loading-dots`, `loading-ring`, `loading-ball`, `loading-bars`, `loading-infinity`
- **size**: `loading-xs`, `loading-sm`, `loading-md`, `loading-lg`, `loading-xl`

### Syntax

```html
<span class="loading loading-spinner loading-lg"></span>
<span class="loading loading-dots loading-sm"></span>
<span class="loading loading-ball"></span>
<span class="loading loading-infinity loading-md text-error"></span>
```

## Progress

Linear progress bar using the native `<progress>` element.

### Class Names

- **component**: `progress`
- **color**: `progress-neutral`, `progress-primary`, `progress-secondary`, `progress-accent`, `progress-info`, `progress-success`, `progress-warning`, `progress-error`

### Syntax

```html
<progress class="progress progress-primary w-56" value="70" max="100"></progress>
<progress class="progress progress-error w-full" value="30" max="100"></progress>
```

### Rules

- Must specify `value` and `max` attributes

## Radial Progress

Circular progress indicator using CSS custom properties.

### Class Names

- **component**: `radial-progress`

### Syntax

```html
<div class="radial-progress text-primary" style="--value:70; --size:6rem; --thickness:8px;" role="progressbar" aria-valuenow="70">70%</div>
```

### Rules

- `--value` CSS variable must be a number between 0 and 100
- Add `aria-valuenow` and `role="progressbar"` for accessibility
- Use `--size` to set diameter (default `5rem`) and `--thickness` for indicator thickness
- Use `<div>` instead of `<progress>` because browsers can't display text inside `<progress>`

## Skeleton

Placeholder shimmer effect for loading states.

### Class Names

- **component**: `skeleton`
- **modifier**: `skeleton-text`

### Syntax

```html
<div class="skeleton w-52 h-32"></div>

<!-- Text skeleton -->
<div class="skeleton skeleton-text h-4 w-20"></div>
<div class="skeleton skeleton-text h-4 w-40"></div>
```

### Rules

- Set dimensions with `h-*` and `w-*` utility classes

## Toast

Positioned container for stacking notification elements at page corners.

### Class Names

- **component**: `toast`
- **placement**: `toast-start`, `toast-center`, `toast-end`, `toast-top`, `toast-middle`, `toast-bottom`

### Syntax

```html
<div class="toast toast-top toast-end">
  <div class="alert alert-info">
    <span>New message received!</span>
  </div>
</div>

<div class="toast toast-bottom">
  <div class="alert alert-success"><span>Saved successfully</span></div>
  <div class="alert alert-warning"><span>Please review changes</span></div>
</div>
```

## Tooltip

Shows a message on hover over an element.

### Class Names

- **component**: `tooltip`
- **modifier**: `tooltip-open`
- **placement**: `tooltip-top`, `tooltip-bottom`, `tooltip-left`, `tooltip-right`
- **color**: `tooltip-primary`, `tooltip-secondary`, `tooltip-accent`, `tooltip-info`, `tooltip-success`, `tooltip-warning`, `tooltip-error`

### Syntax

```html
<div class="tooltip tooltip-bottom" data-tip="Helpful message">
  <button class="btn">Hover me</button>
</div>

<div class="tooltip tooltip-primary" data-tip="Primary tip">
  <span class="link">Hover the link</span>
</div>
```

### Rules

- `data-tip` attribute contains the tooltip text
- `tooltip-open` keeps the tooltip permanently visible
