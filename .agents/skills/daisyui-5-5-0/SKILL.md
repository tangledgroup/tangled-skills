---
name: daisyui-5-5-0
description: A skill for using DaisyUI 5.5, a component library for Tailwind CSS 4 that provides semantic class names for common UI components with built-in theming support. Use when building responsive web interfaces with pre-styled components, implementing theme switching, or creating consistent design systems without writing custom CSS.
version: "5.5.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
- tailwindcss
- daisyui
- ui-components
- theming
- css-framework
- web-design
category: frontend-development
external_references:
- https://daisyui.com/
- https://github.com/saadeghi/daisyui
---

# DaisyUI 5.5

## Overview

DaisyUI is the most popular free and open-source component library for Tailwind CSS, providing human-friendly semantic class names for common UI components with built-in theming support. Version 5 requires Tailwind CSS 4 and uses the `@plugin` directive instead of the deprecated `tailwind.config.js`.

With over 65 components, 500+ utilities, and 35 built-in themes, DaisyUI enables rapid UI development using only HTML class names — no custom CSS or JavaScript required for most patterns. It works with any framework (React, Vue, Svelte, Next.js, plain HTML) and any build tool or no build tool at all.

## When to Use

- Building responsive web interfaces quickly with pre-styled, accessible components
- Implementing light/dark theme switching without writing custom CSS
- Creating consistent design systems on top of Tailwind CSS
- Prototyping UIs without a build step (via CDN)
- Migrating from Bootstrap or other component libraries to Tailwind CSS
- Adding semantic class names (`btn`, `card`, `navbar`) instead of long utility class strings

## Installation / Setup

### Node.js (recommended)

Install as a development dependency, then add the plugin directive to your CSS:

```css
@import "tailwindcss";
@plugin "daisyui";
```

This is all that's needed. No `tailwind.config.js` file — Tailwind CSS v4 deprecated it entirely.

### CDN (no build step)

For prototyping, documentation sites, or static pages:

```html
<link href="https://cdn.jsdelivr.net/npm/daisyui@5" rel="stylesheet" type="text/css" />
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
```

## Config

DaisyUI configuration is done inline in CSS using the `@plugin` directive:

```css
@plugin "daisyui" {
  themes: light --default, dark --prefersdark;
  root: ":root";
  include: ;
  exclude: ;
  prefix: ;
  logs: true;
}
```

### Config Options

- **`themes`** — List of themes to enable. Use `--default` for the default theme and `--prefersdark` for the automatic dark mode theme. All other listed themes can be activated with `data-theme="name"` on `<html>`.
- **`root`** — CSS selector where theme variables are applied (default: `:root`).
- **`include`** — Specific components to include (comma-separated). Leave empty for all.
- **`exclude`** — Components or utilities to exclude (e.g., `rootscrollgutter, checkbox`).
- **`prefix`** — Class name prefix for all daisyUI classes (e.g., `daisy-` makes `btn` into `daisy-btn`).
- **`logs`** — Enable/disable console logging (`true` or `false`).

### Enabling All Built-in Themes

```css
@plugin "daisyui" {
  themes: light, dark, cupcake, bumblebee --default, emerald, corporate,
    synthwave --prefersdark, retro, cyberpunk, valentine, halloween,
    garden, forest, aqua, lofi, pastel, fantasy, wireframe, black,
    luxury, dracula, cmyk, autumn, business, acid, lemonade,
    night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk;
}
```

## Colors

DaisyUI provides semantic color names that adapt automatically to the active theme. Use these instead of Tailwind's raw color names (like `red-500`) so colors change with themes.

### Color Roles

- **`primary`** / **`primary-content`** — Main brand color and its foreground text color
- **`secondary`** / **`secondary-content`** — Secondary brand color and its foreground
- **`accent`** / **`accent-content`** — Accent color and its foreground
- **`neutral`** / **`neutral-content`** — Neutral dark color for non-saturated UI parts
- **`base-100`** — Primary surface/background color
- **`base-200`** — Slightly darker base, for elevations
- **`base-300`** — Even darker base, for deeper elevations
- **`base-content`** — Foreground text on base surfaces
- **`info`** / **`info-content`** — Informational messages
- **`success`** / **`success-content`** — Success/safe messages
- **`warning`** / **`warning-content`** — Warning/caution messages
- **`error`** / **`error-content`** — Error/danger messages

### Color Usage Rules

- Use daisyUI color names in Tailwind utilities: `bg-primary`, `text-base-content`, `border-error`
- No need for `dark:` prefix — daisyUI colors adapt automatically
- Avoid raw Tailwind colors like `text-gray-800` because they won't adapt to dark themes
- Use `base-*` colors for most page surfaces, reserve `primary` for important interactive elements
- The `*-content` variants are designed to have sufficient contrast on their parent color

## Themes

### Built-in Themes (35 total)

`light`, `dark`, `cupcake`, `bumblebee`, `emerald`, `corporate`, `synthwave`, `retro`, `cyberpunk`, `valentine`, `halloween`, `garden`, `forest`, `aqua`, `lofi`, `pastel`, `fantasy`, `wireframe`, `black`, `luxury`, `dracula`, `cmyk`, `autumn`, `business`, `acid`, `lemonade`, `night`, `coffee`, `winter`, `dim`, `nord`, `sunset`, `caramellatte`, `abyss`, `silk`

