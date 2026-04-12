# Customization with CSS Variables and SASS

Pico includes over 130 CSS variables for easy customization of the design system. All variables are prefixed with `pico-` to avoid collisions.

## CSS Variables Overview

Variables are categorized into:
1. **Style variables** - Independent of color scheme (fonts, spacing, borders)
2. **Color variables** - Dependent on color scheme (primary, background, text colors)

### Defining Variables

Define within `:root` for global changes:

```css
:root {
  --pico-border-radius: 2rem;
  --pico-typography-spacing-vertical: 1.5rem;
}
```

Or on specific selectors for local changes:

```css
h1 {
  --pico-font-family: "Pacifico", cursive;
  --pico-font-weight: 400;
}

button {
  --pico-font-weight: 700;
}
```

## Style Variables (Color-Scheme Independent)

### Typography

```css
:root {
  --pico-font-family-emoji: "Apple Color Emoji", "Segoe UI Emoji";
  --pico-font-family-sans-serif: system-ui, -apple-system, sans-serif;
  --pico-font-family-monospace: ui-monospace, SFMono-Regular, monospace;
  --pico-font-family: var(--pico-font-family-sans-serif);
  --pico-line-height: 1.5;
  --pico-font-weight: 400;
  --pico-font-size: 100%;
  --pico-text-underline-offset: 0.1rem;
}
```

### Spacing

```css
:root {
  --pico-spacing: 1rem;
  --pico-typography-spacing-vertical: 1rem;
  --pico-block-spacing-vertical: var(--pico-spacing);
  --pico-block-spacing-horizontal: var(--pico-spacing);
  --pico-grid-column-gap: var(--pico-spacing);
  --pico-grid-row-gap: var(--pico-spacing);
}
```

### Borders and Radius

```css
:root {
  --pico-border-radius: 0.25rem;
  --pico-border-width: 0.0625rem;
  --pico-outline-width: 0.125rem;
  --pico-transition: 0.2s ease-in-out;
}
```

## Color Variables (Color-Scheme Dependent)

### Primary Color

```css
/* Light mode */
[data-theme="light"],
:root:not([data-theme="dark"]) {
  --pico-text-selection-color: rgba(1, 114, 173, 0.25);
  --pico-primary: #0172ad;
  --pico-primary-background: #026091;
  --pico-primary-underline: rgba(1, 114, 173, 0.5);
  --pico-primary-hover: #026091;
  --pico-primary-hover-background: #0172ad;
  --pico-primary-focus: rgba(1, 114, 173, 0.5);
  --pico-primary-inverse: #fff;
}

/* Dark mode (auto) */
@media only screen and (prefers-color-scheme: dark) {
  :root:not([data-theme]) {
    --pico-text-selection-color: rgba(1, 187, 249, 0.1875);
    --pico-primary: #01b9f9;
    --pico-primary-background: #026091;
    --pico-primary-underline: rgba(1, 187, 249, 0.5);
    --pico-primary-hover: #6eeaff;
    --pico-primary-hover-background: #01c7ff;
    --pico-primary-focus: rgba(1, 187, 249, 0.375);
    --pico-primary-inverse: #fff;
  }
}

/* Dark mode (forced) */
[data-theme="dark"] {
  /* Same variables as auto dark mode */
}
```

### Secondary and Neutral Colors

```css
--pico-secondary: #5c677f;
--pico-secondary-background: #4f586a;
--pico-secondary-hover: #4f586a;
--pico-secondary-hover-background: #5c677f;
--pico-secondary-inverse: #fff;

--pico-muted: #7a829e;
--pico-muted-background: #6c738d;
--pico-muted-hover: #6c738d;
--pico-muted-hover-background: #7a829e;
--pico-muted-inverse: #fff;

--pico-contrast: #21252f;
--pico-contrast-background: #1a1d24;
--pico-contrast-hover: #1a1d24;
--pico-contrast-hover-background: #21252f;
--pico-contrast-inverse: #fff;
```

### Web Colors

Pico supports all 140 web color keywords as CSS variables:

```css
--pico-color-blue: #0172ad;
--pico-color-green: #01a65d;
--pico-color-orange: #f96d01;
--pico-color-red: #ae162d;
/* ... and 136 more */
```

