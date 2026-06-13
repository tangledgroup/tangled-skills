# Utilities and Helpers

## Flexbox Utilities

| Class | CSS |
|-------|-----|
| `.flex` | `display: flex` |
| `.flex-col` | `flex-direction: column` |
| `.items-center` | `align-items: center` |
| `.justify-center` | `justify-content: center` |
| `.justify-between` | `justify-content: space-between` |
| `.justify-end` | `justify-content: flex-end` |

## Stack Utilities

| Class | Description |
|-------|-------------|
| `.hstack` | Horizontal flex stack with `gap: var(--space-3)`, wrap, children have zero margin |
| `.vstack` | Vertical flex stack with `gap: var(--space-3)` |

`.hstack` is the most commonly used layout helper. It creates a responsive horizontal row that wraps on small screens, with consistent gap spacing and automatic child margin reset.

```html
<div class="hstack">
  <button>One</button>
  <button>Two</button>
  <span>Some text</span>
</div>
```

## Gap Utilities

| Class | CSS |
|-------|-----|
| `.gap-1` | `gap: var(--space-1)` (0.25rem) |
| `.gap-2` | `gap: var(--space-2)` (0.5rem) |
| `.gap-4` | `gap: var(--space-4)` (1rem) |

## Text Alignment

| Class | CSS |
|-------|-----|
| `.align-left` | `text-align: start` |
| `.align-center` | `text-align: center` |
| `.align-right` | `text-align: end` |

## Text Color Utilities

| Class | CSS |
|-------|-----|
| `.text-light` | `color: var(--muted-foreground)` |
| `.text-lighter` | `color: var(--faint-foreground)` |

## Margin Utilities

| Class | CSS |
|-------|-----|
| `.mt-2` | `margin-block-start: var(--space-2)` |
| `.mt-4` | `margin-block-start: var(--space-4)` |
| `.mt-6` | `margin-block-start: var(--space-6)` |
| `.mb-2` | `margin-block-end: var(--space-2)` |
| `.mb-4` | `margin-block-end: var(--space-4)` |
| `.mb-6` | `margin-block-end: var(--space-6)` |

## Padding Utilities

| Class | CSS |
|-------|-----|
| `.p-4` | `padding: var(--space-4)` |

## Width Utilities

| Class | CSS |
|-------|-----|
| `.w-100` | `width: 100%` |

## Unstyled

Removes default list styles and link decoration:

```html
<ul class="unstyled">
  <li>No bullets</li>
</ul>
<ol class="unstyled">
  <li>No numbers</li>
</ol>
<a href="#" class="unstyled">No underline</a>
```

Applies: `list-style: none`, `text-decoration: none`, `padding: 0`.

---

## Animation Classes

### Pop-In Animation

`.animate-pop-in` — Swing-in animation for modals and overlays.

```html
<dialog class="animate-pop-in">
  ...
</dialog>
```

**Behavior**: Enters from above with perspective rotation (rotateX -15deg, translateZ -80px). Uses `@starting-style` for entry animation. Exit via `[data-state="closing"]`. Backdrop opacity transition included.

### Slide-In Animation

`.animate-slide-in` — Slide-in animation for toasts and notifications.

```html
<div class="toast animate-slide-in">
  Notification content
</div>
```

**Behavior**: Slides in from right (translateX 100%). Exit via `[data-state="closing"]` sliding back out.

### Dialog Backdrop

Native `dialog::backdrop` has built-in opacity transition (150ms). Uses `@starting-style` for entry fade.

---

## Reduced Motion Support

OAT respects `prefers-reduced-motion: reduce`:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

All animations and transitions are effectively disabled when the user prefers reduced motion. This is applied at the `@layer animations` level.
