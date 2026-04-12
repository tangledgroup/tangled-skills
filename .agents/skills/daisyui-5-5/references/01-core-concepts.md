# DaisyUI Core Concepts

This guide covers the fundamental concepts of DaisyUI 5.5 including the color system, CSS customization, and usage rules.

## Color System

### Semantic Color Names

DaisyUI adds semantic color names to Tailwind CSS that change based on the active theme:

| Color Name | Purpose | Content Color |
|------------|---------|---------------|
| `primary` | Primary brand color | `primary-content` |
| `secondary` | Secondary brand color | `secondary-content` |
| `accent` | Accent brand color | `accent-content` |
| `neutral` | Neutral dark color | `neutral-content` |
| `base-100` | Base surface (background) | `base-content` |
| `base-200` | Base elevated surface | - |
| `base-300` | Base higher elevation | - |
| `info` | Informative messages | `info-content` |
| `success` | Success/safe messages | `success-content` |
| `warning` | Warning/caution messages | `warning-content` |
| `error` | Error/danger messages | `error-content` |

### Color Usage Rules

1. **Use semantic colors for theming**: DaisyUI color names include CSS variables, so they change automatically based on the theme
2. **No `dark:` prefix needed**: Unlike Tailwind colors, DaisyUI colors auto-switch between light and dark themes
3. **Avoid Tailwind static colors**: Using `text-gray-800` on `bg-base-100` would be unreadable on dark themes since `base-100` becomes dark
4. **Content colors have contrast**: `*-content` colors are designed with proper contrast for their associated colors

### Color Examples

```html
<!-- Primary color - changes with theme -->
<button class="btn btn-primary">Primary Action</button>

<!-- Base colors for page structure -->
<body class="bg-base-100 text-base-content">
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title text-base-content">Title</h2>
    </div>
  </div>
</body>

<!-- Semantic colors for feedback -->
<div class="alert alert-success" role="alert">
  <span>Success! Operation completed.</span>
</div>

<div class="alert alert-error" role="alert">
  <span>Error: Something went wrong.</span>
</div>

<!-- Using colors with Tailwind utilities -->
<div class="bg-primary text-primary-content p-4 rounded">
  Themed background with proper contrast
</div>

<div class="border border-primary">
  Primary colored border
</div>

<div class="hover:bg-secondary transition-colors">
  Hover changes to secondary color
</div>
```

## Component Class Structure

DaisyUI class names fall into these categories:

| Category | Description | Example |
|----------|-------------|---------|
| `component` | Required base class | `btn`, `card`, `modal` |
| `part` | Child element classes | `card-body`, `modal-action` |
| `style` | Visual style variants | `btn-outline`, `alert-soft` |
| `behavior` | Behavior modifiers | `btn-disabled`, `dropdown-hover` |
| `color` | Theme color application | `btn-primary`, `badge-success` |
| `size` | Size modifiers | `btn-lg`, `input-sm` |
| `placement` | Position placement | `chat-start`, `modal-top` |
| `direction` | Direction orientation | `steps-vertical`, `join-horizontal` |
| `modifier` | Special modifications | `btn-block`, `table-zebra` |
| `variant` | Conditional styles | `is-drawer-open:hidden` |

### Component Syntax Pattern

```html
<!-- Basic component -->
<button class="btn">Button</button>

<!-- With color -->
<button class="btn btn-primary">Primary Button</button>

<!-- With style -->
<button class="btn btn-outline">Outline Button</button>

<!-- Combined: component + color + style + size -->
<button class="btn btn-primary btn-outline btn-lg">Large Outline Primary</button>

<!-- With modifier -->
<button class="btn btn-block">Full Width Button</button>
```

## Usage Rules

### 1. Class Application Order

Apply classes in this order for readability:
1. Component class (required)
2. Color class
3. Style class
4. Size class
5. Modifier/behavior classes
6. Tailwind utility classes

```html
<!-- Recommended order -->
<button class="btn btn-primary btn-outline btn-lg w-full">
  Button
</button>

<!-- Card example -->
<div class="card card-compact bg-base-100 shadow-xl w-96">
  <div class="card-body">
    <h2 class="card-title">Title</h2>
  </div>
</div>
```

### 2. Customization with Tailwind Utilities

Customize components using Tailwind CSS utility classes:

```html
<!-- Custom padding on button -->
<button class="btn px-10">Extra Wide Button</button>

<!-- Custom rounded corners -->
<div class="card rounded-3xl shadow-xl">
  <div class="card-body">Rounded Card</div>
</div>

<!-- Custom spacing -->
<div class="alert alert-info my-4">
  <span>Spaced alert</span>
</div>
```

### 3. Overriding Component Styles

If Tailwind utilities don't work due to CSS specificity, use `!` for important:

```html
<!-- Force background color -->
<button class="btn bg-red-500!">Red Button</button>

<!-- Force text color -->
<div class="badge badge-primary text-white!">White Text Badge</div>

<!-- Force multiple properties -->
<div class="card bg-gradient-to-br from-primary to-secondary!">
  Gradient Card
</div>
```

**Note**: Use `!` sparingly as a last resort. Prefer Tailwind utilities or custom themes.

### 4. Creating Custom Components

If a component doesn't exist in DaisyUI, create it using Tailwind utilities:

```html
<!-- Custom component built with Tailwind -->
<div class="bg-base-200 rounded-lg p-4 shadow-md border border-base-300">
  <h3 class="font-bold text-lg mb-2">Custom Card</h3>
  <p class="text-sm opacity-70">Custom styled content</p>
</div>
```

### 5. Responsive Design with Flex and Grid

When using Tailwind's `flex` and `grid` for layout, make them responsive:

```html
<!-- Responsive grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <div class="card">Card 1</div>
  <div class="card">Card 2</div>
  <div class="card">Card 3</div>
</div>

<!-- Responsive flex -->
<div class="flex flex-col md:flex-row gap-4">
  <div class="flex-1">Content 1</div>
  <div class="flex-1">Content 2</div>
</div>
```

### 6. Allowed Class Names

Only use:
- Existing DaisyUI class names
- Tailwind CSS utility classes

Avoid writing custom CSS when possible.

### 7. Placeholder Images

Use placeholder image services for prototyping:

```html
<img src="https://picsum.photos/400/300" alt="Placeholder" />
<img src="https://picsum.photos/200/200" class="rounded-full" alt="Avatar" />
```

### 8. Font Usage

Don't add custom fonts unless necessary. Use system fonts for best performance.

### 9. Body Styling

Avoid adding `bg-base-100 text-base-content` to `<body>` unless specifically needed:

```html
<!-- Usually not needed -->
<body class="bg-base-100 text-base-content">

<!-- Better - apply to specific containers -->
<div class="min-h-screen bg-base-100 text-base-content">
  <main>Your content</main>
</div>
```

### 10. Design Best Practices

Follow Refactoring UI principles:
- Use sufficient whitespace
- Maintain consistent spacing scale
- Limit color palette usage
- Ensure proper contrast ratios
- Group related elements visually

## CSS Customization

### Basic Plugin Configuration

```css
/* Minimal configuration */
@import "tailwindcss";
@plugin "daisyui";

/* With theme selection */
@import "tailwindcss";
@plugin "daisyui" {
  themes: light --default, dark --prefersdark;
}

/* Full configuration */
@import "tailwindcss";
@plugin "daisyui" {
  themes: light --default, dark --prefersdark, cupcake, bumblebee;
  root: ":root";
  include: ;
  exclude: ;
  prefix: ;
  logs: true;
}
```

### Configuration Options

| Option | Description | Example |
|--------|-------------|---------|
| `themes` | Enable themes, set defaults | `light --default, dark --prefersdark` |
| `root` | CSS selector for theme variables | `":root"` or `"html"` |
| `include` | Components to include | `button, alert` |
| `exclude` | Components to exclude | `checkbox, scrollbar` |
| `prefix` | Class prefix for all DaisyUI classes | `"daisy-"` → `daisy-btn` |
| `logs` | Enable/disable console logs | `true` or `false` |

### Using Prefix

Add a prefix to avoid class name conflicts:

```css
@plugin "daisyui" {
  prefix: "daisy-";
}
```

```html
<!-- Classes become prefixed -->
<button class="daisy-btn daisy-btn-primary">Button</button>
<div class="daisy-card">Card</div>
```

### Including/Excluding Components

Reduce bundle size by including only needed components:

```css
@plugin "daisyui" {
  include: button, alert, card, input, modal;
}
```

Exclude specific components:

```css
@plugin "daisyui" {
  exclude: checkbox, scrollbar, mockup-phone;
}
```

## Variant Prefixes

DaisyUI supports Tailwind's variant syntax for conditional styling:

```html
<!-- Hover states -->
<button class="btn hover:bg-secondary">Hover Button</button>

<!-- Focus states -->
<input class="input focus:outline-none" type="text" />

<!-- Drawer variants -->
<div class="drawer lg:drawer-open">
  <div class="drawer-side is-drawer-close:w-14 is-drawer-open:w-64">
    Sidebar
  </div>
</div>

<!-- Custom variants -->
<div class="dark:bg-dark-100">Dark mode background</div>
```

## Accessibility

DaisyUI components include accessibility features:

### Semantic HTML
- Use proper HTML elements (`<button>`, `<nav>`, `<footer>`)
- Include ARIA attributes where provided
- Maintain keyboard navigation

### Focus Management
- Components support Tab navigation
- Focus visible states are included
- Use `tabindex` appropriately

### Screen Readers
- Use `role="alert"` for alerts
- Add `aria-label` for icon-only buttons
- Include descriptive text for interactive elements

```html
<!-- Accessible alert -->
<div class="alert alert-info" role="alert">
  <span>Important notification</span>
</div>

<!-- Accessible button with icon -->
<button class="btn btn-ghost" aria-label="Close menu">
  ✕
</button>

<!-- Accessible modal -->
<dialog class="modal">
  <form method="dialog" class="modal-box">
    <h3 class="font-bold text-lg">Modal Title</h3>
    <form method="dialog">
      <button class="btn">Close</button>
    </form>
  </form>
</dialog>
```

## Performance Tips

1. **Include only needed components** to reduce CSS size
2. **Use built-in themes** instead of custom colors when possible
3. **Avoid `!` important declarations** - they prevent user stylesheet overrides
4. **Leverage Tailwind's purge** to remove unused utilities in production
5. **Use system fonts** for faster loading

## Browser Support

DaisyUI 5 supports modern browsers with Tailwind CSS 4 compatibility:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)
