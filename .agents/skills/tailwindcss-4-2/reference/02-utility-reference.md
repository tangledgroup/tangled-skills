# Utility Reference

Complete listing of Tailwind CSS 4.2 utility categories with examples and usage patterns.

## Spacing

### Padding

```html
<p class="p-4">All sides</p>
<p class="px-4 py-2">Horizontal and vertical</p>
<p class="pt-4 pr-2 pb-3 pl-6">Individual sides</p>
```

Values use the `--spacing-*` theme scale. Default spacing unit is `0.25rem` (4px), so `p-4` = `1rem`.

### Margin

```html
<div class="m-4">All sides</div>
<div class="mx-auto">Center horizontally (auto margins)</div>
<div class="-ml-4">Negative margin</div>
<div class="mt-[117px]">Arbitrary value</div>
```

### Gap

```html
<div class="flex gap-4">Gap between flex items</div>
<div class="grid gap-x-4 gap-y-8">Grid gaps</div>
```

## Sizing

### Width and Height

```html
<div class="w-full h-screen">Full width, full viewport height</div>
<div class="w-96 h-64">Fixed sizes (6rem x 4rem)</div>
<div class="w-1/2">Fractional width (50%)</div>
<div class="min-h-[300px] max-w-xl">Min/max constraints</div>
```

### Aspect Ratio

```html
<div class="aspect-video">16:9 ratio</div>
<div class="aspect-square">1:1 ratio</div>
<div class="aspect-[4/3]">Custom ratio</div>
```

## Layout

### Display

```html
<div class="flex">Flex container</div>
<div class="grid">Grid container</div>
<div class="hidden">Hidden (display: none)</div>
<div class="inline-block">Inline block</div>
```

Common display utilities: `block`, `inline-block`, `inline-flex`, `flex`, `grid`, `hidden`, `inline-grid`, `table`, `list-item`.

### Flexbox

```html
<div class="flex flex-col items-center justify-between gap-4">
  <div class="flex-1">Grows to fill space</div>
  <div class="flex-shrink-0">Never shrinks</div>
</div>
```

Key utilities: `flex`, `flex-col`, `flex-row`, `flex-wrap`, `flex-1`, `flex-initial`, `flex-grow`, `flex-shrink`, `items-center`, `items-start`, `items-end`, `items-stretch`, `justify-center`, `justify-between`, `justify-around`, `content-center`.

### Grid

```html
<div class="grid grid-cols-3 gap-4 auto-rows-min">
  <div class="col-span-2">Spans 2 columns</div>
  <div class="row-start-1">Starts at row 1</div>
</div>
```

Key utilities: `grid`, `grid-cols-*`, `grid-rows-*`, `col-span-*`, `row-span-*`, `auto-rows-min`, `auto-rows-max`, `auto-rows-fr`, `auto-cols-min`, `grid-flow-dense`.

### Position

```html
<div class="relative">Positioned container</div>
<div class="absolute inset-0">Fill parent</div>
<div class="fixed top-4 right-4">Fixed to viewport</div>
<div class="sticky top-0">Sticky on scroll</div>
```

Values: `static`, `fixed`, `absolute`, `relative`, `sticky`. Combined with `top-*`, `right-*`, `bottom-*`, `left-*` and `inset-*` for offsets.

### Z-Index

```html
<div class="z-0">Base layer</div>
<div class="z-10">Above base</div>
<div class="z-50">Modal overlay</div>
<div class="z-[9999]">Arbitrary z-index</div>
```

## Typography

### Font Family

```html
<p class="font-sans">Default sans-serif stack</p>
<p class="font-serif">Default serif stack</p>
<p class="font-mono">Default monospace stack</p>
<p class="font-display">Custom font from @theme</p>
```

### Font Size and Line Height

```html
<h1 class="text-3xl font-bold">Large heading</h1>
<p class="text-sm/6">Small text with leading-6 line height</p>
<p class="text-base">Default body size (1rem)</p>
```

Sizes: `xs`, `sm`, `base`, `lg`, `xl`, `2xl`, `3xl`, `4xl`, `5xl`, `6xl`, `7xl`, `8xl`, `9xl`.

### Font Weight

```html
<p class="font-light">Light (300)</p>
<p class="font-normal">Normal (400)</p>
<p class="font-medium">Medium (500)</p>
<p class="font-bold">Bold (700)</p>
```

Values: `thin`, `extralight`, `light`, `normal`, `medium`, `semibold`, `bold`, `extrabold`, `black`.

### Text Alignment and Transform

