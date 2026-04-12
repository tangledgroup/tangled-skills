---
name: daisyui-5-5
description: A skill for using DaisyUI 5.5, a component library for Tailwind CSS 4 that provides semantic class names for common UI components with built-in theming support. Use when building responsive web interfaces with pre-styled components, implementing theme switching, or creating consistent design systems without writing custom CSS.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - tailwindcss
  - daisyui
  - ui-components
  - theming
  - css-framework
  - web-design
category: frontend-development
required_environment_variables: []
---

# DaisyUI 5.5

DaisyUI 5.5 is a component library for Tailwind CSS 4 that provides semantic class names for common UI components. It enables rapid UI development with built-in theming, dark mode support, and accessible components without writing custom CSS.

## When to Use

- Building responsive web interfaces with pre-styled components
- Implementing theme switching (light/dark mode or custom themes)
- Creating consistent design systems quickly
- Prototyping UIs without writing custom CSS
- Adding accessible components (modals, dropdowns, menus) to applications
- Styling forms, buttons, cards, navigation, and other common UI elements

## Setup

### Installation

DaisyUI 5 requires **Tailwind CSS 4**. The traditional `tailwind.config.js` file is deprecated in Tailwind CSS v4.

**Using npm (recommended):**

```bash
npm install -D daisyui@latest
```

**CSS configuration:**

```css
@import "tailwindcss";
@plugin "daisyui";
```

**CDN usage (for quick prototyping):**

```html
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://cdn.jsdelivr.net/npm/daisyui@latest/dist/full.min.css" rel="stylesheet" type="text/css" />
```

## Quick Start

### Basic Button

```html
<button class="btn btn-primary">Click me</button>
```

### Themed Alert

```html
<div class="alert alert-success" role="alert">
  <span>Success! Your action was completed.</span>
</div>
```

### Card Component

```html
<div class="card w-96 bg-base-100 shadow-xl">
  <figure><img src="https://picsum.photos/400/300" alt="Demo image" /></figure>
  <div class="card-body">
    <h2 class="card-title">Card Title</h2>
    <p>Card description goes here.</p>
    <div class="card-actions">
      <button class="btn btn-primary">Action</button>
    </div>
  </div>
</div>
```

See [Core Concepts](references/01-core-concepts.md) for detailed theming and color usage.

## Core Features

### Theming

DaisyUI includes 27+ built-in themes that can be enabled:

```css
@plugin "daisyui" {
  themes: light --default, dark --prefersdark, cupcake, bumblebee, emerald;
}
```

Apply themes with `data-theme` attribute:

```html
<html data-theme="cupcake">
<!-- or -->
<div data-theme="dark">Dark themed section</div>
```

Refer to [Theming Guide](references/02-theming-guide.md) for custom theme creation.

### Semantic Colors

Use DaisyUI's semantic color system instead of Tailwind's static colors:

```html
<!-- Changes with theme -->
<div class="bg-primary text-primary-content">Themed colors</div>
<div class="bg-base-100 text-base-content">Base colors</div>

<!-- Static - same on all themes (not recommended) -->
<div class="bg-blue-500 text-white">Static colors</div>
```

### Component Structure

All DaisyUI components follow a consistent pattern:

- **Component**: Required base class (e.g., `btn`, `card`, `modal`)
- **Part**: Child element classes (e.g., `card-body`, `modal-action`)
- **Style**: Visual variants (e.g., `btn-outline`, `alert-soft`)
- **Color**: Theme colors (e.g., `btn-primary`, `badge-success`)
- **Size**: Size modifiers (e.g., `btn-lg`, `input-sm`)
- **Modifier**: Behavior changes (e.g., `btn-block`, `dropdown-hover`)

## Component Categories

### Form Components
- **Input** - Text fields with styles and sizes
- **Select** - Dropdown selects
- **Checkbox** - Styled checkboxes
- **Radio** - Radio button groups
- **Range** - Slider inputs
- **File Input** - File upload fields
- **Textarea** - Multi-line text inputs

See [Form Components](references/03-form-components.md) for detailed usage.

### Interactive Components
- **Button** - Action buttons with multiple styles
- **Modal** - Dialog boxes and popups
- **Dropdown** - Click/hover menus
- **Accordion** - Collapsible content sections
- **Tabs** - Tabbed navigation
- **Tooltip** - Hover hints
- **Popover** - Contextual popups

Refer to [Interactive Components](references/04-interactive-components.md) for implementation details.

### Layout Components
- **Navbar** - Top navigation bars
- **Footer** - Page footers
- **Drawer** - Sidebar layouts with toggle
- **Hero** - Large hero sections
- **Container** - Content containers

See [Layout Components](references/05-layout-components.md) for responsive patterns.

### Display Components
- **Card** - Content cards with images
- **Alert** - Notification messages
- **Badge** - Status indicators
- **Avatar** - User profile images
- **Table** - Data tables
- **Stats** - Statistics displays
- **Timeline** - Vertical timelines

Refer to [Display Components](references/06-display-components.md) for usage examples.

### Feedback Components
- **Loading** - Loading animations (spinner, dots, bars)
- **Skeleton** - Loading placeholders
- **Progress** - Progress bars
- **Radial Progress** - Circular progress indicators

## Reference Files

- [`references/01-core-concepts.md`](references/01-core-concepts.md) - Color system, theming basics, and CSS customization
- [`references/02-theming-guide.md`](references/02-theming-guide.md) - Built-in themes, custom theme creation, and theme switching
- [`references/03-form-components.md`](references/03-form-components.md) - Input, select, checkbox, radio, range, and form styling
- [`references/04-interactive-components.md`](references/04-interactive-components.md) - Button, modal, dropdown, accordion, tabs, tooltip, popover
- [`references/05-layout-components.md`](references/05-layout-components.md) - Navbar, footer, drawer, hero, and layout patterns
- [`references/06-display-components.md`](references/06-display-components.md) - Card, alert, badge, avatar, table, stats, timeline
- [`references/07-advanced-patterns.md`](references/07-advanced-patterns.md) - Customization, overrides, responsive design, and best practices

## Troubleshooting

### Components not styling correctly
- Ensure Tailwind CSS 4 is properly configured
- Verify `@plugin "daisyui";` is included in CSS after `@import "tailwindcss"`
- Check that build process includes PostCSS if using it

### Colors not changing with theme
- Use DaisyUI semantic colors (`primary`, `base-100`) instead of Tailwind colors (`blue-500`)
- Ensure `data-theme` attribute is set on `<html>` or parent element
- Don't use `dark:` prefix with DaisyUI colors - they auto-switch

### Custom styles not overriding components
- Use `!` for important: `btn bg-red-500!`
- Or use Tailwind utility classes: `btn px-10`
- Avoid custom CSS when possible

### Modal not closing
- For dialog element modals, include `<form method="dialog">Close</form>`
- For checkbox modals, ensure label `for` attribute matches checkbox `id`
- Check for unique IDs if multiple modals exist

See [Advanced Patterns](references/07-advanced-patterns.md) for more solutions.
