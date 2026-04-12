# Oat UI - Utilities and Helper Classes

Utility classes for common styling needs without custom CSS.

## Display Utilities

### Visibility

```html
<div class="hidden">Hidden (display: none)</div>
<div class="invisible">Invisible (visibility: hidden)</div>
```

### Display Type

```html
<div class="block">Block element</div>
<div class="inline">Inline element</div>
<div class="inline-block">Inline block</div>
<div class="flex">Flex container</div>
<div class="grid">Grid container</div>
```

## Flexbox Utilities

### Flex Container

```html
<div class="hstack">
  <!-- Horizontal flex (row) -->
</div>

<div class="vstack">
  <!-- Vertical flex (column) -->
</div>
```

### Justify Content

```html
<div class="hstack justify-start">Start (default)</div>
<div class="hstack justify-center">Center</div>
<div class="hstack justify-end">End</div>
<div class="hstack justify-between">Space between</div>
<div class="hstack justify-around">Space around</div>
```

### Align Items

```html
<div class="hstack items-start">Align start</div>
<div class="hstack items-center">Align center</div>
<div class="hstack items-end">Align end</div>
<div class="hstack items-stretch">Stretch (default)</div>
```

### Flex Direction

```html
<div class="flex-row">Horizontal</div>
<div class="flex-column">Vertical</div>
<div class="flex-wrap">Wrap items</div>
```

### Flex Grow/Shrink

```html
<div class="flex-1">Grow to fill space</div>
<div class="flex-auto">Auto flex</div>
<div class="flex-none">No flex</div>
```

## Spacing Utilities

### Margin

Scale: `1` = 4px, `2` = 8px, `3` = 12px, `4` = 16px, `6` = 24px, `8` = 32px, `10` = 40px, `12` = 48px, `16` = 64px

```html
<div class="m-4">Margin all sides: 16px</div>
<div class="mx-4">Margin horizontal: 16px</div>
<div class="my-4">Margin vertical: 16px</div>
<div class="mt-4">Margin top: 16px</div>
<div class="mr-4">Margin right: 16px</div>
<div class="mb-4">Margin bottom: 16px</div>
<div class="ml-4">Margin left: 16px</div>

<div class="m-auto">Auto margin</div>
<div class="mx-auto">Horizontal center</div>
```

### Padding

```html
<div class="p-4">Padding all: 16px</div>
<div class="px-4">Padding horizontal: 16px</div>
<div class="py-4">Padding vertical: 16px</div>
<div class="pt-4">Padding top: 16px</div>
<div class="pr-4">Padding right: 16px</div>
<div class="pb-4">Padding bottom: 16px</div>
<div class="pl-4">Padding left: 16px</div>
```

### Gap (for flex/grid)

```html
<div class="hstack gap-2">Gap: 8px</div>
<div class="vstack gap-4">Gap: 16px</div>
<div class="gap-0">No gap</div>
```

## Size Utilities

### Width

```html
<div class="w-full">Width: 100%</div>
<div class="w-auto">Width: auto</div>
<div class="w-screen">Width: 100vw</div>

<div class="min-w-0">Min-width: 0</div>
<div class="min-w-full">Min-width: 100%</div>

<div class="max-w-full">Max-width: 100%</div>
<div class="max-w-screen">Max-width: screen</div>
```

### Height

```html
<div class="h-full">Height: 100%</div>
<div class="h-auto">Height: auto</div>
<div class="h-screen">Height: 100vh</div>

<div class="min-h-0">Min-height: 0</div>
<div class="min-h-full">Min-height: 100%</div>
<div class="min-h-screen">Min-height: 100vh</div>
```

## Text Utilities

### Text Color

```html
<p class="text-light">Muted text color</p>
```

### Text Alignment

```html
<p class="text-left">Left align (default)</p>
<p class="text-center">Center align</p>
<p class="text-right">Right align</p>
```

### Text Size

```html
<p class="small">Smaller text</p>
<p class="large">Larger text</p>
```

### Font Weight

```html
<span class="font-normal">Normal (400)</span>
<span class="font-medium">Medium (500)</span>
<span class="font-semibold">Semibold (600)</span>
<span class="font-bold">Bold (700)</span>
```

### Text Transform

```html
<p class="uppercase">UPPERCASE</p>
<p class="lowercase">lowercase</p>
<p class="capitalize">Capitalize</p>
```

### Text Decoration

```html
<a class="no-underline">No underline</a>
<p class="line-through">Strikethrough</p>
```

## Alignment Utilities

### Vertical Align

```html
<span class="align-base">Baseline</span>
<span class="align-middle">Middle</span>
<span class="align-top">Top</span>
<span class="align-bottom">Bottom</span>
```

### Text Align (Vertical)

