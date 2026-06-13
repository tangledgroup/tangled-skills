# Community Extensions: Data Encoding and Templates

Extensions for JSON encoding, client-side templating, and structured data handling.

## json-enc

Encode request parameters as JSON instead of URL-encoded form data.

### Installation
```html
<script src="https://unpkg.com/htmx-ext-json-enc@2.0.0/json-enc.js"></script>
```

### Usage
```html
<form hx-post="/api/items"
      hx-ext="json-enc"
      hx-encoding="application/json">
  <input name="name" value="Widget" />
  <input name="price" value="9.99" />
  <button type="submit">Create</button>
</form>
```

Sends body as: `{"name":"Widget","price":"9.99"}`

> Note: All values are strings. Use `form-json` for type preservation.

---

## form-json

Like json-enc but with **type preservation**. Converts form data into structured JSON while maintaining correct types for numbers, booleans, and files (Base64-encoded).

### Installation
```html
<script src="https://unpkg.com/htmx-ext-form-json@1.0.0/form-json.js"></script>
```

### Usage
```html
<form hx-post="/api/items"
      hx-ext="form-json"
      hx-encoding="application/json">
  <input name="name" value="Widget" />
  <input name="price" value="9.99" />
  <input name="active" value="true" />
  <button type="submit">Create</button>
</form>
```

Sends: `{"name":"Widget","price":9.99,"active":true}`

### Nested Structures

Supports dot notation and bracket notation for nested objects:

```html
<input name="user.name" value="John" />
<input name="user.age" value="30" />
<input name="tags[0]" value="htmx" />
<input name="tags[1]" value="web" />
```

Sends: `{"user":{"name":"John","age":30},"tags":["htmx","web"]}`

---

## json-enc-custom

Extended JSON encoding supporting complex structures via name attributes alone.

### Installation
```html
<script src="https://unpkg.com/htmx-ext-json-enc-custom@1.0.0/json-enc-custom.js"></script>
```

### Usage
```html
<form hx-post="/api"
      hx-ext="json-enc-custom"
      hx-encoding="application/json">
  <input name="items[0].name" value="Widget A" />
  <input name="items[0].price" value="10" />
  <input name="items[1].name" value="Widget B" />
  <input name="items[1].price" value="20" />
</form>
```

Sends: `{"items":[{"name":"Widget A","price":10},{"name":"Widget B","price":20}]}`

Supports embedding JSON objects, lists, and handling indexes purely through name attributes.

---

## client-side-templates

Transform JSON/XML responses into HTML using client-side templates before swapping.

### Installation
```html
<script src="https://unpkg.com/htmx-ext-client-side-templates@2.0.0/client-side-templates.js"></script>
```

### Supported Template Engines

| Engine | Package |
|--------|---------|
| Mustache | `mustache` |
| Nunjucks | `nunjucks` |
| Handlebars | `handlebars` |
| EJS | `ejs` |
| Eta | `eta` |

### Usage with Mustache

```html
<script src="https://cdn.jsdelivr.net/npm/mustache@4"></script>
<script src="https://unpkg.com/htmx-ext-client-side-templates@2.0.0/client-side-templates.js"></script>

<div hx-ext="client-side-templates"
     hx-get="/api/items.json"
     hx-swap="innerHTML"
     hx-select-template="item-template">
</div>

<template id="item-template">
  {{#items}}
  <div class="item">
    <h3>{{name}}</h3>
    <p>${{price}}</p>
  </div>
  {{/items}}
</template>
```

### Template Selection

```html
<!-- Use template by ID -->
<div hx-get="/api/data.json" hx-select-template="my-template"></div>

<!-- Use first <template> in response -->
<div hx-get="/api/data.json" hx-select-template="first"></div>
```

### When to Use

- Server returns JSON, not HTML
- Need client-side rendering with template engine
- Building API-driven interfaces without a full SPA framework

---

## htmx-json

Support JSON responses by transforming HTML directly. Different approach than client-side-templates — transforms the HTML response itself.

### Installation
```html
<script src="https://unpkg.com/htmx-json@1.0.0/htmx-json.js"></script>
```

### Usage
```html
<div hx-ext="htmx-json"
     hx-get="/api/data.json"
     hx-swap="innerHTML">
</div>
```

Simpler than client-side-templates for basic JSON-to-HTML conversion.
