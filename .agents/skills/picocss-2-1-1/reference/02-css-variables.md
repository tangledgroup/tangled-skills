# CSS Variables

## Overview

Pico exposes 130+ CSS custom properties for full visual customization without overriding compiled stylesheets. All variables are prefixed with `--pico-`.

## Core Variables

**Colors and backgrounds:**
- `--pico-color` — default text color
- `--pico-background-color` — default background
- `--pico-muted-color` — muted/subtle text
- `--pico-muted-border-color` — subtle borders

**Primary accent:**
- `--pico-primary` — primary link/button text color
- `--pico-primary-background` — primary button background
- `--pico-primary-border` — primary border
- `--pico-primary-hover` / `--pico-primary-hover-background` — hover states
- `--pico-primary-focus` — focus ring
- `--pico-primary-inverse` — text on primary background

**Secondary and contrast:**
- `--pico-secondary-*` — secondary button/link colors
- `--pico-contrast-*` — high-contrast button/link colors

## Typography Variables

- `--pico-h1-color` through `--pico-h6-color` — heading text colors (each level has a distinct shade)
- `--pico-font-family` — default font stack
- `--pico-line-height` — base line height

## Form Element Variables

- `--pico-form-element-background-color` — input/select/textarea background
- `--pico-form-element-border-color` — input border
- `--pico-form-element-color` — input text color
- `--pico-form-element-placeholder-color` — placeholder text
- `--pico-form-element-active-border-color` — focused input border
- `--pico-form-element-focus-color` — focus ring
- `--pico-form-element-disabled-opacity` — disabled state opacity
- `--pico-form-element-invalid-border-color` — validation error border
- `--pico-form-element-valid-border-color` — validation success border

## Component Variables

**Cards:**
- `--pico-card-background-color`
- `--pico-card-border-color`
- `--pico-card-box-shadow`
- `--pico-card-sectioning-background-color`

**Modals:**
- `--pico-modal-overlay-background-color`

**Dropdowns:**
- `--pico-dropdown-background-color`
- `--pico-dropdown-border-color`
- `--pico-dropdown-hover-background-color`

**Accordions:**
- `--pico-accordion-border-color`
- `--pico-accordion-active-summary-color`

**Tooltips:**
- `--pico-tooltip-background-color`
- `--pico-tooltip-color`

**Progress:**
- `--pico-progress-background-color`
- `--pico-progress-color`

## Switch and Range Variables

- `--pico-switch-background-color`
- `--pico-switch-checked-background-color`
- `--pico-range-border-color`
- `--pico-range-thumb-color`
- `--pico-range-thumb-active-color`

## Customization Example

Override variables on `:root` or any scoped element:

```css
:root {
  --pico-primary: #6f0xff;
  --pico-primary-background: #5200ae;
  --pico-primary-hover: #9b6dff;
  --pico-primary-hover-background: #6c23f5;
}
```

Scope to a specific section:

```html
<section style="--pico-primary: #ff6b00;">
  <button>Orange themed button</button>
</section>
```

## Icon Variables

Pico includes inline SVG data URIs for form validation icons:
- `--pico-icon-valid` — checkmark icon (green)
- `--pico-icon-invalid` — exclamation icon (red)

These are used with native HTML5 form validation (`:valid` / `:invalid` pseudo-classes).