```html
<p class="text-center">Centered text</p>
<p class="text-right">Right-aligned</p>
<p class="uppercase tracking-widest">UPPERCASE WITH TRACKING</p>
<p class="truncate">Text that truncates with ellipsis...</p>
```

### Text Decoration

```html
<a class="underline decoration-2 underline-offset-2">Underlined link</a>
<span class="line-through text-gray-400">Strikethrough</span>
```

### Letter Spacing and Line Clamp

```html
<p class="tracking-tight">Tight tracking</p>
<p class="tracking-wide">Wide tracking</p>
<p class="line-clamp-3">Clamped to 3 lines with ellipsis...</p>
```

## Colors

### Default Palette

Tailwind includes a vast color palette with 11 steps (50–950) for each color:

- Neutral: `slate`, `gray`, `zinc`, `neutral`, `stone`
- Chromatic: `red`, `orange`, `amber`, `yellow`, `lime`, `green`, `emerald`, `teal`, `cyan`, `sky`, `blue`, `indigo`, `violet`, `purple`, `fuchsia`, `pink`, `rose`
- Special: `white`, `black`, `transparent`

### Color Utilities

```html
<div class="bg-white text-gray-900 border-gray-200">Basic colors</div>
<div class="bg-sky-500 hover:bg-sky-600">State variants</div>
<div class="dark:bg-gray-800 dark:text-white">Dark mode</div>
<div class="bg-black/50">Opacity with slash syntax</div>
```

Color applies to: `bg-*` (background), `text-*` (color), `border-*` (border-color), `fill-*` (SVG fill), `stroke-*` (SVG stroke), `ring-*` (outline ring), `placeholder-*`, `accent-*`, `caret-*`, `shadow-*`.

### OKLCH Colors

Tailwind 4.x palette uses OKLCH for perceptually uniform colors:

```css
@theme {
  --color-brand-500: oklch(0.65 0.2 250);
}
```

You can still use hex, rgb, hsl, and named colors.

## Backgrounds

### Background Color and Image

```html
<div class="bg-gradient-to-r from-blue-500 to-purple-600">Gradient</div>
<div class="bg-[url(/img/hero.jpg)] bg-cover bg-center">Image background</div>
<div class="bg-fixed">Fixed background (parallax)</div>
```

### Background Size and Position

```html
<div class="bg-cover">Cover entire element</div>
<div class="bg-contain">Contain within element</div>
<div class="bg-top bg-no-repeat">Positioned, non-repeating</div>
```

## Borders

### Border Width and Color

```html
<div class="border border-gray-200">All sides</div>
<div class="border-b-2 border-blue-500">Bottom border only</div>
<div class="divide-y divide-gray-100">Dividers between children</div>
```

### Border Radius

```html
<div class="rounded">Default radius (0.25rem)</div>
<div class="rounded-lg">Large radius</div>
<div class="rounded-full">Pill/circle shape</div>
<div class="rounded-tl-xl">Individual corner</div>
```

Values: `none`, `sm`, `md`, `lg`, `xl`, `2xl`, `3xl`, `full`.

## Effects

### Box Shadow

```html
<div class="shadow-sm">Subtle shadow</div>
<div class="shadow-lg">Large shadow</div>
<div class="shadow-xl">Extra large shadow</div>
<div class="shadow-none">No shadow</div>
```

### Text Shadow (v4+)

```html
<h1 class="text-shadow-lg">Text with shadow</h1>
```

### Opacity

```html
<div class="opacity-0">Fully transparent</div>
<div class="opacity-50">Half transparent</div>
<div class="opacity-100">Fully opaque</div>
```

### Mix Blend Mode

```html
<img class="mix-blend-multiply" src="overlay.png" />
<div class="bg-blend-color-burn">Background blend</div>
```

## Filters

### Filter Effects

```html
<img class="blur-sm" src="photo.jpg" />
<img class="brightness-75 grayscale contrast-150" src="photo.jpg" />
<img class="hue-rotate-90 invert saturate-200 sepia" src="photo.jpg" />
<div class="drop-shadow-lg">Drop shadow filter</div>
```

### Backdrop Filter

Apply filters to content behind an element:

```html
<div class="backdrop-blur-md bg-white/30">Frosted glass effect</div>
<div class="backdrop-brightness-50 backdrop-grayscale">Dimmed overlay</div>
```

## Transforms

### Scale, Rotate, Translate

```html
<div class="scale-95 hover:scale-105">Scale on hover</div>
<div class="rotate-45">Rotated 45 degrees</div>
<div class="-translate-x-full">Slide off-screen left</div>
<div class="translate-y-1/2">Move down by half height</div>
<div class="skew-x-12">Skewed on X axis</div>
```

