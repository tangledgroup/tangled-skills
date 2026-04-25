# Utility Reference

Complete reference of Tailwind CSS v4.2 utility classes with examples and usage patterns.

## Layout

### Display
```html
<div class="block">Block level</div>
<div class="inline">Inline</div>
<div class="inline-block">Inline block</div>
<div class="flex">Flex container</div>
<div class="inline-flex">Inline flex</div>
<div class="grid">Grid container</div>
<div class="inline-grid">Inline grid</div>
<div class="hidden">Hidden (display: none)</div>
```

### Position
```html
<div class="static">Static positioning</div>
<div class="fixed">Fixed to viewport</div>
<div class="absolute">Absolute positioned</div>
<div class="relative">Relative to normal flow</div>
<div class="sticky">Sticky on scroll</div>

<!-- Position values -->
<div class="top-0 left-0 right-0 bottom-0">Full coverage</div>
<div class="top-4 left-1/2 -translate-x-1/2">Centered top</div>
<div class="inset-0">All sides 0</div>
<div class="inset-x-0 inset-y-4">Horizontal full, vertical 1rem</div>
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

### Overflow
```html
<div class="overflow-auto">Scroll when needed</div>
<div class="overflow-hidden">Clip overflow</div>
<div class="overflow-visible">Show overflow</div>
<div class="overflow-scroll">Always show scrollbars</div>
<div class="overflow-x-auto">Horizontal scroll</div>
<div class="overflow-y-hidden">Vertical clip</div>

<!-- Overscroll behavior -->
<div class="overscroll-contain">Prevent pull-to-refresh</div>
<div class="overscroll-auto">Default browser behavior</div>
```

### Visibility
```html
<div class="visible">Visible</div>
<div class="invisible">Invisible but takes space</div>
```

## Flexbox & Grid

### Flex Container
```html
<div class="flex">Flex row</div>
<div class="flex-col">Flex column</div>
<div class="flex-wrap">Wrap items</div>
<div class="flex-nowrap">No wrap</div>
<div class="flex-wrap-reverse">Reverse wrap</div>

<!-- Flex direction -->
<div class="flex-row">Left to right</div>
<div class="flex-row-reverse">Right to left</div>
<div class="flex-col">Top to bottom</div>
<div class="flex-col-reverse">Bottom to top</div>

<!-- Justify content -->
<div class="justify-start">Start aligned</div>
<div class="justify-end">End aligned</div>
<div class="justify-center">Centered</div>
<div class="justify-between">Space between</div>
<div class="justify-around">Space around</div>
<div class="justify-evenly">Space evenly</div>

<!-- Align items -->
<div class="items-start">Start aligned</div>
<div class="items-end">End aligned</div>
<div class="items-center">Vertically centered</div>
<div class="items-stretch">Stretch to fill</div>
<div class="items-baseline">Baseline aligned</div>

<!-- Content alignment -->
<div class="content-start">Start</div>
<div class="content-end">End</div>
<div class="content-center">Center</div>
<div class="content-between">Between</div>
<div class="content-around">Around</div>
<div class="content-evenly">Evenly</div>
```

### Flex Items
```html
<div class="flex-auto">Auto grow and shrink</div>
<div class="flex-1">Grow and shrink (flex: 1)</div>
<div class="flex-initial">Shrink only</div>
<div class="flex-none">No flex</div>

<!-- Grow -->
<div class="grow">flex-grow: 1</div>
<div class="grow-0">flex-grow: 0</div>
<div class="grow-2">flex-grow: 2</div>

<!-- Shrink -->
<div class="shrink">flex-shrink: 1</div>
<div class="shrink-0">flex-shrink: 0</div>

<!-- Basis -->
<div class="basis-auto">flex-basis: auto</div>
<div class="basis-full">flex-basis: 100%</div>
<div class="basis-1/2">flex-basis: 50%</div>
```

### Order
```html
<div class="order-first">order: -9999</div>
<div class="order-last">order: 9999</div>
<div class="order-none">order: 0</div>
<div class="order-1">order: 1</div>
<div class="order-12">order: 12</div>
```

### Grid Container
```html
<div class="grid">Grid container</div>

