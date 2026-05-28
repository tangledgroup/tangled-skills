# Core Extension: htmx-1-compat

Rolls back most behavioral changes from htmx 2 to htmx 1 defaults. Use this extension to upgrade to htmx 2 with minimal breaking changes, then gradually migrate.

### Installation

```html
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/htmx-ext-htmx-1-compat@2.0.2"></script>
<body hx-ext="htmx-1-compat">
```

Or via npm: `npm install htmx-ext-htmx-1-compat`

### What It Restores

**Obsolete attributes:**
- `hx-ws` — restored in favor of `ws-connect`/`ws-send` (use ws extension instead)
- `hx-sse` — restored in favor of `sse-connect`/`sse-swap` (use sse extension instead)
- `hx-on` — restored in favor of `hx-on*` wildcard attribute

**Default changes reverted:**
- `htmx.config.scrollBehavior` → `"smooth"` (htmx 2 default is `"instant"`)
- `DELETE` requests use form-encoded body (htmx 2 uses URL params per RFC 9110)
- Cross-domain requests allowed by default (htmx 2 forbids them; set `selfRequestsOnly: false` manually instead)

### What It Does NOT Cover

This extension does not restore every htmx 1 behavior. Some breaking changes in htmx 2 require manual migration. Consult the [htmx 1.x to 2.x migration guide](https://v2-0v2-0.htmx.org/migration-guide-htmx-1/) for full details.

### Migration Strategy

1. Install `htmx-1-compat` to get immediate compatibility
2. Replace `hx-ws` → `ws-connect`/`ws-send` + ws extension
3. Replace `hx-sse` → `sse-connect`/`sse-swap` + sse extension
4. Replace `hx-on` → `hx-on::*` wildcard syntax
5. Review DELETE request behavior (URL params vs body)
6. Remove `htmx-1-compat` once all migration is complete