```html
<article class="card align-center">Centered content</article>
<article class="card align-start">Top aligned</article>
<article class="card align-end">Bottom aligned</article>
```

## Position Utilities

```html
<div class="relative">Position: relative</div>
<div class="absolute">Position: absolute</div>
<div class="fixed">Position: fixed</div>
<div class="sticky">Position: sticky</div>
```

### Z-Index

```html
<div class="z-0">z-index: 0</div>
<div class="z-10">z-index: 10</div>
<div class="z-20">z-index: 20</div>
<div class="z-30">z-index: 30</div>
<div class="z-40">z-index: 40</div>
<div class="z-50">z-index: 50</div>
<div class="z-auto">z-index: auto</div>
```

## Border Utilities

### Border Width

```html
<div class="border">Border: 1px</div>
<div class="border-0">No border</div>
<div class="border-t">Top border</div>
<div class="border-r">Right border</div>
<div class="border-b">Bottom border</div>
<div class="border-l">Left border</div>
```

### Border Radius

```html
<div class="rounded">Default radius</div>
<div class="rounded-none">No radius</div>
<div class="rounded-sm">Small radius</div>
<div class="rounded-md">Medium radius</div>
<div class="rounded-lg">Large radius</div>
<div class="rounded-full">Full radius (circle)</div>
```

## Background Utilities

```html
<div class="bg-transparent">Transparent</div>
<div class="bg-current">Current color</div>
```

## Overflow Utilities

```html
<div class="overflow-auto">Scroll when needed</div>
<div class="overflow-hidden">Hide overflow</div>
<div class="overflow-visible">Show overflow</div>
<div class="overflow-scroll">Always scroll</div>

<div class="overflow-x-auto">Horizontal scroll</div>
<div class="overflow-y-auto">Vertical scroll</div>
```

## Cursor Utilities

```html
<div class="cursor-pointer">Pointer cursor</div>
<div class="cursor-default">Default cursor</div>
<div class="cursor-not-allowed">Not allowed</div>
<div class="cursor-wait">Waiting</div>
<div class="cursor-text">Text input</div>
```

## Opacity Utilities

```html
<div class="opacity-0">0% opacity</div>
<div class="opacity-50">50% opacity</div>
<div class="opacity-100">100% opacity</div>
```

## Shadow Utilities

```html
<div class="shadow-none">No shadow</div>
<div class="shadow-sm">Small shadow</div>
<div class="shadow-md">Medium shadow</div>
<div class="shadow-lg">Large shadow</div>
```

## Transition Utilities

```html
<div class="transition">Default transition</div>
<div class="transition-none">No transition</div>
<div class="transition-all">All properties</div>
```

## User Select

```html
<div class="select-none">Cannot select</div>
<div class="select-all">Select all</div>
<div class="select-auto">Auto select</div>
```

## Common Combinations

### Centered Content

```html
<div class="align-center p-8">
  <h3>Centered Title</h3>
  <p class="text-light">Centered paragraph</p>
</div>
```

### Inline Actions

```html
<div class="hstack items-center gap-2">
  <span>Item name</span>
  <span class="badge">Status</span>
  <button class="outline small">Edit</button>
</div>
```

### Card Header with Actions

```html
<header class="hstack justify-between items-start">
  <div>
    <h3>Title</h3>
    <p class="text-light">Subtitle</p>
  </div>
  <button class="outline small">Settings</button>
</header>
```

### Form Row

```html
<div class="hstack gap-3">
  <div class="flex-1">
    <label data-field><input type="text" placeholder="First name" /></label>
  </div>
  <div class="flex-1">
    <label data-field><input type="text" placeholder="Last name" /></label>
  </div>
</div>
```

### Button Group Footer

```html
<footer class="hstack justify-end gap-2 pt-4 border-t">
  <button class="outline">Cancel</button>
  <button>Save</button>
</footer>
```

### Responsive Text

```html
<h1 class="text-center">
  <span class="large">Hello</span>
  <span class="large"> </span>
  <span class="xlarge">World</span>
</h1>
```

## Custom Utility Classes

You can extend utilities in your own CSS:

```css
/* Custom spacing */
.m-20 { margin: var(--space-20); }
.p-20 { padding: var(--space-20); }

/* Custom text sizes */
.text-xsmall { font-size: 0.625rem; }
.text-xlarge { font-size: 1.5rem; }

/* Custom display */
.flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Custom borders */
.border-primary {
  border-color: var(--primary);
}
```

## Best Practices

### DO

- Use utilities for quick layouts and spacing
- Combine with semantic components
- Keep classes readable and organized
- Use for one-off styling needs

### DON'T

- Overuse utilities (use custom CSS for complex patterns)
- Chain too many classes on single element
- Replace component classes with utilities
- Forget to test responsive behavior
