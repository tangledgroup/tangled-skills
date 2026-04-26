# Content Elements

## Typography

Pico uses responsive font sizes that scale with viewport width. The base size grows from 16px (xs) to 21px (xxl), and all elements use `rem` units so they scale proportionally.

**Responsive font sizes:**

| Element | xs (&lt;576px) | sm (≥576px) | md (≥768px) | lg (≥1024px) | xl (≥1280px) | xxl (≥1536px) |
|---------|------|------|------|------|------|------|
| Base | 16px | 17px | 18px | 19px | 20px | 21px |
| `<h1>` | 32px | 34px | 36px | 38px | 40px | 42px |
| `<h2>` | 28px | 30px | 31.5px | 33px | 35px | 37px |
| `<h3>` | 24px | 26px | 27px | 29px | 30px | 32px |
| `<h4>` | 20px | 21px | 23px | 24px | 25px | 26px |
| `<h5>` | 18px | 19px | 20px | 21px | 23px | 24px |
| `<h6>` | 16px | 17px | 18px | 19px | 20px | 21px |
| `<small>` | 14px | 15px | 16px | 17px | 18px | 18px |

Each heading level has a distinct text color (`--pico-h1-color` through `--pico-h6-color`).

## Links

Styled automatically with primary accent color. Underline appears on hover by default:

```html
<a href="#">A styled link</a>
```

Use `.secondary` for muted links:
```html
<a href="#" class="secondary">Muted link</a>
```

## Buttons

Native `<button>` and `<input type="submit">` elements are styled automatically. They match input field sizing for consistent forms.

**Variants:**
```html
<button>Primary button</button>
<button class="secondary">Secondary button</button>
<button class="contrast">Contrast button</button>
```

Buttons support `outline` variant via `.outline` class and loading states with `[aria-busy="true"]`.

## Tables

Semantic `<table>` elements are styled with borders, padding, and striped row option:

```html
<table class="striped">
  <thead>
    <tr><th>Name</th><th>Email</th></tr>
  </thead>
  <tbody>
    <tr><td>Alice</td><td>alice@example.com</td></tr>
  </tbody>
</table>
```

The `.striped` class adds alternating row backgrounds. Table styling respects `--pico-table-border-color` and `--pico-table-row-stripped-background-color`.

## Code

Inline `<code>` and `<pre>` blocks are styled with monospace font, background color, and rounded corners:

```html
<code>inline code</code>

<pre><code>
block code example
</code></pre>
```

`<kbd>` elements render as keyboard keycaps using `--pico-code-kbd-background-color` and `--pico-code-kbd-color`.

## Embedded Media

`<iframe>`, `<video>`, `<audio>`, and `<canvas>` elements are styled with consistent borders and responsive sizing. `<figure>` with `<figcaption>` provides caption support.

## Other Elements

- `<mark>` — highlighted text with `--pico-mark-background-color`
- `<ins>` — inserted text in green (`--pico-ins-color`)
- `<del>` — deleted text in red (`--pico-del-color`)
- `<blockquote>` — styled with left border (`--pico-blockquote-border-color`) and muted footer
