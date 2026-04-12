# Theming & Customization

This reference covers how to customize Tailwind CSS v4 themes, create design systems, and extend the framework with custom properties.

## Theme Configuration

### Basic @theme Usage

All customization happens in CSS using the `@theme` directive:

```css
/* src/theme.css */
@theme {
  /* Your custom theme values */
  --color-primary: oklch(0.6 0.2 250);
  --font-heading: 'Inter', sans-serif;
}

/* Then import it */
@import 'tailwindcss';
@import './theme.css';
```

### Complete Theme Example

```css
@theme {
  /* Colors */
  --color-brand-50: oklch(0.97 0.01 250);
  --color-brand-100: oklch(0.94 0.02 250);
  --color-brand-200: oklch(0.89 0.04 250);
  --color-brand-300: oklch(0.81 0.08 250);
  --color-brand-400: oklch(0.72 0.14 250);
  --color-brand-500: oklch(0.62 0.20 250);
  --color-brand-600: oklch(0.52 0.22 250);
  --color-brand-700: oklch(0.42 0.20 250);
  --color-brand-800: oklch(0.32 0.16 250);
  --color-brand-900: oklch(0.22 0.12 250);
  --color-brand-950: oklch(0.12 0.08 250);
  
  /* Success, warning, error colors */
  --color-success: oklch(0.72 0.15 150);
  --color-warning: oklch(0.82 0.18 90);
  --color-error: oklch(0.62 0.20 25);
  
  /* Typography */
  --font-sans: 'Inter', ui-sans-serif, system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;
  
  /* Spacing extensions */
  --spacing-3xl: 48rem;
  --spacing-4xl: 56rem;
  --spacing-5xl: 64rem;
  
  /* Breakpoints */
  --breakpoint-3xl: 1200px;
  --breakpoint-4xl: 1400px;
  
  /* Border radius */
  --radius-xl: 1rem;
  --radius-2xl: 1.5rem;
  --radius-3xl: 2rem;
  
  /* Shadows */
  --shadow-lg: 
    0 10px 15px -3px rgb(0 0 0 / 0.1),
    0 4px 6px -4px rgb(0 0 0 / 0.1);
  
  /* Z-index scale */
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-modal: 300;
  --z-popover: 400;
  --z-tooltip: 500;
}
```

## Using Custom Theme Values

### Generated Utilities

Theme values automatically generate utility classes:

```css
@theme {
  --color-brand: oklch(0.6 0.2 250);
  --spacing-3xl: 48rem;
  --radius-3xl: 2rem;
}
```

Generates these utilities:
```html
<!-- Color -->
<div class="bg-brand text-brand border-brand"></div>

<!-- Spacing -->
<div class="p-3xl m-3xl gap-3xl"></div>

<!-- Border radius -->
<div class="rounded-3xl"></div>
```

### Reference Variables (No Utilities)

Use `@theme reference` for internal-only variables:

```css
@theme reference {
  --animation-speed: 300ms;
  --header-height: 4rem;
}

/* Use in component styles */
@layer components {
  .header {
    height: var(--header-height);
    transition: all var(--animation-speed) ease;
  }
}
```

## Color Customization

### OKLCH Color System

Tailwind v4 uses OKLCH for perceptually uniform colors:

```css
@theme {
  /* Format: oklch(Lightness Chroma Hue) */
  
  /* Lightness: 0 (black) to 1 (white) */
  --color-dark: oklch(0.2 0 0);
  --color-light: oklch(0.9 0 0);
  
  /* Chroma: 0 (gray) to ~0.4 (vibrant) */
  --color-muted: oklch(0.6 0.05 250);
  --color-vibrant: oklch(0.6 0.3 250);
  
  /* Hue: 0-360 degrees */
  --color-red: oklch(0.6 0.2 25);
  --color-blue: oklch(0.6 0.2 250);
  --color-green: oklch(0.7 0.15 150);
}
```

### Creating Color Palettes

Generate a full color scale by varying lightness:

```css
@theme {
  --color-indigo-50: oklch(0.97 0.01 260);
  --color-indigo-100: oklch(0.94 0.02 260);
  --color-indigo-200: oklch(0.89 0.04 260);
  --color-indigo-300: oklch(0.81 0.07 260);
  --color-indigo-400: oklch(0.71 0.11 260);
  --color-indigo-500: oklch(0.59 0.15 260);
  --color-indigo-600: oklch(0.48 0.17 260);
  --color-indigo-700: oklch(0.38 0.16 260);
  --color-indigo-800: oklch(0.29 0.14 260);
  --color-indigo-900: oklch(0.21 0.11 260);
  --color-indigo-950: oklch(0.12 0.07 260);
}
```