<!-- Columns -->
<div class="grid-cols-1">1 column</div>
<div class="grid-cols-2">2 columns</div>
<div class="grid-cols-3">3 columns</div>
<div class="grid-cols-4">4 columns</div>
<div class="grid-cols-5">5 columns</div>
<div class="grid-cols-6">6 columns</div>
<div class="grid-cols-7">7 columns</div>
<div class="grid-cols-8">8 columns</div>
<div class="grid-cols-9">9 columns</div>
<div class="grid-cols-10">10 columns</div>
<div class="grid-cols-12">12 columns</div>
<div class="grid-cols-none">grid-template-columns: none</div>
<div class="grid-cols-auto-fit">auto-fit</div>
<div class="grid-cols-auto-min-max">minmax(0, 1fr)</div>

<!-- Rows -->
<div class="grid-rows-1">1 row</div>
<div class="grid-rows-2">2 rows</div>
<div class="grid-rows-none">grid-template-rows: none</div>
```

### Grid Items
```html
<div class="col-auto">Auto column</div>
<div class="col-span-1">Span 1 column</div>
<div class="col-span-2">Span 2 columns</div>
<div class="col-span-full">Span all columns</div>
<div class="col-start-1">Start at line 1</div>
<div class="col-end-3">End at line 3</div>

<div class="row-auto">Auto row</div>
<div class="row-span-2">Span 2 rows</div>
<div class="row-span-full">Span all rows</div>
<div class="row-start-1">Start at line 1</div>
<div class="row-end-3">End at line 3</div>
```

### Gap
```html
<div class="gap-0">No gap</div>
<div class="gap-1">0.25rem gap</div>
<div class="gap-4">1rem gap</div>
<div class="gap-8">2rem gap</div>
<div class="gap-x-4">Horizontal gap</div>
<div class="gap-y-2">Vertical gap</div>
```

## Spacing

### Padding
```html
<div class="p-0">No padding</div>
<div class="p-1">0.25rem padding</div>
<div class="p-4">1rem padding</div>
<div class="p-8">2rem padding</div>
<div class="px-4">Horizontal padding</div>
<div class="py-2">Vertical padding</div>
<div class="ps-4">Start padding (logical)</div>
<div class="pe-4">End padding (logical)</div>
<div class="pt-4">Top padding</div>
<div class="pr-4">Right padding</div>
<div class="pb-4">Bottom padding</div>
<div class="pl-4">Left padding</div>
```

### Margin
```html
<div class="m-0">No margin</div>
<div class="m-auto">Auto margin</div>
<div class="mx-auto">Horizontal auto (center)</div>
<div class="my-4">Vertical margin 1rem</div>
<div class="mt-0">Top margin 0</div>
<div class="-mb-4">Negative bottom margin</div>
```

## Sizing

### Width
```html
<div class="w-0">width: 0</div>
<div class="w-full">width: 100%</div>
<div class="w-auto">width: auto</div>
<div class="w-screen">width: 100vw</div>
<div class="w-min">width: min-content</div>
<div class="w-max">width: max-content</div>
<div class="w-1/2">width: 50%</div>
<div class="w-1/3">width: 33.33%</div>
<div class="w-1/4">width: 25%</div>
<div class="w-px">width: 1px</div>
```

### Height
```html
<div class="h-0">height: 0</div>
<div class="h-full">height: 100%</div>
<div class="h-auto">height: auto</div>
<div class="h-screen">height: 100vh</div>
<div class="h-min">height: min-content</div>
<div class="h-max">height: max-content</div>
<div class="h-px">height: 1px</div>
```

### Min/Max Width
```html
<div class="min-w-0">min-width: 0</div>
<div class="min-w-full">min-width: 100%</div>
<div class="min-w-min">min-width: min-content</div>
<div class="min-w-max">min-width: max-content</div>

<div class="max-w-none">max-width: none</div>
<div class="max-w-0">max-width: 0</div>
<div class="max-w-full">max-width: 100%</div>
<div class="max-w-prose">max-width: 65ch</div>
<div class="max-w-screen-sm">max-width: 640px</div>
```

### Min/Max Height
```html
<div class="min-h-0">min-height: 0</div>
<div class="min-h-full">min-height: 100%</div>
<div class="min-h-screen">min-height: 100vh</div>

