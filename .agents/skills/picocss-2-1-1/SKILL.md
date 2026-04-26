---
name: picocss-2-1-1
description: A skill for using Pico CSS v2.1, a minimalist CSS framework that styles semantic HTML elements elegantly by default with responsive typography, automatic light/dark modes, and over 130 customizable CSS variables. Use when building clean, lightweight web interfaces with pure HTML markup, creating class-light designs without JavaScript dependencies, or implementing accessible design systems with minimal CSS overhead.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "2.1.1"
tags:
  - css-framework
  - semantic-html
  - responsive-design
  - light-dark-mode
  - minimal-css
  - web-development
category: development
external_references:
  - https://picocss.com/
  - https://github.com/picocss/pico
---

# Pico CSS 2.1

## Overview

Pico CSS is a minimalist and lightweight starter kit that prioritizes semantic syntax, making every HTML element responsive and elegant by default. It is a "superpowered HTML reset" — write semantic HTML, add Pico CSS, and get a polished, accessible interface with zero JavaScript dependencies.

Key characteristics:
- **Class-light** — fewer than 10 `.classes` overall (most styling targets HTML elements directly)
- **Semantic-first** — styles native HTML tags (`<header>`, `<main>`, `<article>`, `<form>`, etc.)
- **Responsive everything** — font sizes and spacings scale natively with screen width
- **Light/dark mode** — automatic `prefers-color-scheme` detection, no JavaScript needed
- **130+ CSS variables** — full customization without overriding stylesheets
- **Sass-based** — compile custom builds with modular settings
- **Class-less version** — zero classes needed for basic layouts

## When to Use

- Building clean, lightweight web interfaces with pure HTML markup
- Creating class-light designs without JavaScript dependencies
- Implementing accessible design systems with minimal CSS overhead
- Prototyping quickly with semantic HTML
- Projects where reducing CSS specificity and bundle size matters
- Documentation sites, landing pages, admin panels, and internal tools

## Core Concepts

**Semantic styling**: Pico directly styles HTML tags rather than requiring utility classes. A `<form>` looks great without any `class` attribute. A `<button>` gets proper sizing and colors automatically.

**Responsive typography**: The base font size is defined as a percentage that grows with screen width (16px at xs up to 21px at xxl). All heading sizes scale proportionally using `rem` units, respecting the user's browser default.

**Color schemes**: Light is the default. Dark mode activates automatically via `prefers-color-scheme: dark`. Override with `data-theme="light"` or `data-theme="dark"` on any element.

**Container system**: Use `.container` for centered fixed-width layouts, `.container-fluid` for full-width. Breakpoints range from 510px (sm) to 1450px (xxl).

## Installation / Setup

Four ways to include Pico CSS:

**CDN (recommended for quick start):**
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
```

**NPM:**
```bash
npm install @picocss/pico
```

Then import in your SCSS:
```scss
@use "pico";
```

**Manual download:** Link `css/pico.min.css` from the downloaded archive.

**Composer:**
```bash
composer require picocss/pico
```

**Starter HTML template:**
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="color-scheme" content="light dark">
    <link rel="stylesheet" href="css/pico.min.css">
    <title>Hello world!</title>
  </head>
  <body>
    <main class="container">
      <h1>Hello world!</h1>
    </main>
  </body>
</html>
```

The `<meta name="color-scheme" content="light dark">` tag is essential for proper light/dark mode support.

## Advanced Topics

**Class-less version**: Zero-class semantic styling with automatic containers → [Class-less Version](reference/01-classless-version.md)

**CSS variables**: Over 130 customizable design tokens for colors, spacing, typography, and component styling → [CSS Variables](reference/02-css-variables.md)

**Sass customization**: Compile custom builds with modular settings, themes, and breakpoints → [Sass Customization](reference/03-sass-customization.md)

**Layout system**: Containers, grid, landmarks, sections, and responsive spacing → [Layout System](reference/04-layout-system.md)

**Content elements**: Typography, links, buttons, tables, code blocks, and embedded media → [Content Elements](reference/05-content-elements.md)

**Forms**: Inputs, textareas, selects, checkboxes, radios, switches, and ranges with validation styling → [Forms](reference/06-forms.md)

**Components**: Cards, modals, accordions, dropdowns, tooltips, progress bars, nav, loading states, and groups → [Components](reference/07-components.md)

**Color schemes and themes**: Light/dark modes, `data-theme` attribute, and 20 precompiled color themes → [Color Schemes and Themes](reference/08-color-schemes-themes.md)
