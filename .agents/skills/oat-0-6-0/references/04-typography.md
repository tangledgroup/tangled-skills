# Oat UI - Typography

Complete typography system with automatic styling for semantic HTML elements. No classes required.

## Headings

Six levels of headings styled automatically:

```html
<h1>Heading 1</h1>
<h2>Heading 2</h2>
<h3>Heading 3</h4>
<h4>Heading 4</h4>
<h5>Heading 5</h5>
<h6>Heading 6</h6>
```

### Heading in Cards

Headings inside cards adjust size appropriately:

```html
<article class="card">
  <header>
    <h3>Card Title</h3>
    <p>Card description</p>
  </header>
</article>
```

## Paragraphs

Standard paragraph styling with proper line height and spacing:

```html
<p>This is a paragraph. It has proper line height, letter spacing, and margins for optimal readability.</p>

<p>Multiple paragraphs are separated by consistent vertical spacing.</p>
```

### Lead/Intro Text

Use `class="lead"` for larger introductory text:

```html
<p class="lead">This is a lead paragraph, larger and more prominent for introductions.</p>
```

## Text Emphasis

### Bold and Italic

```html
<p>This text has <strong>bold emphasis</strong> for important points.</p>
<p>This text has <em>italic emphasis</em> for titles or foreign terms.</p>
<p>You can combine <strong><em>bold and italic</em></strong> together.</p>
```

### Underline

```html
<p><u>Underlined text</u> - use sparingly as it conflicts with links</p>
```

### Strikethrough

```html
<p><s>Deleted text</s> or <del>deleted with del tag</del></p>
```

### Inline Code

```html
<p>Use the <code>&lt;div&gt;</code> element for block-level containers.</p>
<p>The <code>console.log()</code> method outputs to the console.</p>
```

## Links

Links styled automatically with hover states:

```html
<p>Check out <a href="https://oat.ink">Oat UI</a> for more information.</p>

<a href="/docs">Documentation</a>
<a href="/demo">Live Demo</a>
```

### Link in Button Style

```html
<a href="/page" class="button">Link as Button</a>
```

## Lists

### Unordered Lists

```html
<ul>
  <li>First item</li>
  <li>Second item</li>
  <li>Third item</li>
</ul>
```

### Ordered Lists

```html
<ol>
  <li>Step one</li>
  <li>Step two</li>
  <li>Step three</li>
</ol>
```

### Nested Lists

```html
<ul>
  <li>Main item
    <ul>
      <li>Nested item 1</li>
      <li>Nested item 2</li>
    </ul>
  </li>
  <li>Another main item</li>
</ul>
```

### Description Lists

```html
<dl>
  <dt>Term 1</dt>
  <dd>Definition 1</dd>
  
  <dt>Term 2</dt>
  <dd>Definition 2</dd>
</dl>
```

## Code Blocks

### Inline Code

Already shown above with `<code>` tag.

### Preformatted Code Blocks

```html
<pre><code>function hello() {
  console.log('Hello, World!');
  return true;
}</code></pre>
```

### Syntax Highlighting

Oat doesn't include syntax highlighting. Use a library like Highlight.js or Prism.js:

```html
<pre><code class="language-javascript">function hello() {
  console.log('Hello, World!');
}</code></pre>

<script src="https://cdn.jsdelivr.net/npm/highlightjs@11/lib/highlight.min.js"></script>
<script>hljs.highlightAll();</script>
```

## Blockquotes

```html
<blockquote>
  This is a blockquote. It's styled with a left border and indentation.
</blockquote>

<blockquote>
  <p>A blockquote can contain multiple paragraphs.</p>
  <p>Each paragraph maintains the quote styling.</p>
</blockquote>
```

### Blockquote with Citation

```html
<blockquote>
  Simplicity is the ultimate sophistication.
  <footer>— Leonardo da Vinci</footer>
</blockquote>
```

## Horizontal Rule

```html
<hr>
```

Creates a thematic break/separator line.