<div class="max-h-none">max-height: none</div>
<div class="max-h-full">max-height: 100%</div>
<div class="max-h-screen">max-height: 100vh</div>
```

## Typography

### Font Family
```html
<p class="font-sans">Sans-serif</p>
<p class="font-serif">Serif</p>
<p class="font-mono">Monospace</p>
```

### Font Size
```html
<p class="text-xs">xs (0.75rem)</p>
<p class="text-sm">sm (0.875rem)</p>
<p class="text-base">base (1rem)</p>
<p class="text-lg">lg (1.125rem)</p>
<p class="text-xl">xl (1.25rem)</p>
<p class="text-2xl">2xl (1.5rem)</p>
<p class="text-3xl">3xl (1.875rem)</p>
<p class="text-4xl">4xl (2.25rem)</p>
<p class="text-5xl">5xl (3rem)</p>
<p class="text-6xl">6xl (3.75rem)</p>
<p class="text-7xl">7xl (4.5rem)</p>
<p class="text-8xl">8xl (6rem)</p>
<p class="text-9xl">9xl (8rem)</p>
```

### Font Weight
```html
<p class="font-thin">Thin (100)</p>
<p class="font-extralight">Extra Light (200)</p>
<p class="font-light">Light (300)</p>
<p class="font-normal">Normal (400)</p>
<p class="font-medium">Medium (500)</p>
<p class="font-semibold">Semi Bold (600)</p>
<p class="font-bold">Bold (700)</p>
<p class="font-extrabold">Extra Bold (800)</p>
<p class="font-black">Black (900)</p>
```

### Font Style
```html
<p class="italic">Italic</p>
<p class="not-italic">Not italic</p>
<p class="line-through">Line through</p>
<p class="no-underline">No underline</p>
<p class="overline">Overline</p>
```

### Letter Spacing
```html
<p class="tracking-tighter">Tighter (-0.05em)</p>
<p class="tracking-tight">Tight (-0.025em)</p>
<p class="tracking-normal">Normal (0)</p>
<p class="tracking-wide">Wide (0.025em)</p>
<p class="tracking-wider">Wider (0.05em)</p>
<p class="tracking-widest">Widest (0.1em)</p>
```

### Line Height
```html
<p class="leading-none">leading: 1</p>
<p class="leading-tight">leading: 1.25</p>
<p class="leading-snug">leading: 1.375</p>
<p class="leading-normal">leading: 1.5</p>
<p class="leading-relaxed">leading: 1.625</p>
<p class="leading-loose">leading: 2</p>
```

### Text Align
```html
<p class="text-left">Left aligned</p>
<p class="text-center">Centered</p>
<p class="text-right">Right aligned</p>
<p class="text-justify">Justified</p>
<p class="text-start">Start (logical)</p>
<p class="text-end">End (logical)</p>
```

### Text Color
```html
<p class="text-current">Current color</p>
<p class="text-transparent">Transparent</p>
<p class="text-black">Black</p>
<p class="text-white">White</p>
<p class="text-red-500">Red-500</p>
<p class="text-blue-500">Blue-500</p>
<p class="text-gray-400">Gray-400</p>
<p class="text-inherit">Inherit</p>
```

### Text Decoration
```html
<p class="underline">Underlined</p>
<p class="no-underline">No underline</p>
<p class="line-through">Strikethrough</p>
<p class="overline">Overline</p>

<!-- Decoration style -->
<p class="decoration-solid">Solid line</p>
<p class="decoration-double">Double line</p>
<p class="decoration-dotted">Dotted line</p>
<p class="decoration-dashed">Dashed line</p>
<p class="decoration-wavy">Wavy line</p>

<!-- Decoration thickness -->
<p class="decoration-auto">Auto thickness</p>
<p class="decoration-from-font">From font</p>
<p class="decoration-1">1px thick</p>
<p class="decoration-2">2px thick</p>

<!-- Decoration color -->
<p class="decoration-red-500">Red underline</p>
<p class="decoration-blue-500/50">50% opacity blue</p>

