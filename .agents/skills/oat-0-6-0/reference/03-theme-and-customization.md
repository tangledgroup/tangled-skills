# Theme and Customization

## CSS Variable System

OAT's entire visual design is driven by CSS custom properties defined in `01-theme.css` under the `@layer theme` layer. Override any variable in your own CSS (included after OAT) to customize the look.

### Color Variables

All color variables use `light-dark()` for automatic system dark mode support.

| Variable | Purpose | Light Default | Dark Default |
|----------|---------|--------------|-------------|
| `--background` | Page background | `#fff` | `#09090b` |
| `--foreground` | Primary text color | `#09090b` | `#fafafa` |
| `--card` | Card surface background | `#fff` | `#18181b` |
| `--card-foreground` | Text on card surfaces | `#09090b` | `#fafafa` |
| `--primary` | Primary buttons, links, accents | `#574747` | `#fafafa` |
| `--primary-foreground` | Text on primary background | `#fafafa` | `#18181b` |
| `--secondary` | Secondary button surfaces | `#f4f4f5` | `#27272a` |
| `--secondary-foreground` | Text on secondary surfaces | `#574747` | `#fafafa` |
| `--muted` | Subtle background surfaces | `#f4f4f5` | `#27272a` |
| `--muted-foreground` | Muted/subtle text | `#71717a` | `#a1a1aa` |
| `--faint` | Very subtle backgrounds | `#fafafa` | `#1e1e21` |
| `--faint-foreground` | Very subtle text | `#a1a1aa` | `#71717a` |
| `--accent` | Accent hover surfaces | `#f4f4f5` | `#27272a` |
| `--accent-foreground` | Text on accent surfaces | `#242427` | `#fafafa` |
| `--danger` | Error/danger color | `#d32f2f` | `#f4807b` |
| `--danger-foreground` | Text on danger background | `#fafafa` | `#18181b` |
| `--success` | Success/positive color | `#008032` | `#6cc070` |
| `--success-foreground` | Text on success background | `#fafafa` | `#18181b` |
| `--warning` | Warning/caution color | `#a65b00` | `#f0a030` |
| `--warning-foreground` | Text on warning background | `#09090b` | `#09090b` |
| `--border` | Border/divider color | `#d4d4d8` | `#52525b` |
| `--input` | Input field border | `#d4d4d8` | `#52525b` |
| `--ring` | Focus ring color | `#574747` | `#d4d4d8` |

### Spacing Scale

| Variable | Value |
|----------|-------|
| `--space-1` | 0.25rem |
| `--space-2` | 0.5rem |
| `--space-3` | 0.75rem |
| `--space-4` | 1rem |
| `--space-5` | 1.25rem |
| `--space-6` | 1.5rem |
| `--space-8` | 2rem |
| `--space-10` | 2.5rem |
| `--space-12` | 3rem |
| `--space-14` | 3.5rem |
| `--space-16` | 4rem |
| `--space-18` | 4.5rem |

### Border Radius

| Variable | Value |
|----------|-------|
| `--radius-small` | 0.125rem |
| `--radius-medium` | 0.375rem |
| `--radius-large` | 0.75rem |
| `--radius-full` | 9999px |

### Typography Scale

| Variable | Value | Notes |
|----------|-------|-------|
| `--text-1` | `clamp(1.75rem, 1.5rem + 1.1vw, 2.25rem)` | h1 (fluid) |
| `--text-2` | `clamp(1.5rem, 1.3rem + 0.8vw, 1.875rem)` | h2 (fluid) |
| `--text-3` | `clamp(1.25rem, 1.1rem + 0.5vw, 1.5rem)` | h3 (fluid) |
| `--text-4` | `clamp(1.125rem, 1.05rem + 0.3vw, 1.25rem)` | h4 (fluid) |
| `--text-5` | 1.125rem | h5 (fixed) |
| `--text-6` | 1rem | Body text |
| `--text-7` | 0.875rem | Small/caption |
| `--text-8` | 0.75rem | Extra small |
| `--text-regular` | `var(--text-6)` | Alias for body text |

### Font Weights

| Variable | Value |
|----------|-------|
| `--font-normal` | 400 |
| `--font-medium` | 500 |
| `--font-semibold` | 600 |
| `--font-bold` | 600 |

### Shadows

| Variable | Value |
|----------|-------|
| `--shadow-small` | `0 1px 2px 0 rgb(0 0 0 / 0.05)` |
| `--shadow-medium` | Two-layer shadow at 0.1 opacity |
| `--shadow-large` | Two-layer shadow for modals/dropdowns |

### Transitions

| Variable | Value |
|----------|-------|
| `--transition-fast` | 120ms cubic-bezier(0.4, 0, 0.2, 1) |
| `--transition` | 200ms cubic-bezier(0.4, 0, 0.2, 1) |

### Other Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `--bar-height` | 0.5rem | Progress/meter bar height |
| `--leading-normal` | 1.5 | Default line height |
| `--font-sans` | `system-ui, sans-serif` | Primary font family |
| `--font-mono` | `ui-monospace, Consolas, monospace` | Monospace font family |
| `--z-dropdown` | 50 | Dropdown z-index |
| `--z-modal` | 200 | Modal/dialog z-index |

## Overriding Variables

To customize, create your own CSS file and include it **after** the OAT CSS:

```html
<link rel="stylesheet" href="oat.min.css">
<link rel="stylesheet" href="my-theme.css">
```

In `my-theme.css`:

```css
:root {
  --primary: #6366f1;
  --primary-foreground: #ffffff;
  --radius-medium: 0.5rem;
}
```

## Dark Mode Customization

For dark-mode-specific overrides, scope inside `[data-theme="dark"]`:

```css
[data-theme="dark"] {
  --primary: #818cf8;
  --background: #0f172a;
  --card: #1e293b;
}
```

Note: By default, OAT uses `color-scheme: light dark` with `light-dark()` functions for automatic system dark mode. The `data-theme="dark"` attribute is for explicit control.

## Example: Brown Theme (OAT Default)

```css
:root {
  --primary: #574747;
  --primary-foreground: #fafafa;
  --secondary: #f4f4f5;
  --secondary-foreground: #574747;
  --ring: #574747;
  --danger: #df514c;
}
```

## Selective Inclusion

For minimal bundles, include only what you need:

```css
/* Required base */
@import '@knadh/oat/css/00-base.css';
@import '@knadh/oat/css/01-theme.css';

/* Your overrides (after theme, before components) */
:root {
  --primary: #3b82f6;
}

/* Only needed components */
@import '@knadh/oat/css/button.css';
@import '@knadh/oat/css/card.css';
@import '@knadh/oat/css/form.css';
```
