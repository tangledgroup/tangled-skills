# Syntax Reference

## Tag Syntax

### Self-Closing Tags

Both `<tag />` and `<tag/>` are supported:

```js
html`<div />`;   // Valid
html`<div/>`;    // Valid
```

### Component Tags

Use `<${}>` to reference component variables (required because `$` is not valid in HTML tag names):

```js
const MyComponent = () => html`<div>Hello</div>`;

// Opening tag with props:
html`<${MyComponent} name="World" />`;

// With closing tag:
html`<${MyComponent}>content</${MyComponent}>`;

// Auto-closing shorthand:
html`<${MyComponent}>content<//>`;
```

Dynamic tag names work with any expression:

```js
const tagName = 'article';
html`<${tagName} />`;  // Renders as <article>
```

## Attribute Syntax

### Static String Values

Quoted and unquoted values are both supported:

```js
html`<a href="/path" />`;       // href: "/path"
html`<a href=/path />`;         // href: "/path" (unquoted)
html`<a class=my-class />`;     // class: "my-class"
```

### Dynamic Values

Use `${}` interpolation for dynamic values:

```js
const url = '/path';
html`<a href=${url} />`;        // href: "/path" (no quotes needed)
```

### Mixed Static and Dynamic Values

Static and dynamic parts are concatenated as strings:

```js
html`<a href="/api/${id}" />`;  // href: "/api/42"
html`<a href=${protocol}://${host} />`;  // href: "https://example.com"
```

### Boolean Attributes

Attributes without values are set to `true`:

```js
html`<input disabled />`;           // { disabled: true }
html`<button autofocus />`;         // { autofocus: true }
html`<details open />`;             // { open: true }
```

Multiple boolean attributes work together:

```js
html`<input disabled readonly />`;  // { disabled: true, readonly: true }
```

### Spread Attributes

Use `...${}` to spread an object into attributes. Note the `$` — this distinguishes it from JSX's `{...props}`:

```js
const props = { class: 'btn', id: 'submit' };
html`<button ...${props}>Click</button>`;
```

Spread can be combined with other attributes:

```js
html`<a b ...${{ foo: 'bar' }} />`;    // { b: true, foo: 'bar' }
html`<a ...${{ foo: 'bar' }} b />`;    // { b: true, foo: 'bar' }
html`<a x="1" ...${extras} />`;        // { x: "1", ...extras }
```

Multiple spreads in one element:

```js
html`<a ...${baseProps} ...${overrideProps} />`;
```

htm does not mutate spread variables — the original object is never modified.

## Children Syntax

### Text Content

Plain text between tags becomes children:

```js
html`<p>Hello world</p>`;  // children: ['Hello world']
```

### Dynamic Content

Interpolated values become children alongside text:

```js
const name = 'Alice';
html`<p>Hello, ${name}!</p>`;  // children: ['Hello, ', 'Alice', '!']
```

### Nested Elements

```js
html`<div><span>Nested</span></div>`;
```

### Mixed Content

Text, dynamic values, and elements can be mixed freely:

```js
html`
  <div>
    Before
    ${dynamicValue}
    <span>Middle</span>
    ${anotherValue}
    After
  </div>
`;
// children: ['Before', dynamicValue, <span>, anotherValue, 'After']
```

### Multiple Root Elements

When the template has multiple top-level elements, htm returns an array:

```js
html`<h1>Title</h1><p>Paragraph</p>`;
// Returns [VNode(h1), VNode(p)]
```

Single root elements return a single VNode (not wrapped in an array).

## Whitespace Handling

htm trims leading and trailing whitespace/newlines from text content:

```js
html`
  <div>
    Hello
  </div>
`;
// Text content is "Hello" (surrounding whitespace stripped)
```

This matches JSX behavior and prevents unwanted whitespace nodes.

## Special Characters and Edge Cases

### Hyphens in Attribute Names

Hyphens are allowed in attribute names (for custom data attributes, etc.):

```js
html`<div data-value="test" aria-label=hello></div>`;
```

### Forward Slashes

A `/` followed by `>` always self-closes the element:

```js
html`<div prop=value/>`;     // Self-closes, prop: "value"
html`<div prop=val/ue>`;     // "val/ue" is a valid value (not followed by >)
html`<div prop=value/ >`;    // prop: "value/" (slash before space, not before >)
```

A `/` in the middle of a tag name self-closes the element at that point:

```js
html`<ab/ba prop=value>`;    // Tag is "ab", self-closed. "ba" is ignored.
```

### HTML Comments

Comments are parsed and ignored (not rendered):

```js
html`<div><!-- This is a comment --></div>`;  // children: []
html`<a><!-- Hello,\nworld! --></a>`;          // Multi-line comments work too
```

## Empty Templates

An empty template returns `undefined`:

```js
html``;  // undefined
```

## Non-Element Roots

Templates without any tags return the raw content:

```js
html`foo`;           // "foo"
html`${1}`;          // 1
html`foo${1}bar`;    // ["foo", 1, "bar"]
```
