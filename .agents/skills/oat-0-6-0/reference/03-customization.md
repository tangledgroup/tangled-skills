# Oat UI - Customization and Theming

Complete guide to customizing Oat's appearance through CSS variables and theme overrides.

## CSS Variable Architecture

All visual properties in Oat are defined as CSS variables, making customization straightforward. Variables are organized hierarchically:

### Variable Categories

1. **Colors**: Primary, secondary, semantic colors (success, warning, danger)
2. **Spacing**: Consistent spacing scale
3. **Typography**: Font sizes, weights, line heights
4. **Borders**: Border radii, widths, colors
5. **Shadows**: Box shadow presets
6. **Transitions**: Animation timing functions

### Override Pattern

To customize, redefine variables in your own CSS file included **after** Oat's CSS:

```html
<link rel="stylesheet" href="oat.min.css">
<link rel="stylesheet" href="custom.css"> <!-- Your overrides here -->
```

## Color Theme Variables

### Primary Colors

```css
:root {
  /* Page background */
  --background: rgb(255 255 255);
  
  /* Primary text color */
  --foreground: rgb(9 9 11);
  
  /* Card and surface backgrounds */
  --card: rgb(255 255 255);
  --card-foreground: rgb(9 9 11);
  
  /* Primary buttons and links (brand color) */
  --primary: rgb(24 24 27);
  --primary-foreground: rgb(250 250 250);
  
  /* Secondary buttons */
  --secondary: rgb(244 244 245);
  --secondary-foreground: rgb(24 24 27);
}
```

### Semantic Colors

```css
:root {
  /* Error/Danger */
  --danger: rgb(223 81 76);
  --danger-foreground: rgb(250 250 250);
  
  /* Success */
  --success: rgb(76 175 80);
  --success-foreground: rgb(250 250 250);
  
  /* Warning */
  --warning: rgb(255 140 0);
  --warning-foreground: rgb(9 9 11);
}
```

### Muted and Accent Colors

```css
:root {
  /* Muted (lighter) background */
  --muted: rgb(244 244 245);
  --muted-foreground: rgb(113 113 122);
  
  /* Subtler than muted */
  --faint: rgb(250 250 250);
  --faint-foreground: rgb(161 161 170);
  
  /* Accent background */
  --accent: rgb(244 244 245);
  --accent-foreground: rgb(24 24 27);
}
```

### UI Element Colors

```css
:root {
  /* Border color (boxes, dividers) */
  --border: rgb(212 212 216);
  
  /* Input field borders */
  --input: rgb(212 212 216);
  
  /* Focus ring color */
  --ring: rgb(24 24 27);
}
```

## Creating Custom Themes

### Example: Blue Theme

```css
:root {
  --background: rgb(255 255 255);
  --foreground: rgb(15 23 42);
  
  --primary: rgb(59 130 246);        /* Blue-500 */
  --primary-foreground: rgb(255 255 255);
  
  --secondary: rgb(239 246 255);     /* Blue-50 */
  --secondary-foreground: rgb(30 64 175);  /* Blue-800 */
  
  --muted: rgb(239 246 255);
  --muted-foreground: rgb(100 116 139);
  
  --accent: rgb(239 246 255);
  --accent-foreground: rgb(30 64 175);
  
  --border: rgb(226 232 240);
  --input: rgb(226 232 240);
  --ring: rgb(59 130 246);
}
```

### Example: Green Theme

```css
:root {
  --background: rgb(255 255 255);
  --foreground: rgb(6 46 20);
  
  --primary: rgb(22 163 74);         /* Green-600 */
  --primary-foreground: rgb(255 255 255);
  
  --secondary: rgb(240 253 244);     /* Green-50 */
  --secondary-foreground: rgb(6 78 59);    /* Green-900 */
  
  --border: rgb(227 231 236);
  --ring: rgb(22 163 74);
}
```

### Example: Purple Theme

```css
:root {
  --background: rgb(255 255 255);
  --foreground: rgb(28 25 23);
  
  --primary: rgb(147 51 234);        /* Purple-600 */
  --primary-foreground: rgb(255 255 255);
  
  --secondary: rgb(243 232 255);     /* Purple-100 */
  --secondary-foreground: rgb(88 28 135);   /* Purple-900 */
  
  --border: rgb(229 231 235);
  --ring: rgb(147 51 234);
}
```