### Transform Origin and Style

```html
<div class="origin-top-right rotate-12">Rotate from corner</div>
<div class="transform-3d preserve-3d">3D transform context</div>
<div class="backface-hidden">Hide back face</div>
```

## Transitions and Animation

### Transition Properties

```html
<button class="transition-colors duration-300 ease-in-out hover:bg-blue-600">
  Smooth color transition
</button>

<div class="transition-all duration-500">All properties animate</div>
```

Properties: `transition-none`, `transition`, `transition-colors`, `transition-opacity`, `transition-shadow`, `transition-transform`, `transition-all`.

Duration: `duration-75` through `duration-1000` (75ms to 1000ms).

Timing: `ease-linear`, `ease-in`, `ease-out`, `ease-in-out`.

Delay: `delay-75` through `delay-1000`.

### Animation

```html
<div class="animate-spin">Loading spinner</div>
<div class="animate-ping">Ping effect</div>
<div class="animate-pulse">Pulse effect</div>
<div class="animate-bounce">Bounce effect</div>
```

Custom animations via `@theme`:

```css
@theme {
  --animate-fade-in: fade-in 0.5s ease-in-out;
}
```

## Interactivity

### Cursor and Pointer Events

```html
<button class="cursor-pointer">Clickable</button>
<div class="cursor-not-allowed opacity-50">Disabled</div>
<div class="pointer-events-none">Ignore clicks</div>
```

### Resize and User Select

```html
<textarea class="resize">Resizable textarea</textarea>
<div class="select-none">Cannot be selected</div>
<div class="select-all">Selects all on click</div>
```

### Scroll Behavior

```html
<div class="overflow-auto">Scroll when content overflows</div>
<div class="overflow-hidden">Clip overflow</div>
<div class="scroll-smooth">Smooth scrolling</div>
<div class="overscroll-contain">Contain overscroll</div>
```

### Touch Action

```html
<div class="touch-pan-x">Horizontal pan only</div>
<div class="touch-none">Disable touch gestures</div>
```

## SVG

### Fill and Stroke

```html
<svg class="fill-blue-500 stroke-white stroke-2">
  <!-- SVG content -->
</svg>
```

## Accessibility

### Forced Color Adjust

```html
<div class="forced-color-adjust-auto">Respects Windows high contrast</div>
<div class="forced-color-adjust-none">Disables forced color adjustments</div>
```

## Visibility and Isolation

```html
<div class="invisible">Invisible but takes space</div>
<div class="visible">Visible</div>
<div class="isolate">Create stacking context</div>
<div class="isolation-auto">Auto isolation</div>
```

## Overflow

```html
<div class="overflow-hidden">Clip content</div>
<div class="overflow-scroll">Always show scrollbars</div>
<div class="overflow-x-auto">Horizontal scroll when needed</div>
<div class="truncate">Single-line truncation with ellipsis</div>
```

## Tables

```html
<table class="border-collapse border-spacing-2">
  <caption class="caption-top">Table caption</caption>
</table>
```

Utilities: `border-collapse`, `border-separate`, `border-spacing-*`, `table-auto`, `table-fixed`, `caption-top`, `caption-bottom`.

## Column Layout

```html
<div class="columns-2">Two-column text layout</div>
<div class="columns-3 lg:columns-4">Responsive columns</div>
<div class="break-before-page">Page break before</div>
```

## Line Height as Spacing

Tailwind 4.x supports using line-height values for vertical rhythm:

```html
<p class="leading-5">Tight leading (1.25rem)</p>
<p class="leading-relaxed">Relaxed leading (1.625)</p>
```

Values: `none`, `tight`, `snug`, `normal`, `relaxed`, `loose`, plus numeric values.

## Container Queries (v4+)

Tailwind 4.x supports container queries for component-level responsive design:

```html
<div class="@container">
  <div class="@sm:text-lg @lg:text-xl">
    Text scales based on container width, not viewport
  </div>
</div>
```

`@container` establishes a query container. `@sm:`, `@md:`, `@lg:`, etc. apply styles based on the container's size.

## Child and Sibling Selectors

Apply utilities to children using descendant selectors:

```html
<div class="*:flex *:items-center [&>*>*]:text-sm">
  <!-- All direct children are flex + items-center -->
  <!-- Grandchildren get text-sm -->
</div>
```

- `*:` — all descendants
- `[&>*]:` — direct children
- `[&>*>*]:` — grandchildren

## Data Attributes

Style based on data attributes:

```html
<div class="[data-state=open]:block [data-state=closed]:hidden">
  Shows/hides based on data-state attribute
</div>
```
