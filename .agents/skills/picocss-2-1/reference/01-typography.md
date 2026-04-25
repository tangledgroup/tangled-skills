# Typography and Color Schemes

All typographic elements are responsive and scale gracefully across devices and viewports.

## Responsive Font Sizes

Font sizes grow proportionally with screen size using percentage-based base font and `rem` units:

| Breakpoint | xs (< 576px) | sm (≥ 576px) | md (≥ 768px) | lg (≥ 1024px) | xl (≥ 1280px) | xxl (≥ 1536px) |
|------------|--------------|--------------|--------------|---------------|---------------|----------------|
| Base | 16px | 17px | 18px | 19px | 20px | 21px |
| `<h1>` | 32px | 34px | 36px | 38px | 40px | 42px |
| `<h2>` | 28px | 29.75px | 31.5px | 33.25px | 35px | 36.75px |
| `<h3>` | 24px | 25.5px | 27px | 28.5px | 30px | 31.5px |
| `<h4>` | 20px | 21.25px | 22.5px | 23.75px | 25px | 26.25px |
| `<h5>` | 18px | 19.125px | 20.25px | 21.375px | 22.5px | 23.625px |
| `<h6>` | 16px | 17px | 18px | 19px | 20px | 21px |
| `<small>` | 14px | 14.875px | 15.75px | 16.625px | 17.5px | 18.375px |

## Headings

```html
<h1>Heading 1</h1>
<h2>Heading 2</h2>
<h3>Heading 3</h3>
<h4>Heading 4</h4>
<h5>Heading 5</h5>
<h6>Heading 6</h6>
```

## Heading Group

Inside `<hgroup>`, margins are collapsed and the `:last-child` is muted:

```html
<hgroup>
  <h2>Get inspired with CSS</h2>
  <p>How to use CSS to add glam to your Website?</p>
</hgroup>
```

## Inline Text Elements

| Element | Example | HTML |
|---------|---------|------|
| Abbreviation | Abbr. | `<abbr title="Abbreviation">Abbr.</abbr>` |
| Bold | **Bold** | `<strong>Bold</strong>` or `<b>Bold</b>` |
| Italic | *Italic* | `<em>Italic</em>` or `<i>Italic</i>` |
| Underline | <u>Underline</u> | `<u>Underline</u>` |
| Strike | <s>Strike</s> | `<s>Strike</s>` or `<del>Strike</del>` |
| Mark | <mark>Mark</mark> | `<mark>Mark</mark>` |
| Superscript | x² | `<sup>x²</sup>` |
| Subscript | H₂O | `<sub>H₂O</sub>` |
| Keyboard | `kbd` | `<kbd>kbd</kbd>` |
| Code | `code` | `<code>code</code>` |
| Sample | `samp` | `<samp>samp</samp>` |

## Blockquote

```html
<blockquote>
  <p>The only way to do great work is to love what you do.</p>
  <footer>— Steve Jobs</footer>
</blockquote>
```

## Horizontal Rule

```html
<hr>
```

## Color Schemes

Pico comes with two accessible, neutral color schemes: light and dark. It automatically adapts to users' `prefers-color-scheme` without JavaScript.

### Light Mode (Default)

Light mode is the default. Force it with `data-theme="light"`:

```html
<html data-theme="light">
```

### Dark Mode (Auto)

Dark mode activates automatically if user has dark mode enabled via device settings. Force it with `data-theme="dark"`:

```html
<html data-theme="dark">
```

### Customizing Color Schemes

To customize colors for light mode only:

```css
[data-theme="light"],
:root:not([data-theme="dark"]) {
  --pico-primary: #bd3c13;
  --pico-primary-background: #d24317;
  --pico-primary-hover: #942d0d;
}
```

To customize dark mode, define variables twice (auto and forced):

```css
/* Dark mode (Auto) - when user prefers dark */
@media only screen and (prefers-color-scheme: dark) {
  :root:not([data-theme]) {
    --pico-primary: #f56b3d;
    --pico-primary-background: #d24317;
  }
}

/* Dark mode (Forced) - when data-theme="dark" */
[data-theme="dark"] {
  --pico-primary: #f56b3d;
  --pico-primary-background: #d24317;
}
```

See [CSS Variables](02-customization.md) for the complete list of color variables.

### Precompiled Color Themes

Pico v2 includes 20 handcrafted color themes with over 100 combinations accessible via CDN:

```html
<!-- Example: Pico Blue theme -->
<link
  rel="stylesheet"
  href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/themes/pico-blue.min.css"
>
```

Available themes include: pico, pico-blue, pico-green, pico-orange, pico-red, and more. Check the official documentation for the complete list.