## Text Utilities

### Text Color

```html
<p class="text-light">Lighter, muted text color</p>
```

### Text Alignment

```html
<p class="text-left">Left aligned (default)</p>
<p class="text-center">Center aligned</p>
<p class="text-right">Right aligned</p>
```

### Text Size Modifiers

```html
<p class="small">Smaller text</p>
<p class="large">Larger text</p>
```

## Special Characters and Entities

### Accented Characters

```html
<p>Café, naïve, résumé - accented characters work fine.</p>
```

### Special Symbols

```html
<p>Copyright: © 2024<br>
   Trademark: ®<br>
   Registered: ™<br>
   Euro: €<br>
   Pound: £</p>
```

### Arrows and Pointers

```html
<p>Left: ← Right: → Up: ↑ Down: ↓</p>
<p>Bullet: • Star: ★ Heart: ♥</p>
```

## Typography Best Practices

### Readability

- Use `<p>` tags for all paragraph text
- Keep line length between 45-75 characters
- Use adequate line height (Oat defaults to 1.5)
- Break long content into multiple paragraphs

### Hierarchy

- Use heading levels in order (h1 → h2 → h3)
- Only one h1 per page
- Don't skip heading levels
- Use headings for structure, not styling

### Emphasis

- Prefer `<strong>` over `<b>` (semantic vs visual)
- Prefer `<em>` over `<i>` (semantic vs visual)
- Use bold sparingly for true emphasis
- Avoid multiple emphasis types on same text

## Responsive Typography

Oat's typography is responsive by default. Font sizes scale appropriately on mobile devices using rem units.

### Custom Breakpoints

Override in your CSS if needed:

```css
@media (max-width: 768px) {
  :root {
    --text-8: 1.875rem;  /* Smaller h1 on mobile */
    --text-7: 1.5rem;    /* Smaller h2 on mobile */
  }
}
```

## Font Customization

### Using System Fonts (Default)

Oat uses system font stack by default - fastest loading, most native feel:

```css
:root {
  --font-sans: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
```

### Using Google Fonts

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
:root {
  --font-sans: 'Inter', system-ui, sans-serif;
}
</style>
```

### Using Local Fonts

```css
@font-face {
  font-family: 'CustomFont';
  src: url('/fonts/customfont.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
}

:root {
  --font-sans: 'CustomFont', system-ui, sans-serif;
}
```

## Accessibility

### Semantic HTML

- Use proper heading hierarchy for screen readers
- Use `<strong>` and `<em>` for semantic emphasis
- Use `<code>` for technical terms

### Text Contrast

Oat's default colors meet WCAG AA contrast requirements. When customizing, verify contrast ratios:

- Normal text: 4.5:1 minimum
- Large text (18px+): 3:1 minimum

### Language Declaration

Always declare page language:

```html
<html lang="en">
```

For mixed content:

```html
<p>English text with <span lang="fr">French phrase</span> inside.</p>
```

## Common Patterns

### Article with Metadata

```html
<article>
  <header>
    <h2>Article Title</h2>
    <p class="text-light">By <strong>Jane Doe</strong> on <time datetime="2024-01-15">January 15, 2024</time></p>
  </header>
  
  <p>Article content starts here...</p>
  
  <footer>
    <p class="text-light">Tags: <a href="/tag/design">Design</a>, <a href="/tag/ui">UI</a></p>
  </footer>
</article>
```

### Documentation Section

```html
<section>
  <h2>Installation</h2>
  
  <p>Follow these steps to install Oat:</p>
  
  <ol>
    <li>Download the CSS and JS files</li>
    <li>Include them in your HTML</li>
    <li>Start building!</li>
  </ol>
  
  <pre><code>npm install @knadh/oat</code></pre>
</section>
```

### Quote with Author

```html
<figure>
  <blockquote>
    <p>The best way to predict the future is to invent it.</p>
  </blockquote>
  <figcaption>— Alan Kay</figcaption>
</figure>
```
