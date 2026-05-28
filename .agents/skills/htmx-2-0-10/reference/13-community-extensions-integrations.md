# Community Extensions: Third-Party Integrations

Extensions that integrate htmx with specific platforms and services.

## signalr

Bidirectional real-time communication via .NET SignalR.

### Installation
```html
<script src="https://unpkg.com/htmx-ext-signalr@1.0.0/signalr.js"></script>
```

Requires Microsoft SignalR JavaScript client:
```html
<script src="https://cdn.jsdelivr.net/npm/@microsoft/signalr@7/dist/browser/signalr.min.js"></script>
```

### Usage
```html
<div hx-ext="signalr"
     signalr-hub="/chatHub"
     signalr-send="SendMessage"
     signalr-receive="ReceiveMessage">
  <div id="messages"></div>
  <form signalr-send>
    <input name="message" />
    <button type="submit">Send</button>
  </form>
</div>
```

| Attribute | Description |
|-----------|-------------|
| `signalr-hub="<url>"` | SignalR hub endpoint URL |
| `signalr-send="<method>"` | Hub method to call when form submits |
| `signalr-receive="<method>"` | Hub method to listen for (swaps response) |

### Events

Fires `htmx:signalrOpen`, `htmx:signalrClose`, `htmx:signalrError` events analogous to WebSocket extension.

---

## amz-content-sha256

AWS content hash verification for services requiring SHA256 content digest in request headers.

### Installation
```html
<script src="https://unpkg.com/amz-content-sha256@1.0.0/amz-content-sha256.js"></script>
```

### Usage
```html
<form hx-post="/aws-endpoint"
      hx-ext="amz-content-sha256">
  <!-- Automatically adds x-amz-content-sha256 header -->
</form>
```

Computes SHA256 hash of request body and adds as `x-amz-content-sha256` header for AWS data integrity verification.

---

## hx-drag

Send htmx requests triggered by drag-and-drop operations.

### Installation
```bash
npm install hx-drag
```

### Usage
```html
<div hx-ext="hx-drag">
  <div hx-drag
       hx-post="/items/reorder"
       hx-include="#form"
       draggable="true">
    Draggable item
  </div>
</div>
```

Sends request on `drop` event with drag position data included in parameters.

---

## replace-params

Replace specific URL parameters instead of resetting all parameters. Useful for pagination and search filters.

### Installation
```html
<script src="https://unpkg.com/htmx-ext-replace-params@1.0.0/replace-params.js"></script>
```

### Usage
```html
<!-- Only replace 'page' param, keep other query params -->
<a href="/search?page=2"
   hx-get="/search"
   hx-ext="replace-params"
   replace-params="page">
  Next Page
</a>

<!-- Delete a parameter by setting empty value -->
<button replace-params="sort:">Clear Sort</button>
```

---

## Comparison Table

| Extension | Platform | Purpose |
|-----------|----------|---------|
| signalr | .NET/ASP.NET Core | Real-time bidirectional via SignalR hubs |
| amz-content-sha256 | AWS | Content hash for AWS API requests |
| hx-drag | Browser native | Drag-and-drop triggered htmx requests |
| replace-params | Any | Preserve query params, replace only specific ones |
