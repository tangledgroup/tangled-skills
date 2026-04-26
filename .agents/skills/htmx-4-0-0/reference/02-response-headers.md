# Response Headers

htmx processes special `HX-*` response headers to control client-side behavior after receiving a response. These allow the server to dynamically redirect, trigger events, retarget swaps, and modify URLs.

**Important:** Response headers are not processed on 3xx response codes. Return a 2xx status when using these headers.

In htmx 4.0, `400` and `500` responses are swapped by default (unlike htmx 2.x where they were not). Configure via `htmx.config.noSwap`.

## `HX-Trigger`

Triggers client-side JavaScript events when content is swapped.

```http
HX-Trigger: myEvent
```

Multiple events:
```http
HX-Trigger: event1, event2
```

Event with detail (JSON):
```http
HX-Trigger: {"showMessage":"Hello World"}
```

Handle on the client:
```javascript
document.body.addEventListener("showMessage", (evt) => {
  alert(evt.detail.value); // "Hello World"
});
```

Combine with `hx-trigger` to respond to server events:
```html
<div hx-trigger="showMessage from:body" hx-get="/message"></div>
```

## `HX-Redirect`

Redirects to a new URL with a **full page reload**. Use when redirecting to non-htmx endpoints or pages requiring full browser load.

```http
HX-Redirect: /dashboard
```

For AJAX navigation within your htmx app, use `HX-Location` instead.

## `HX-Location`

Performs an AJAX redirect — loads the new URL via htmx rather than a full page reload. The response from the new URL is swapped into the current page.

```http
HX-Location: /new-page
```

Accepts a JSON object for more control:
```http
HX-Location: {"path":"/new-page","source":"#main","eventTarget":"#main"}
```

## `HX-Retarget`

Overrides the element that receives swapped content, replacing whatever `hx-target` was set on the triggering element.

```http
HX-Retarget: #notifications
```

Value is a CSS selector for the new target element.

## `HX-Reswap`

Overrides the swap style used when inserting the response, replacing whatever `hx-swap` was set.

```http
HX-Reswap: outerHTML
```

Accepts same values as `hx-swap`, including modifiers:
```http
HX-Reswap: innerHTML transition:true
```

## `HX-Retarget` and `HX-Reswap` Together

Both can be used together to fully control where and how content is swapped from the server side.

## `HX-Push-Url`

Pushes a URL into the browser history (same as `hx-push-url` but from the server).

```http
HX-Push-Url: /account/home
```

Value of `false` prevents any URL push.

## `HX-Replace-Url`

Replaces the current URL in browser history (does not create a new entry, removes previous).

```http
HX-Replace-Url: /dashboard
```

Value of `false` prevents URL update. Overrides attribute-level behavior.

## `HX-Reselect`

Overrides the `hx-select` value for this response.

```http
HX-Reselect: #main-content
```

## `HX-Retarget` and `HX-Reswap` Notes

Both headers are evaluated after the response is received but before swapping occurs. They give the server full control over how responses are integrated into the DOM, enabling patterns where the client doesn't need to know swap details upfront.