### Example: Orange Theme

```css
:root {
  --background: rgb(255 255 255);
  --foreground: rgb(49 29 10);
  
  --primary: rgb(255 102 0);         /* Orange-600 */
  --primary-foreground: rgb(255 255 255);
  
  --secondary: rgb(255 247 237);     /* Orange-50 */
  --secondary-foreground: rgb(194 62 0);    /* Orange-900 */
  
  --border: rgb(250 243 233);
  --ring: rgb(255 102 0);
}
```

## Dark Mode Customization

### Automatic Dark Mode

Oat automatically detects system dark mode via `prefers-color-scheme`. No configuration needed.

### Force Dark Mode

```html
<body data-theme="dark">
  <!-- Content always in dark mode -->
</body>
```

### Custom Dark Theme

Override variables scoped to `[data-theme="dark"]`:

```css
[data-theme="dark"] {
  --background: rgb(9 9 11);
  --foreground: rgb(244 244 245);
  
  --card: rgb(9 9 11);
  --card-foreground: rgb(244 244 245);
  
  --primary: rgb(244 244 245);
  --primary-foreground: rgb(9 9 11);
  
  --secondary: rgb(39 39 42);
  --secondary-foreground: rgb(244 244 245);
  
  --muted: rgb(39 39 42);
  --muted-foreground: rgb(161 161 170);
  
  --accent: rgb(39 39 42);
  --accent-foreground: rgb(244 244 245);
  
  --border: rgb(63 63 70);
  --input: rgb(63 63 70);
  --ring: rgb(244 244 245);
}
```

### Dark Theme Example (Blue)

```css
[data-theme="dark"] {
  --background: rgb(15 23 42);
  --foreground: rgb(241 245 249);
  
  --primary: rgb(96 165 250);        /* Blue-400 */
  --primary-foreground: rgb(15 23 42);
  
  --secondary: rgb(30 41 59);
  --secondary-foreground: rgb(241 245 249);
  
  --border: rgb(51 65 85);
  --ring: rgb(96 165 250);
}
```

## Spacing Variables

Oat uses a consistent spacing scale based on 4px base unit:

```css
:root {
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
}
```

Customize spacing scale:

```css
:root {
  /* Tighter spacing */
  --space-1: 0.125rem;  /* 2px */
  --space-2: 0.25rem;   /* 4px */
  --space-4: 0.75rem;   /* 12px */
}
```

## Typography Variables

### Font Family

```css
:root {
  /* System font stack (default) */
  --font-sans: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  
  /* Custom font */
  --font-sans: 'Inter', system-ui, sans-serif;
}
```

### Font Sizes

```css
:root {
  --text-1: 0.75rem;    /* 12px - xs */
  --text-2: 0.875rem;   /* 14px - sm */
  --text-3: 1rem;       /* 16px - base */
  --text-4: 1.125rem;   /* 18px - lg */
  --text-5: 1.25rem;    /* 20px - xl */
  --text-6: 1.5rem;     /* 24px - 2xl */
  --text-7: 1.875rem;   /* 30px - 3xl */
  --text-8: 2.25rem;    /* 36px - 4xl */
  --text-9: 2.625rem;   /* 42px - 5xl */
}
```

### Line Heights

```css
:root {
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
}
```

## Border and Radius Variables

```css
:root {
  /* Border radius */
  --radius-sm: 0.25rem;   /* 4px */
  --radius-md: 0.375rem;  /* 6px */
  --radius-lg: 0.5rem;    /* 8px */
  --radius-full: 9999px;  /* Full circle */
  
  /* Border width */
  --border-width: 1px;
}
```

Custom border radius:

```css
:root {
  /* More rounded */
  --radius-sm: 0.5rem;
  --radius-md: 0.75rem;
  --radius-lg: 1rem;
}

/* Or sharper */
:root {
  --radius-sm: 0;
  --radius-md: 0.125rem;
  --radius-lg: 0.25rem;
}
```

## Shadow Variables

```css
:root {
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}
```

## Transition Variables

```css
:root {
  --transition-fast: 150ms;
  --transition-normal: 200ms;
  --transition-slow: 300ms;
  
  --easing: cubic-bezier(0.4, 0, 0.2, 1);
}
```