### Switching Themes

Add `data-theme="theme-name"` to the `<html>` element:

```html
<html data-theme="cupcake">
```

### Custom Themes

Create a custom theme using the `@plugin "daisyui/theme"` directive:

```css
@plugin "daisyui/theme" {
  name: "mytheme";
  default: true;
  prefersdark: false;
  color-scheme: light;

  --color-base-100: oklch(98% 0.02 240);
  --color-base-200: oklch(95% 0.03 240);
  --color-base-300: oklch(92% 0.04 240);
  --color-base-content: oklch(20% 0.05 240);
  --color-primary: oklch(55% 0.3 240);
  --color-primary-content: oklch(98% 0.01 240);
  --color-secondary: oklch(70% 0.25 200);
  --color-secondary-content: oklch(98% 0.01 200);
  --color-accent: oklch(65% 0.25 160);
  --color-accent-content: oklch(98% 0.01 160);
  --color-neutral: oklch(50% 0.05 240);
  --color-neutral-content: oklch(98% 0.01 240);
  --color-info: oklch(70% 0.2 220);
  --color-info-content: oklch(98% 0.01 220);
  --color-success: oklch(65% 0.25 140);
  --color-success-content: oklch(98% 0.01 140);
  --color-warning: oklch(80% 0.25 80);
  --color-warning-content: oklch(20% 0.05 80);
  --color-error: oklch(65% 0.3 30);
  --color-error-content: oklch(98% 0.01 30);

  --radius-selector: 1rem;
  --radius-field: 0.25rem;
  --radius-box: 0.5rem;
  --size-selector: 0.25rem;
  --size-field: 0.25rem;
  --border: 1px;
  --depth: 1;
  --noise: 0;
}
```

All CSS variables above are required. Colors can use OKLCH, hex, or other CSS color formats. Use the [Theme Generator](https://daisyui.com/theme-generator/) for visual theme creation.

## Usage Rules

1. Style elements by adding daisyUI class names: component class + part classes + modifier classes
2. Customize with Tailwind utility classes when daisyUI classes are insufficient (e.g., `btn px-10`)
3. Use `!` importance override sparingly for specificity conflicts (e.g., `btn bg-red-500!`)
4. Create custom components with Tailwind utilities if daisyUI doesn't have what you need
5. Use responsive prefixes with `flex` and `grid` layouts
6. Only use existing daisyUI class names or Tailwind CSS utility classes
7. Avoid writing custom CSS — prefer daisyUI + Tailwind combination
8. For placeholder images, use `https://picsum.photos/200/300`
9. Don't add `bg-base-100 text-base-content` to body unless necessary
10. Follow Refactoring UI book best practices for design decisions

### Class Name Categories

DaisyUI class names fall into these categories (for reference only, not used in code):

- **component** — The required main class (e.g., `btn`, `card`)
- **part** — A child element of a component (e.g., `card-body`, `collapse-title`)
- **style** — Visual variant (e.g., `btn-outline`, `badge-soft`)
- **behavior** — Interaction behavior (e.g., `btn-disabled`, `dropdown-hover`)
- **color** — Color assignment (e.g., `btn-primary`, `alert-error`)
- **size** — Size variant (e.g., `btn-sm`, `badge-lg`)
- **placement** — Positional placement (e.g., `chat-start`, `tooltip-top`)
- **direction** — Layout direction (e.g., `menu-horizontal`, `steps-vertical`)
- **modifier** — Behavioral or visual modification (e.g., `card-side`, `collapse-open`)
- **variant** — Conditional utility prefix, syntax: `variant:utility-class` (e.g., `is-drawer-open:w-64`)

## Advanced Topics

**Actions Components**: Button, Dropdown, FAB/Speed Dial, Modal, Swap, Theme Controller → [Actions Components](reference/01-actions-components.md)

**Data Display Components**: Accordion, Avatar, Badge, Card, Carousel, Chat, Collapse, Countdown, Diff, Hover 3D, Hover Gallery, Kbd, List, Stat, Status, Table, Text Rotate, Timeline → [Data Display Components](reference/02-data-display-components.md)

**Navigation Components**: Breadcrumbs, Dock, Link, Menu, Navbar, Pagination, Steps, Tab → [Navigation Components](reference/03-navigation-components.md)

**Feedback Components**: Alert, Loading, Progress, Radial Progress, Skeleton, Toast, Tooltip → [Feedback Components](reference/04-feedback-components.md)

**Data Input Components**: Calendar, Checkbox, Fieldset, File Input, Filter, Label, Radio, Range, Rating, Select, Input, Textarea, Toggle, Validator → [Data Input Components](reference/05-data-input-components.md)

**Layout Components**: Divider, Drawer, Footer, Hero, Indicator, Join, Mask, Stack → [Layout Components](reference/06-layout-components.md)

**Mockup Components**: Browser, Code, Phone, Window → [Mockup Components](reference/07-mockup-components.md)