### Color Opacity Modifiers

Use opacity modifiers with any color:

```html
<div class="bg-blue-500/50">50% opacity</div>
<div class="text-red-600/75 hover:text-red-600/100">Hover effect</div>
```

## Typography Customization

### Font Families

```css
@theme {
  --font-sans: 'Inter', ui-sans-serif, system-ui, sans-serif;
  --font-serif: 'Merriweather', ui-serif, Georgia, serif;
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;
  --font-display: 'Poppins', var(--font-sans);
}
```

Usage:
```html
<p class="font-sans">Sans-serif text</p>
<p class="font-serif">Serif text</p>
<p class="font-mono">Monospace text</p>
<p class="font-display">Display font</p>
```

### Font Sizes with Line Heights

```css
@theme {
  --text-xs: 0.75rem;
  --text-xs--line-height: calc(1 / 0.75);
  
  --text-sm: 0.875rem;
  --text-sm--line-height: calc(1.25 / 0.875);
  
  --text-base: 1rem;
  --text-base--line-height: calc(1.5 / 1);
  
  --text-lg: 1.125rem;
  --text-lg--line-height: calc(1.75 / 1.125);
  
  --text-xl: 1.25rem;
  --text-xl--line-height: calc(1.75 / 1.25);
  
  --text-2xl: 1.5rem;
  --text-2xl--line-height: calc(2 / 1.5);
  
  --text-3xl: 1.875rem;
  --text-3xl--line-height: calc(2.25 / 1.875);
  
  --text-4xl: 2.25rem;
  --text-4xl--line-height: calc(2.5 / 2.25);
}
```

### Font Weights

```css
@theme {
  --font-weight-thin: 100;
  --font-weight-extralight: 200;
  --font-weight-light: 300;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  --font-weight-extrabold: 800;
  --font-weight-black: 900;
}
```

Usage:
```html
<p class="font-thin">Thin (100)</p>
<p class="font-bold">Bold (700)</p>
<p class="font-black">Black (900)</p>
```

## Spacing System

### Custom Spacing Scale

```css
@theme {
  /* Base unit */
  --spacing: 0.25rem;
  
  /* Extended scale */
  --spacing-px: 1px;
  --spacing-3xl: 48rem;
  --spacing-4xl: 56rem;
  --spacing-5xl: 64rem;
  --spacing-full: 100%;
  
  /* Fractional spacing */
  --spacing-1-2: 50%;
  --spacing-1-3: 33.333333%;
  --spacing-2-3: 66.666667%;
  --spacing-1-4: 25%;
  --spacing-2-4: 50%;
  --spacing-3-4: 75%;
}
```

Usage:
```html
<div class="p-3xl m-4xl">Large spacing</div>
<div class="w-1-2 h-2-3">Fractional sizing</div>
```

## Breakpoint Customization

### Default Breakpoints

```css
@theme {
  --breakpoint-sm: 40rem;   /* 640px */
  --breakpoint-md: 48rem;   /* 768px */
  --breakpoint-lg: 64rem;   /* 1024px */
  --breakpoint-xl: 80rem;   /* 1280px */
  --breakpoint-2xl: 96rem;  /* 1536px */
}
```

### Adding Custom Breakpoints

```css
@theme {
  --breakpoint-3xl: 1200px;
  --breakpoint-4xl: 1400px;
  --breakpoint-mobile: 320px;
  --breakpoint-tablet: 768px;
}
```

Usage:
```html
<div class="w-full md:w-1/2 lg:w-1/3 xl:w-1/4 3xl:w-1/5">
  Responsive width
</div>

<div class="mobile:hidden tablet:block">
  Tablet only
</div>
```

## Component Styles

### @layer components

Define reusable component styles:

```css
@layer components {
  /* Button variants */
  .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.5rem 1rem;
    font-weight: 500;
    border-radius: var(--radius-md);
    transition: all 0.15s ease;
  }
  
  .btn-primary {
    background-color: var(--color-brand-500);
    color: white;
  }
  
  .btn-primary:hover {
    background-color: var(--color-brand-600);
  }
  
  .btn-secondary {
    background-color: transparent;
    border: 2px solid var(--color-brand-500);
    color: var(--color-brand-500);
  }
  
  /* Card component */
  .card {
    background-color: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    overflow: hidden;
  }
  
  .card-header {
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--color-gray-200);
  }
  
  .card-body {
    padding: 1.5rem;
  }
  
  .card-footer {
    padding: 1rem 1.5rem;
    background-color: var(--color-gray-50);
  }
}
```

Usage:
```html
<button class="btn btn-primary">Primary Button</button>
<button class="btn btn-secondary">Secondary Button</button>

<div class="card">
  <div class="card-header">Card Title</div>
  <div class="card-body">Card content</div>
  <div class="card-footer">Footer</div>
</div>
```

## Dark Mode Theming

### Media Query Based (System Preference)

```css
@theme {
  /* Light mode (default) */
  --bg-primary: oklch(1 0 0);
  --text-primary: oklch(0.15 0 0);
}

@media (prefers-color-scheme: dark) {
  @theme {
    --bg-primary: oklch(0.15 0 0);
    --text-primary: oklch(0.9 0 0);
  }
}
```

### Class-Based Dark Mode

Add `class="dark"` to html element, then use utilities:

```html
<html class="dark">
<div class="bg-white dark:bg-gray-900 text-black dark:text-white">
  Dark mode aware
</div>
</html>
```

## Custom Utilities

### Adding New Utilities with @utility

```css
@utility text-stroke {
  --tw-text-stroke: 1px var(--color-current);
  -webkit-text-stroke: var(--tw-text-stroke);
  text-stroke: var(--tw-text-stroke);
}

@utility text-shadow-lg {
  text-shadow: 
    0 2px 4px rgb(0 0 0 / 0.3),
    0 4px 8px rgb(0 0 0 / 0.2);
}
```

Usage:
```html
<h1 class="text-stroke text-stroke-2 text-white">Outlined Text</h1>
<p class="text-shadow-lg">Large shadow</p>
```

## Animation Customization

### Keyframes

```css
@theme {
  --animate-shake: shake 0.82s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
  --animate-slide-in: slide-in 0.3s ease-out;
  --animate-fade-in: fade-in 0.2s ease-out;
}

@keyframes shake {
  10%, 90% { transform: translate3d(-1px, 0, 0); }
  20%, 80% { transform: translate3d(2px, 0, 0); }
  30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
  40%, 60% { transform: translate3d(4px, 0, 0); }
}

@keyframes slide-in {
  from { transform: translateY(-100%); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

Usage:
```html
<div class="animate-shake">Shake animation</div>
<div class="animate-slide-in">Slide in</div>
<div class="animate-fade-in">Fade in</div>
```

## Best Practices

### 1. Keep Theme Organized

```css
/* src/theme.css - organized sections */
@theme {
  /* Colors */
  --color-brand: oklch(...);
  
  /* Typography */
  --font-sans: ...;
  --text-base: ...;
  
  /* Spacing */
  --spacing-xl: ...;
  
  /* Breakpoints */
  --breakpoint-3xl: ...;
  
  /* Shadows */
  --shadow-lg: ...;
  
  /* Borders */
  --radius-lg: ...;
  
  /* Animation */
  --animate-custom: ...;
}
```

### 2. Use Semantic Names

```css
@theme {
  /* Good: semantic */
  --color-interactive-primary: oklch(...);
  --color-feedback-success: oklch(...);
  --color-feedback-error: oklch(...);
  
  /* Avoid: implementation-specific */
  --color-button-blue: oklch(...);
  --color-alert-green: oklch(...);
}
```

### 3. Leverage Reference Theme

```css
/* Internal variables don't generate utilities */
@theme reference {
  --header-height: 4rem;
  --sidebar-width: 16rem;
  --animation-duration: 200ms;
}
```

### 4. Document Custom Values

```css
@theme {
  /* 
   * Brand colors - derived from brand guidelines v2.1
   * Primary: oklch(0.6 0.2 250) - main brand blue
   */
  --color-brand: oklch(0.6 0.2 250);
  
  /* 
   * Custom breakpoints for dashboard layouts
   * 3xl: 1200px - full dashboard with sidebar
   */
  --breakpoint-3xl: 1200px;
}
```
