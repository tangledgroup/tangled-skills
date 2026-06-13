# Forms

## Overview

Pico styles all form elements automatically. Inputs are `width: 100%` by default and match button sizing for consistent forms. Labels wrap inputs when placed inside `<label>` elements, creating stacked form layouts.

## Basic Form Structure

```html
<form>
  <fieldset>
    <label>
      First name
      <input placeholder="First name" name="first_name" autocomplete="given-name">
    </label>
    <label>
      Email
      <input type="email" placeholder="Email" name="email" autocomplete="email">
    </label>
  </fieldset>
  <input type="submit" value="Subscribe">
</form>
```

`<fieldset>` groups related fields with a styled border. `<legend>` provides group titles.

## Input Types

All standard input types are styled consistently:

- `text`, `email`, `password`, `tel`, `url`, `search`
- `number`, `date`, `time`, `datetime-local`, `month`, `week`
- `color` — native color picker with Pico styling
- `file` — file upload with styled button

```html
<label>
  Text input
  <input type="text" placeholder="Enter text">
</label>

<label>
  Search
  <input type="search" placeholder="Search...">
</label>
```

## Textarea

Multi-line text input, auto-expanding height:

```html
<label>
  Message
  <textarea placeholder="Type your message..."></textarea>
</label>
```

## Select

Dropdown selection with native browser styling enhanced by Pico:

```html
<label>
  Option
  <select>
    <option value="1">Option 1</option>
    <option value="2">Option 2</option>
  </select>
</label>
```

## Checkboxes

Standard checkboxes with Pico accent color:

```html
<label>
  <input type="checkbox" name="agree">
  I agree to the terms
</label>
```

Uses `accent-color: var(--pico-primary)` for native checkbox styling.

## Radios

Radio button groups:

```html
<label>
  <input type="radio" name="plan" value="free">
  Free plan
</label>
<label>
  <input type="radio" name="plan" value="pro">
  Pro plan
</label>
```

## Switch

Toggle switch using `role="switch"`:

```html
<label>
  <input type="checkbox" role="switch" name="notifications">
  Enable notifications
</label>
```

Stylable via `--pico-switch-background-color`, `--pico-switch-checked-background-color`, and `--pico-switch-thumb-box-shadow`.

## Range

Slider input:

```html
<label>
  Volume
  <input type="range" min="0" max="100" value="50">
</label>
```

Stylable via `--pico-range-border-color`, `--pico-range-thumb-color`, and `--pico-range-thumb-active-color`.

## Form Validation

Pico uses native HTML5 validation with visual feedback:

```html
<form>
  <label>
    Email
    <input type="email" required placeholder="Enter email">
  </label>
  <input type="submit" value="Submit">
</form>
```

- `:valid` inputs show green border (`--pico-form-element-valid-border-color`) with checkmark icon
- `:invalid` inputs show red border (`--pico-form-element-invalid-border-color`) with exclamation icon
- Icons are SVG data URIs via `--pico-icon-valid` and `--pico-icon-invalid`

## CSS Variables for Forms

- `--pico-form-element-background-color` — input background
- `--pico-form-element-border-color` — default border
- `--pico-form-element-color` — text color inside inputs
- `--pico-form-element-placeholder-color` — placeholder text
- `--pico-form-element-active-border-color` — focused border
- `--pico-form-element-focus-color` — focus ring color
- `--pico-form-element-disabled-opacity` — disabled state (default: 0.5)
- `--pico-form-element-invalid-border-color` — error state border
- `--pico-form-element-valid-border-color` — success state border