<!-- Underline offset -->
<p class="underline-offset-auto">Auto offset</p>
<p class="underline-offset-1">1px offset</p>
<p class="underline-offset-4">4px offset</p>
```

### Text Transform
```html
<p class="uppercase">UPPERCASE</p>
<p class="lowercase">lowercase</p>
<p class="capitalize">Capitalize</p>
<p class="normal-case">Normal case</p>
```

### Text Overflow
```html
<div class="truncate">Truncate with ellipsis</div>
<div class="overflow-ellipsis">Ellipsis overflow</div>
<div class="overflow-clip">Clip overflow</div>
```

### Line Clamp
```html
<p class="line-clamp-1">Single line clamp</p>
<p class="line-clamp-2">Two line clamp</p>
<p class="line-clamp-3">Three line clamp</p>
```

## Backgrounds

### Background Color
```html
<div class="bg-transparent">Transparent</div>
<div class="bg-current">Current color</div>
<div class="bg-white">White</div>
<div class="bg-black">Black</div>
<div class="bg-red-500">Red-500</div>
<div class="bg-blue-500/50">50% opacity blue</div>
```

### Background Image
```html
<div class="bg-none">No background image</div>
```

### Background Position
```html
<div class="bg-bottom">Bottom positioned</div>
<div class="bg-center">Center positioned</div>
<div class="bg-left">Left positioned</div>
<div class="bg-left-bottom">Left bottom</div>
<div class="bg-left-top">Left top</div>
<div class="bg-right">Right positioned</div>
<div class="bg-right-bottom">Right bottom</div>
<div class="bg-right-top">Right top</div>
<div class="bg-top">Top positioned</div>
```

### Background Repeat
```html
<div class="bg-repeat">Repeat both axes</div>
<div class="bg-no-repeat">No repeat</div>
<div class="bg-repeat-x">Repeat horizontally</div>
<div class="bg-repeat-y">Repeat vertically</div>
<div class="bg-repeat-round">Round repeat</div>
<div class="bg-repeat-space">Space repeat</div>
```

### Background Size
```html
<div class="bg-auto">Auto size</div>
<div class="bg-cover">Cover (object-fit: cover)</div>
<div class="bg-contain">Contain (object-fit: contain)</div>
```

## Borders

### Border Width
```html
<div class="border-0">No border</div>
<div class="border-2">2px border</div>
<div class="border-4">4px border</div>
<div class="border-8">8px border</div>
<div class="border">Default (1px)</div>
<div class="border-x-2">Horizontal borders</div>
<div class="border-y-2">Vertical borders</div>
<div class="border-t-2">Top border</div>
<div class="border-r-2">Right border</div>
<div class="border-b-2">Bottom border</div>
<div class="border-l-2">Left border</div>
```

### Border Color
```html
<div class="border-current">Current color</div>
<div class="border-transparent">Transparent</div>
<div class="border-black">Black</div>
<div class="border-white">White</div>
<div class="border-gray-300">Gray-300</div>
<div class="border-red-500">Red-500</div>
<div class="border-t-blue-500">Top border blue</div>
```

### Border Style
```html
<div class="border-solid">Solid border</div>
<div class="border-dashed">Dashed border</div>
<div class="border-dotted">Dotted border</div>
<div class="border-double">Double border</div>
<div class="border-hidden">Hidden border</div>
<div class="border-none">No border</div>
```

### Border Radius
```html
<div class="rounded-none">No radius</div>
<div class="rounded-sm">Small (0.125rem)</div>
<div class="rounded">Default (0.25rem)</div>
<div class="rounded-md">Medium (0.375rem)</div>
<div class="rounded-lg">Large (0.5rem)</div>
<div class="rounded-xl">Extra large (0.75rem)</div>
<div class="rounded-2xl">2xl (1rem)</div>
<div class="rounded-3xl">3xl (1.5rem)</div>
<div class="rounded-full">Full (9999px)</div>

<!-- Corner-specific -->
<div class="rounded-t-lg">Top rounded</div>
<div class="rounded-tr-lg">Top right rounded</div>
<div class="rounded-br-lg">Bottom right rounded</div>
<div class="rounded-bl-lg">Bottom left rounded</div>
<div class="rounded-tl-lg">Top left rounded</div>
```

## Effects

### Box Shadow
```html
<div class="shadow-none">No shadow</div>
<div class="shadow-xs">Extra small shadow</div>
<div class="shadow-sm">Small shadow</div>
<div class="shadow">Default shadow</div>
<div class="shadow-md">Medium shadow</div>
<div class="shadow-lg">Large shadow</div>
<div class="shadow-xl">Extra large shadow</div>
<div class="shadow-2xl">2xl shadow</div>

