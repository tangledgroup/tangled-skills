---
name: picocss-2-1
description: A skill for using Pico CSS v2.1, a minimalist CSS framework that styles semantic HTML elements elegantly by default with responsive typography, automatic light/dark modes, and over 130 customizable CSS variables. Use when building clean, lightweight web interfaces with pure HTML markup, creating class-light designs without JavaScript dependencies, or implementing accessible design systems with minimal CSS overhead.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - css-framework
  - semantic-html
  - responsive-design
  - light-dark-mode
  - minimal-css
  - web-development
category: development
---

# Pico CSS v2.1


## Core Concepts

This skill covers the key concepts and fundamental ideas related to this topic.
## Overview

A skill for using Pico CSS v2.1, a minimalist CSS framework that styles semantic HTML elements elegantly by default with responsive typography, automatic light/dark modes, and over 130 customizable CSS variables. Use when building clean, lightweight web interfaces with pure HTML markup, creating class-light designs without JavaScript dependencies, or implementing accessible design systems with minimal CSS overhead.

Pico CSS is a minimalist and lightweight starter kit that prioritizes semantic syntax, making every HTML element responsive and elegant by default. Write HTML, add Pico CSS, and Voilà!

**Key features:**
- Class-light and semantic (fewer than 10 `.classes` overall)
- Great styles with just CSS (no JavaScript dependencies)
- Responsive everything (scales font sizes and spacings automatically)
- Light or dark mode (auto-adapts to `prefers-color-scheme`)
- Easy customization (130+ CSS variables, SASS support, 20 color themes)
- Optimized performance (lean HTML, reduced memory usage)

## When to Use

- Building clean, lightweight web interfaces with minimal CSS overhead
- Creating class-light designs using semantic HTML elements
- Implementing accessible design systems without JavaScript dependencies
- Needing automatic light/dark mode support via `prefers-color-scheme`
- Prototyping quickly with responsive typography and spacing
- Customizing UI with CSS variables or SASS

## Setup

### Install Manually

Download Pico and link `/css/pico.min.css` in the `<head>` of your website:

```html
<link rel="stylesheet" href="css/pico.min.css">
```

### Usage from CDN

Use jsDelivr CDN for a dependency-free setup:

```html
<link
  rel="stylesheet"
  href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css"
>
```

### Install with NPM

```bash
npm install @picocss/pico
```

Or

```bash
yarn add @picocss/pico
```

Then import Pico into your SCSS file:

```scss
@use "pico";
```

Learn more about [customization with SASS](references/02-customization.md).

### Install with Composer

```bash
composer require picocss/pico
```

### Starter HTML Template

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

## Quick Start

### Class-Light Semantic HTML

Pico directly styles your HTML tags. Write semantic HTML and it looks great:

```html
<main class="container">
  <hgroup>
    <h1>Welcome to Pico CSS</h1>
    <p>A minimalist framework for semantic HTML</p>
  </hgroup>

  <section>
    <h2>Features</h2>
    <ul>
      <li>Responsive typography</li>
      <li>Automatic light/dark mode</li>
      <li>130+ CSS variables</li>
    </ul>
  </section>

  <form>
    <label for="email">Email address</label>
    <input id="email" type="email" placeholder="you@example.com">
    <button type="submit">Subscribe</button>
  </form>
</main>
```

### Class-Less Version

For pure HTML purists, Pico offers a `.classless` version where `<header>`, `<main>`, and `<footer>` inside `<body>` act as containers:

```html
<link
  rel="stylesheet"
  href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.classless.min.css"
>
```

Or use `.fluid.classless` for a fluid container:

```html
<link
  rel="stylesheet"
  href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.fluid.classless.min.css"
>
```

## Common Operations

### Responsive Typography

Font sizes scale automatically with viewport width (xs to xxl breakpoints):

See [Typography Reference](references/01-typography.md) for detailed font size tables and examples.

### Forms with Semantic HTML

All form elements are fully responsive with pure semantic HTML:

```html
<form>
  <fieldset>
    <label>
      First name
      <input name="first_name" placeholder="First name" autocomplete="given-name">
    </label>
    <label>
      Email
      <input type="email" name="email" placeholder="Email" autocomplete="email">
    </label>
  </fieldset>

  <input type="submit" value="Subscribe">
</form>
```

See [Forms Reference](references/03-forms.md) for all form element types and patterns.

### Grid Layout

Use `.grid` for responsive layouts:

```html
<div class="grid">
  <article>Card 1</article>
  <article>Card 2</article>
  <article>Card 3</article>
</div>
```

See [Layout Reference](references/04-layout.md) for grid, container, and landmarks.

### Light/Dark Mode

Pico automatically adapts to user's `prefers-color-scheme`. Force a theme with `data-theme`:

```html
<html data-theme="dark">  <!-- Force dark mode -->
<html data-theme="light"> <!-- Force light mode -->
```

See [Color Schemes Reference](references/01-typography.md#color-schemes) for customization.

## Reference Files

- [`references/01-typography.md`](references/01-typography.md) - Typography, headings, text elements, color schemes
- [`references/02-customization.md`](references/02-customization.md) - CSS variables, SASS customization, themes
- [`references/03-forms.md`](references/03-forms.md) - Form elements, inputs, buttons, validation patterns
- [`references/04-layout.md`](references/04-layout.md) - Grid, container, landmarks, section styling
- [`references/05-components.md`](references/05-components.md) - Cards, modals, nav, dropdowns, accordions
- [`references/06-troubleshooting.md`](references/06-troubleshooting.md) - Common issues and solutions

**Note:** `{baseDir}` refers to the skill's base directory (e.g., `.agents/skills/picocss-2-1/`). All paths in this skill are relative to this directory.

## Troubleshooting

### Elements not styling correctly

Ensure you're using semantic HTML elements (`<form>`, `<button>`, `<h1>`-`<h6>`, etc.) and that Pico CSS is loaded before your custom styles.

### Dark mode not working

Add `<meta name="color-scheme" content="light dark">` to your `<head>` and ensure you're not forcing a theme with `data-theme`.

### Custom styles not applying

Pico uses low-specificity selectors. Your custom styles should override without issues. If needed, use CSS variables instead of overriding selectors.

See [Troubleshooting Reference](references/06-troubleshooting.md) for more solutions.

## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