## SASS Customization

For advanced customization, use SASS to recompile Pico with your settings.

### Installation

```bash
npm install @picocss/pico sass
```

### Basic Usage

```scss
@use "pico" with (
  $primary: #bd3c13,
  $border-radius: 2rem,
);
```

### Available SASS Variables

```scss
@use "pico" with (
  // Colors
  $primary: #0172ad;
  $secondary: #5c677f;
  $muted: #7a829e;
  $contrast: #21252f;
  
  // Typography
  $font-family: system-ui, -apple-system, sans-serif;
  $font-size: 100%;
  $line-height: 1.5;
  
  // Spacing
  $spacing: 1rem;
  $typography-spacing-vertical: 1rem;
  
  // Borders
  $border-radius: 0.25rem;
  $border-width: 0.0625rem;
  
  // Prefix (change from "pico-" to avoid conflicts)
  $prefix: "pico-";
);
```

### Custom Prefix

Change the CSS variable prefix to avoid conflicts with other frameworks:

```scss
@use "pico" with (
  $prefix: "my-";
);

// Results in --my-primary, --my-spacing, etc.
```

## Example: Complete Custom Theme

```css
<style>
  :root {
    /* Rounded corners everywhere */
    --pico-border-radius: 2rem;
    
    /* More spacing between elements */
    --pico-typography-spacing-vertical: 1.5rem;
    --pico-form-element-spacing-vertical: 1rem;
    --pico-form-element-spacing-horizontal: 1.25rem;
  }
  
  h1 {
    /* Custom font for headings */
    --pico-font-family: "Pacifico", cursive;
    --pico-font-weight: 400;
    --pico-typography-spacing-vertical: 0.5rem;
  }
  
  button {
    /* Bold buttons */
    --pico-font-weight: 700;
  }
  
  /* Custom primary color for light mode */
  [data-theme="light"],
  :root:not([data-theme="dark"]) {
    --pico-text-selection-color: rgba(244, 93, 44, 0.25);
    --pico-primary: #bd3c13;
    --pico-primary-background: #d24317;
    --pico-primary-underline: rgba(189, 60, 19, 0.5);
    --pico-primary-hover: #942d0d;
    --pico-primary-hover-background: #bd3c13;
    --pico-primary-focus: rgba(244, 93, 44, 0.5);
    --pico-primary-inverse: #fff;
  }
  
  /* Custom primary color for dark mode */
  @media only screen and (prefers-color-scheme: dark) {
    :root:not([data-theme]) {
      --pico-text-selection-color: rgba(245, 107, 61, 0.1875);
      --pico-primary: #f56b3d;
      --pico-primary-background: #d24317;
      --pico-primary-underline: rgba(245, 107, 61, 0.5);
      --pico-primary-hover: #f8a283;
      --pico-primary-hover-background: #e74b1a;
      --pico-primary-focus: rgba(245, 107, 61, 0.375);
      --pico-primary-inverse: #fff;
    }
  }
  
  [data-theme="dark"] {
    --pico-text-selection-color: rgba(245, 107, 61, 0.1875);
    --pico-primary: #f56b3d;
    --pico-primary-background: #d24317;
    --pico-primary-underline: rgba(245, 107, 61, 0.5);
    --pico-primary-hover: #f8a283;
    --pico-primary-hover-background: #e74b1a;
    --pico-primary-focus: rgba(245, 107, 61, 0.375);
    --pico-primary-inverse: #fff;
  }
</style>

<h1>Music fest mania</h1>
<p>Get ready to dance and sing your heart out!</p>
<button>Let's rock out!</button>
```

## CDN Themes

Use precompiled themes from jsDelivr:

```html
<!-- Pico Blue theme -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/themes/pico-blue.min.css">

<!-- Pico Green theme -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/themes/pico-green.min.css">

<!-- Pico Orange theme -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/themes/pico-orange.min.css">
```

Available themes: pico, pico-blue, pico-green, pico-orange, pico-red, pico-purple, pico-pink, pico-yellow, pico-teal, and more (20 total with light/dark variations).