<!-- Inset shadows -->
<div class="inset-shadow-sm">Inset small</div>
<div class="inset-shadow-md">Inset medium</div>
<div class="inset-shadow-lg">Inset large</div>
```

### Opacity
```html
<div class="opacity-0">0% opacity</div>
<div class="opacity-5">5%</div>
<div class="opacity-10">10%</div>
<div class="opacity-25">25%</div>
<div class="opacity-50">50%</div>
<div class="opacity-75">75%</div>
<div class="opacity-100">100%</div>
```

### Mix Blend Mode
```html
<div class="mix-blend-normal">Normal</div>
<div class="mix-blend-multiply">Multiply</div>
<div class="mix-blend-screen">Screen</div>
<div class="mix-blend-overlay">Overlay</div>
<div class="mix-blend-darken">Darken</div>
<div class="mix-blend-lighten">Lighten</div>
<div class="mix-blend-color-dodge">Color dodge</div>
<div class="mix-blend-color-burn">Color burn</div>
<div class="mix-blend-hard-light">Hard light</div>
<div class="mix-blend-soft-light">Soft light</div>
<div class="mix-blend-difference">Difference</div>
<div class="mix-blend-exclusion">Exclusion</div>
<div class="mix-blend-hue">Hue</div>
<div class="mix-blend-saturation">Saturation</div>
<div class="mix-blend-color">Color</div>
<div class="mix-blend-luminosity">Luminosity</div>
```

## Filters

### Filter Effects
```html
<!-- Blur -->
<div class="blur-none">No blur</div>
<div class="blur-xs">4px blur</div>
<div class="blur-sm">8px blur</div>
<div class="blur-md">12px blur</div>
<div class="blur-lg">16px blur</div>
<div class="blur-xl">24px blur</div>
<div class="blur-2xl">40px blur</div>
<div class="blur-3xl">64px blur</div>

<!-- Brightness -->
<div class="brightness-0">0% brightness</div>
<div class="brightness-50">50%</div>
<div class="brightness-100">100%</div>
<div class="brightness-125">125%</div>
<div class="brightness-150">150%</div>
<div class="brightness-200">200%</div>

<!-- Contrast -->
<div class="contrast-0">0% contrast</div>
<div class="contrast-50">50%</div>
<div class="contrast-100">100%</div>
<div class="contrast-125">125%</div>
<div class="contrast-150">150%</div>
<div class="contrast-200">200%</div>

<!-- Grayscale -->
<div class="grayscale">100% grayscale</div>
<div class="grayscale-0">0%</div>
<div class="grayscale-5">5%</div>
<div class="grayscale-100">100%</div>

<!-- Hue rotate -->
<div class="hue-rotate-0">0deg</div>
<div class="hue-rotate-15">15deg</div>
<div class="hue-rotate-30">30deg</div>
<div class="hue-rotate-60">60deg</div>
<div class="hue-rotate-90">90deg</div>

<!-- Invert -->
<div class="invert">Invert colors</div>
<div class="invert-0">0%</div>
<div class="invert-100">100%</div>

<!-- Saturate -->
<div class="saturate-0">0% saturation</div>
<div class="saturate-50">50%</div>
<div class="saturate-100">100%</div>
<div class="saturate-150">150%</div>
<div class="saturate-200">200%</div>

<!-- Sepia -->
<div class="sepia">Sepia effect</div>
<div class="sepia-0">0%</div>
<div class="sepia-100">100%</div>

