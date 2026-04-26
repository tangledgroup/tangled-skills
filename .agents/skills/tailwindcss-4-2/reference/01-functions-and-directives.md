# Functions and Directives

Tailwind CSS 4.x exposes custom at-rules and functions that extend CSS syntax for framework-specific functionality.

## @import

Inline import CSS files, including Tailwind itself:

```css
@import "tailwindcss";
```

This is the single entry point. It automatically injects Preflight (base reset styles), theme definitions, and all utility classes. You do not need separate `@tailwind base`, `@tailwind components`, or `@tailwind utilities` directives anymore.

## @theme

Define custom design tokens that generate corresponding utility classes:

```css
@import "tailwindcss";

@theme {
  --font-display: "Satoshi", sans-serif;
  --color-brand-500: oklch(0.65 0.2 250);
  --breakpoint-3xl: 120rem;
  --shadow-card: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}
```

### Theme Variable Namespaces

Theme variables follow naming conventions that map to utility classes:

- `--font-*` → `font-*` utilities (font-family)
- `--color-*` → `bg-*`, `text-*`, `border-*`, `fill-*`, `stroke-*`, etc.
- `--breakpoint-*` → responsive variant prefixes
- `--spacing-*` → spacing utilities (`p-*`, `m-*`, `w-*`, `h-*`)
- `--shadow-*` → `shadow-*` utilities
- `--radius-*` → `rounded-*` utilities
- `--blur-*` → `blur-*` utilities
- `--drop-shadow-*` → `drop-shadow-*` utilities
- `--ease-*` → `ease-*` utilities
- `--animate-*` → `animate-*` utilities

### Why @theme Instead of :root?

Theme variables are not just CSS variables — they instruct Tailwind to generate new utility classes. They must be defined top-level (not nested under selectors or media queries). Use `:root` for regular CSS variables that should not map to utilities.

```css
/* Generates font-poppins utility */
@theme {
  --font-poppins: Poppins, sans-serif;
}

/* Regular CSS variable — no utility generated */
:root {
  --my-custom-var: 12px;
}
```

## @layer

Organize CSS into cascade layers for predictable specificity. Tailwind uses four layers internally:

```css
@layer theme, base, components, utilities;

@import "tailwindcss/theme.css" layer(theme);
@import "tailwindcss/preflight.css" layer(base);
@import "tailwindcss/utilities.css" layer(utilities);
```

Use `@layer` for your own custom styles:

```css
@layer components {
  .btn {
    @apply px-4 py-2 rounded-lg font-medium;
  }

  .card {
    @apply bg-white rounded-xl shadow-md p-6;
  }
}
```

Layer order: `theme` → `base` → `components` → `utilities`. Later layers override earlier ones at equal specificity.

## @utility

Register custom utility classes that work with all variants:

```css
@utility tab-4 {
  tab-size: 4;
}

@utility scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
```

Then use them with variants in HTML:

```html
<pre class="tab-4 hover:scrollbar-hide">...</pre>
```

## @variant

Apply a Tailwind variant to custom CSS styles:

```css
.my-element {
  background: white;
  color: black;

  @variant dark {
    background: black;
    color: white;
  }

  @variant hover {
    opacity: 0.8;
  }
}
```

## @custom-variant

Define custom variants for use with any utility class:

```css
@custom-variant theme-midnight (&:where([data-theme="midnight"] *));
@custom-variant sidebar (&:is(.sidebar, .sidebar *));
```

Then use them as prefixes:

```html
<div class="theme-midnight:bg-black theme-midnight:text-white">...</div>
<div class="sidebar:w-64">...</div>
```

## @apply

Inline existing utility classes into custom CSS:

```css
.select2-dropdown {
  @apply rounded-b-lg shadow-md;
}

.select2-search {
  @apply rounded border border-gray-300;
}

.select2-results__group {
  @apply text-lg font-bold text-gray-900;
}
```

Use `@apply` when extracting repeated utility combinations into reusable classes, or when integrating with third-party components that require class-based styling.

## @source

Explicitly specify source files for class detection when automatic detection misses them:

```css
@import "tailwindcss";

@source "../node_modules/@my-company/ui-lib";
@source "./templates/**/*.email.hbs";
```

Tailwind automatically detects classes in your project's source files. Use `@source` to include additional paths outside the default detection scope.

## --alpha() Function

Adjust the opacity of a color when referencing it as a CSS variable:

```css
@import "tailwindcss";

@layer components {
  .search-result {
    background-color: --alpha(var(--color-gray-950) / 10%);
  }
}
```

## light-dark() Function

Tailwind supports the CSS `light-dark()` function for automatic light/dark mode switching:

```html
<div class="bg-[light-dark(var(--color-white),var(--color-gray-950))]">
  <!-- auto-switches between white and gray-950 -->
</div>
```

## OKLCH Color Space

Tailwind 4.x uses OKLCH as the default color space for its palette. Colors are defined with perceptually uniform lightness, chroma, and hue values:

```css
@theme {
  --color-mint-500: oklch(0.72 0.11 178);
  --color-brand-500: oklch(0.65 0.2 250);
}
```

OKLCH provides better color mixing with `color-mix()` and more perceptually uniform steps. You can still use hex, rgb, and hsl values.

## Preflight

Built on top of modern-normalize, Preflight is an opinionated set of base styles automatically injected when you import Tailwind. It:

- Removes default margins from all elements
- Sets `box-sizing: border-box` globally
- Normalizes form element styling
- Applies consistent text rendering across browsers

Preflight runs in the `base` cascade layer. You can disable it:

```css
@import "tailwindcss" theme utilities;
/* omits preflight */
```

Or import it selectively:

```css
@import "tailwindcss/theme.css" layer(theme);
@import "tailwindcss/utilities.css" layer(utilities);
```
