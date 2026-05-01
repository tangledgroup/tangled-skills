# Theming Reference

Complete reference for Oat UI's CSS variable theming system.

## Theme Variables

All theme properties are defined as CSS custom properties on `:root` inside the `@layer theme` block. Override them in your own stylesheet loaded after Oat's CSS.

### Color Variables

Oat uses `light-dark()` for automatic light/dark mode support. Each variable has both a light and dark value.

**Core colors:**

- `--background` — Page background
- `--foreground` — Primary text color
- `--card` — Card background
- `--card-foreground` — Card text color

**Primary palette:**

- `--primary` — Primary buttons and links
- `--primary-foreground` — Text color on primary buttons

**Secondary palette:**

- `--secondary` — Secondary button background
- `--secondary-foreground` — Text color on secondary buttons

**Muted tones:**

- `--muted` — Muted (lighter) background
- `--muted-foreground` — Muted (lighter) text color
- `--faint` — Subtler than muted background
- `--faint-foreground` — Subtler than muted text color

**Accent:**

- `--accent` — Accent background
- `--accent-foreground` — Accent text color

**Semantic colors:**

- `--danger` — Error/danger color
- `--danger-foreground` — Text on danger background
- `--success` — Success color
- `--success-foreground` — Text on success background
- `--warning` — Warning color
- `--warning-foreground` — Text on warning background

**UI chrome:**

- `--border` — Border color (boxes, dividers)
- `--input` — Input borders
- `--ring` — Focus ring color

### Spacing Variables

Oat uses a consistent spacing scale based on `rem` units:

- `--space-1`: 0.25rem
- `--space-2`: 0.5rem
- `--space-3`: 0.75rem
- `--space-4`: 1rem
- `--space-5`: 1.25rem
- `--space-6`: 1.5rem
- `--space-8`: 2rem
- `--space-10`: 2.5rem
- `--space-12`: 3rem
- `--space-14`: 3.5rem
- `--space-16`: 4rem
- `--space-18`: 4.5rem

### Border Radius

- `--radius-small`: 0.125rem
- `--radius-medium`: 0.375rem
- `--radius-large`: 0.75rem
- `--radius-full`: 9999px

### Typography Variables

Font families:
- `--font-sans`: system-ui, sans-serif
- `--font-mono`: ui-monospace, Consolas, monospace

Font sizes (using `clamp()` for responsive sizing on headings):
- `--text-1`: clamp(1.75rem, 1.5rem + 1.1vw, 2.25rem) — h1
- `--text-2`: clamp(1.5rem, 1.3rem + 0.8vw, 1.875rem) — h2
- `--text-3`: clamp(1.25rem, 1.1rem + 0.5vw, 1.5rem) — h3
- `--text-4`: clamp(1.125rem, 1.05rem + 0.3vw, 1.25rem) — h4
- `--text-5`: 1.125rem — h5
- `--text-6`: 1rem — body text, h6
- `--text-7`: 0.875rem — small text
- `--text-8`: 0.75rem — extra small
- `--text-regular`: var(--text-6)

Font weights:
- `--font-normal`: 400
- `--font-medium`: 500
- `--font-semibold`: 600
- `--font-bold`: 600

Line height:
- `--leading-normal`: 1.5

### Shadows

- `--shadow-small`: 0 1px 2px 0 rgb(0 0 0 / 0.05)
- `--shadow-medium`: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)
- `--shadow-large`: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)

### Transitions

- `--transition-fast`: 120ms cubic-bezier(0.4, 0, 0.2, 1)
- `--transition`: 200ms cubic-bezier(0.4, 0, 0.2, 1)

### Z-index

- `--z-dropdown`: 50
- `--z-modal`: 200

### Bar height (for progress/meter bars)

- `--bar-height`: 0.5rem

## Dark Mode

Oat supports dark mode through two mechanisms:

**Automatic (system preference):** The `color-scheme: light dark` declaration and `light-dark()` CSS function handle automatic switching based on the user's OS/browser preference. No code needed.

**Manual toggle:** Add `data-theme="dark"` to `<body>` (or any ancestor) to force dark mode. Remove it for light mode.

```html
<body data-theme="dark">
  <!-- Content renders in dark theme -->
</body>
```

**Preventing FOUC:** Apply the theme attribute before rendering to avoid flash of unstyled content:

```javascript
(function() {
  var t = localStorage.getItem('theme');
  if (t) {
    document.documentElement.style.colorScheme = t;
    document.documentElement.setAttribute('data-theme', t);
  }
})();
```

**Customizing dark theme:** Scope overrides inside `[data-theme="dark"]`:

```css
[data-theme="dark"] {
  --background: #0a0a0f;
  --foreground: #e0e0e0;
  --primary: #818cf8;
  --primary-foreground: #0a0a0f;
}
```

## Example Theme: Default Oat Brown

The default light theme uses a brown primary color:

```css
--background: #fff;
--foreground: #09090b;
--card: #fff;
--card-foreground: #09090b;
--primary: #574747;
--primary-foreground: #fafafa;
--secondary: #f4f4f5;
--secondary-foreground: #574747;
--muted: #f4f4f5;
--muted-foreground: #71717a;
--faint: #fafafa;
--accent: #f4f4f5;
--danger: #df514c;
--danger-foreground: #fafafa;
--success: #4caf50;
--success-foreground: #fafafa;
--warning: #ff8c00;
--warning-foreground: #09090b;
--border: #d4d4d8;
--input: #d4d4d8;
--ring: #574747;
```

## Overriding Strategy

1. Include Oat's CSS first (`oat.min.css` or individual files)
2. Include your custom CSS after
3. Redefine only the variables you want to change on `:root` (for light mode) or `[data-theme="dark"]` (for dark mode)

```html
<head>
  <link rel="stylesheet" href="oat.min.css">
  <link rel="stylesheet" href="my-theme.css">
</head>
```

```css
/* my-theme.css */
:root {
  --primary: #6366f1;
  --primary-foreground: #ffffff;
  --radius-medium: 0.5rem;
  --font-sans: 'Inter', system-ui, sans-serif;
}
```

## Cascade Layers

Oat uses CSS `@layer` for clean style organization:

```css
@layer theme, base, components, animations, utilities;
```

Layers in priority order (lowest to highest):
1. `theme` — CSS variable definitions
2. `base` — Reset and base element styles
3. `components` — Component-specific styles
4. `animations` — Animation keyframes and classes
5. `utilities` — Helper utility classes

Your custom CSS outside any layer has higher priority than all Oat layers, making overrides straightforward without `!important`.
