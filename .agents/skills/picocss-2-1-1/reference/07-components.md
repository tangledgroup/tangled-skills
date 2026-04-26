# Components

## Card

The `<article>` element serves as a card — styled with background, border-radius, and box-shadow:

```html
<article>
  I'm a card!
</article>
```

**With sectioning (header/footer):**
```html
<article>
  <header>Card Header</header>
  Card body content here.
  <footer>Card Footer</footer>
</article>
```

The `<header>` and `<footer>` inside `<article>` get distinct background coloring via `--pico-card-sectioning-background-color`.

## Modal

Built with native `<dialog>` element:

```html
<dialog open>
  <article>
    <header>
      <h2>Modal Title</h2>
      <button rel="prev" aria-label="Close"></button>
    </header>
    Modal content goes here.
    <footer>
      <button rel="prev">Cancel</button>
      <button>Confirm</button>
    </footer>
  </article>
</dialog>
```

- `<button rel="prev">` in header floats right for close button alignment
- `[open]` attribute shows the modal
- Overlay background via `--pico-modal-overlay-background-color`
- Can be controlled with JavaScript `showModal()` / `close()` methods

## Accordion

Uses native `<details>` / `<summary>` elements:

```html
<details>
  <summary>First section</summary>
  <p>Content for the first section.</p>
</details>
<details>
  <summary>Second section</summary>
  <p>Content for the second section.</p>
</details>
```

- `summary[role="button"]` gets interactive styling
- Supports `.contrast` variant on summary
- Border color via `--pico-accordion-border-color`

## Dropdown

Native `<details>` / `<summary>` used for dropdown menus:

```html
<details class="dropdown">
  <summary>Menu</summary>
  <ul>
    <li><a href="#">Item 1</a></li>
    <li><a href="#">Item 2</a></li>
    <li><hr></li>
    <li><a href="#">Item 3</a></li>
  </ul>
</details>
```

Stylable via `--pico-dropdown-background-color`, `--pico-dropdown-border-color`, and `--pico-dropdown-hover-background-color`.

## Tooltip

Use `data-tooltip` attribute for native tooltips:

```html
<button data-tooltip="Helpful info" data-placement="bottom">
  Hover me
</button>
```

- `data-placement`: `top`, `bottom`, `left`, `right`
- Background via `--pico-tooltip-background-color`
- Text color via `--pico-tooltip-color`

## Progress

Native `<progress>` element:

```html
<progress value="70" max="100"></progress>
```

Stylable via `--pico-progress-background-color` (track) and `--pico-progress-color` (fill). Uses `accent-color` for native rendering.

## Nav

Navigation uses `<nav>` with semantic list structure:

```html
<nav>
  <ul>
    <li><a href="#" aria-current="page">Home</a></li>
    <li><a href="#">About</a></li>
    <li><a href="#">Contact</a></li>
  </ul>
</nav>
```

`[aria-current="page"]` marks the active link with distinct styling.

## Loading

Buttons show loading spinner when `[aria-busy="true"]`:

```html
<button aria-busy="true">Processing...</button>
```

- Spinner opacity via `--pico-loading-spinner-opacity`
- Works on `<button>`, `<input type="submit">`, `<input type="button">`, and `[role="button"]`

## Group

Button groups (new in v2) using `.group` class:

```html
<div class="group">
  <button>Left</button>
  <button>Center</button>
  <button>Right</button>
</div>
```

Buttons in a group share borders and align seamlessly.

## Component CSS Variables Summary

- `--pico-card-background-color` / `--pico-card-border-color` / `--pico-card-box-shadow`
- `--pico-card-sectioning-background-color`
- `--pico-modal-overlay-background-color`
- `--pico-accordion-border-color`
- `--pico-dropdown-background-color` / `--pico-dropdown-border-color`
- `--pico-tooltip-background-color` / `--pico-tooltip-color`
- `--pico-progress-background-color` / `--pico-progress-color`
- `--pico-loading-spinner-opacity`