## Component-Specific Customization

### Button Customization

```css
/* Override button styles */
button {
  --btn-padding: var(--space-3) var(--space-5);
  --btn-radius: var(--radius-lg);
  --btn-font-weight: 600;
}

/* Primary button specific */
button:not([data-variant]) {
  background-color: var(--primary);
  padding: var(--space-4);
  border-radius: var(--radius-full);
}
```

### Input Customization

```css
/* Make inputs larger */
input, textarea, select {
  --input-height: 2rem;
  --input-padding: var(--space-3);
  --input-radius: var(--radius-md);
}

/* Remove input border */
input, textarea, select {
  border: none;
  background-color: var(--muted);
}
```

### Card Customization

```css
article.card {
  --card-padding: var(--space-6);
  --card-radius: var(--radius-lg);
  --card-shadow: var(--shadow-md);
  
  padding: var(--card-padding);
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
}
```

## Utility Classes for Overrides

Oat provides utility classes for common overrides without custom CSS:

### Text Utilities

```html
<p class="text-light">Lighter text (muted-foreground)</p>
<p class="text-center">Centered text</p>
<p class="text-right">Right-aligned text</p>
```

### Spacing Utilities

```html
<div class="mt-4">Margin top: 16px</div>
<div class="mb-8">Margin bottom: 32px</div>
<div class="px-4">Padding horizontal: 16px</div>
<div class="py-2">Padding vertical: 8px</div>
```

### Flexbox Utilities

```html
<div class="hstack">Horizontal flex container</div>
<div class="vstack">Vertical flex container</div>
<div class="hstack justify-between">Space between items</div>
<div class="hstack items-center">Vertically centered</div>
```

### Width/Height Utilities

```html
<div class="w-full">Width: 100%</div>
<div class="h-screen">Height: 100vh</div>
<div class="min-w-0">Min-width: 0</div>
```

## Complete Custom Theme Example

Here's a complete custom theme file:

```css
/* custom-theme.css */
:root {
  /* Brand colors */
  --primary: rgb(79 70 229);        /* Indigo-600 */
  --primary-foreground: rgb(255 255 255);
  
  /* Semantic colors */
  --success: rgb(34 197 94);        /* Green-500 */
  --warning: rgb(251 191 36);       /* Yellow-500 */
  --danger: rgb(239 68 68);         /* Red-500 */
  
  /* Spacing scale (larger) */
  --space-4: 1.25rem;
  --space-6: 2rem;
  --space-8: 3rem;
  
  /* Rounded corners */
  --radius-md: 0.75rem;
  --radius-lg: 1rem;
  
  /* Typography */
  --font-sans: 'Inter', system-ui, sans-serif;
}

/* Dark mode overrides */
[data-theme="dark"] {
  --background: rgb(17 24 39);      /* Gray-900 */
  --foreground: rgb(243 244 246);   /* Gray-100 */
  
  --primary: rgb(129 140 248);      /* Indigo-400 */
  --primary-foreground: rgb(17 24 39);
  
  --card: rgb(31 41 55);            /* Gray-800 */
  --card-foreground: rgb(243 244 246);
}

/* Component-specific overrides */
button {
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

article.card {
  border: 1px solid var(--border);
}
```

Include after Oat's CSS:

```html
<link rel="stylesheet" href="oat.min.css">
<link rel="stylesheet" href="custom-theme.css">
```

## Best Practices

### DO

- Use CSS variables for all customizations
- Scope dark mode overrides to `[data-theme="dark"]`
- Include custom CSS after Oat's CSS
- Test both light and dark modes
- Use utility classes when possible instead of custom CSS

### DON'T

- Use `!important` (CSS variables should override cleanly)
- Modify Oat's source files directly
- Override semantic colors with conflicting values
- Forget to test dark mode after changes

## Debugging Customization Issues

### Variables Not Applying

```javascript
// Check computed styles in browser console
const btn = document.querySelector('button');
const styles = getComputedStyle(btn);
console.log(styles.getPropertyValue('--primary'));
```

### Specificity Issues

If overrides not working, check CSS specificity:

```css
/* Low specificity - might not override */
button {
  background-color: red;
}

/* Higher specificity */
body button {
  background-color: red;
}

/* Use variables instead (recommended) */
:root {
  --primary: red;
}
```