<!-- Drop shadow -->
<div class="drop-shadow-xs">Extra small</div>
<div class="drop-shadow-sm">Small</div>
<div class="drop-shadow-md">Medium</div>
<div class="drop-shadow-lg">Large</div>
<div class="drop-shadow-xl">Extra large</div>
<div class="drop-shadow-2xl">2xl</div>
```

### Backdrop Filters
```html
<div class="backdrop-blur-sm">Small blur</div>
<div class="backdrop-blur-md">Medium blur</div>
<div class="backdrop-blur-lg">Large blur</div>
<div class="backdrop-blur-xl">Extra large</div>
<div class="backdrop-brightness-50">50% brightness</div>
<div class="backdrop-contrast-125">125% contrast</div>
<div class="backdrop-grayscale">Grayscale</div>
<div class="backdrop-invert">Invert</div>
<div class="backdrop-opacity-50">50% opacity</div>
<div class="backdrop-saturate-150">150% saturation</div>
```

## Transitions & Animation

### Transition Properties
```html
<div class="transition-none">No transition</div>
<div class="transition-all">All properties</div>
<div class="transition-colors">Color properties</div>
<div class="transition-opacity">Opacity only</div>
<div class="transition-shadow">Shadow only</div>
<div class="transition-transform">Transform only</div>
<div class="transition">Default (color, opacity, shadow, transform)</div>

<!-- Transition duration -->
<div class="duration-75">75ms</div>
<div class="duration-100">100ms</div>
<div class="duration-150">150ms</div>
<div class="duration-200">200ms</div>
<div class="duration-300">300ms</div>
<div class="duration-500">500ms</div>
<div class="duration-700">700ms</div>
<div class="duration-1000">1000ms</div>

<!-- Transition timing function -->
<div class="ease-linear">Linear</div>
<div class="ease-in">Ease in</div>
<div class="ease-out">Ease out</div>
<div class="ease-in-out">Ease in-out</div>

<!-- Transition delay -->
<div class="delay-75">75ms delay</div>
<div class="delay-100">100ms delay</div>
<div class="delay-150">150ms delay</div>
<div class="delay-200">200ms delay</div>
<div class="delay-300">300ms delay</div>
```

### Animations
```html
<div class="animate-none">No animation</div>
<div class="animate-spin">Continuous spin</div>
<div class="animate-ping">Ping effect</div>
<div class="animate-pulse">Pulse effect</div>
<div class="animate-bounce">Bounce effect</div>
```

## Transforms

### Transform Utilities
```html
<!-- Scale -->
<div class="scale-0">Scale 0%</div>
<div class="scale-50">Scale 50%</div>
<div class="scale-75">Scale 75%</div>
<div class="scale-90">Scale 90%</div>
<div class="scale-95">Scale 95%</div>
<div class="scale-100">Scale 100%</div>
<div class="scale-105">Scale 105%</div>
<div class="scale-110">Scale 110%</div>
<div class="scale-125">Scale 125%</div>
<div class="scale-150">Scale 150%</div>
<div class="scale-x-105">X-axis scale</div>
<div class="scale-y-105">Y-axis scale</div>

<!-- Rotate -->
<div class="rotate-0">0deg</div>
<div class="rotate-1">1deg</div>
<div class="rotate-3">3deg</div>
<div class="rotate-6">6deg</div>
<div class="rotate-12">12deg</div>
<div class="rotate-45">45deg</div>
<div class="rotate-90">90deg</div>
<div class="-rotate-90">-90deg</div>

<!-- Skew -->
<div class="skew-x-3">Skew X 3deg</div>
<div class="skew-y-2">Skew Y 2deg</div>
<div class="-skew-x-12">Skew X -12deg</div>

<!-- Translate -->
<div class="translate-x-0">Translate X 0</div>
<div class="translate-x-full">Translate X 100%</div>
<div class="-translate-x-1/2">Translate X -50%</div>
<div class="translate-y-4">Translate Y 1rem</div>
<div class="-translate-y-full">Translate Y -100%</div>

<!-- Transform origin -->
<div class="origin-center">Center origin</div>
<div class="origin-top">Top origin</div>
<div class="origin-top-right">Top right origin</div>
<div class="origin-right">Right origin</div>
<div class="origin-bottom-right">Bottom right origin</div>
<div class="origin-bottom">Bottom origin</div>
<div class="origin-bottom-left">Bottom left origin</div>
<div class="origin-left">Left origin</div>
<div class="origin-top-left">Top left origin</div>
```

### 3D Transforms
```html
<div class="perspective-none">No perspective</div>
<div class="perspective-dramatic">100px perspective</div>
<div class="perspective-near">300px perspective</div>
<div class="perspective-normal">500px perspective</div>
<div class="perspective-midrange">800px perspective</div>
<div class="perspective-distant">1200px perspective</div>

<div class="preserve-3d">Preserve 3D</div>
<div class="flat">Flat (discard 3D)</div>

<div class="backface-visible">Backface visible</div>
<div class="backface-hidden">Backface hidden</div>
```

## Interactivity

### Cursor
```html
<div class="cursor-auto">Auto cursor</div>
<div class="cursor-default">Default</div>
<div class="cursor-pointer">Pointer</div>
<div class="cursor-wait">Wait</div>
<div class="cursor-text">Text</div>
<div class="cursor-move">Move</div>
<div class="cursor-help">Help</div>
<div class="cursor-not-allowed">Not allowed</div>
<div class="cursor-none">No cursor</div>
```

### Pointer Events
```html
<div class="pointer-events-none">No pointer events</div>
<div class="pointer-events-auto">Auto pointer events</div>
```

### Resize
```html
<div class="resize-none">No resize</div>
<div class="resize">Resize both axes</div>
<div class="resize-x">Horizontal resize</div>
<div class="resize-y">Vertical resize</div>
```

### User Select
```html
<div class="select-none">Cannot select</div>
<div class="select-text">Can select text</div>
<div class="select-all">Select all</div>
<div class="select-auto">Auto selection</div>
```

### Scroll Behavior
```html
<div class="scroll-auto">Auto scroll behavior</div>
<div class="scroll-smooth">Smooth scroll</div>
```

## SVG Utilities

### Fill & Stroke
```html
<svg class="fill-current">Current color fill</svg>
<svg class="fill-blue-500">Blue-500 fill</svg>
<svg class="stroke-current">Current color stroke</svg>
<svg class="stroke-red-500">Red-500 stroke</svg>
<svg class="stroke-2">2px stroke width</svg>
<svg class="stroke-4">4px stroke width</svg>
```

## Accessibility

### Forced Color Adjust
```html
<div class="forced-color-adjust-auto">Auto adjust</div>
<div class="forced-color-adjust-none">No adjust</div>
```

## Responsive Modifiers

Apply utilities at different breakpoints:

```html
<!-- Mobile first -->
<div class="w-full md:w-1/2 lg:w-1/3">
  Full width on mobile, half on tablet, third on desktop
</div>

<!-- Hide/show at breakpoints -->
<div class="hidden md:block">Hidden on mobile, visible on medium+</div>
<div class="block lg:hidden">Visible until large, then hidden</div>

<!-- Different styles per breakpoint -->
<button class="px-4 py-2 md:px-6 md:py-3 lg:px-8 lg:py-4">
  Responsive padding
</button>
```

## State Modifiers

### Hover, Focus, Active States
```html
<button class="bg-blue-500 hover:bg-blue-600 focus:ring-2 active:bg-blue-700">
  Interactive button
</button>

<a class="text-gray-600 hover:text-blue-500 focus:underline">
  Link with states
</a>
```

### Focus Variants
```html
<input class="focus:outline-none focus:ring-2 focus:ring-blue-500">
<div class="focus-visible:ring-2">Ring on keyboard focus only</div>
```

### Group Hover
```html
<div class="group">
  <div class="group-hover:text-blue-500">Changes when parent hovered</div>
</div>
```

### Peer States
```html
<input class="peer">
<label class="peer-placeholder-shown:text-gray-400 peer-valid:text-green-500">
  Changes based on sibling input state
</label>
```

### Dark Mode
```html
<div class="bg-white dark:bg-gray-900 text-black dark:text-white">
  Light and dark mode aware
</div>
```

## Arbitrary Values

Use square brackets for custom values:

```html
<!-- Arbitrary length -->
<div class="w-[27%]">27% width</div>
<div class="top-[30px]">30px from top</div>

<!-- Arbitrary color -->
<div class="bg-[#123456]">#123456 background</div>
<div class="text-[oklch(0.5_0.2_250)]">OKLCH color</div>

<!-- Arbitrary property -->
<div class="[&_p]:text-blue-500">All p elements blue</div>
<div class="[transform:rotateY(45deg)]">3D rotation</div>
```

## Important Modifier

Force utility with `!`:

```html
<div class="!visible">Forced visible</div>
<div class="text-red-500 !uppercase">Always uppercase</div>
```
