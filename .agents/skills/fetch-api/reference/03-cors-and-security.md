# CORS and Security

## Contents
- Overview
- Cross-Origin Modes
- Simple vs Preflighted Requests
- Credentials in Cross-Origin Requests
- Opaque Responses
- Forbidden Headers
- CORS-Safelisted Headers
- Content Security Policy

## Overview

Cross-Origin Resource Sharing (CORS) controls how resources on one origin can be accessed from another. The Fetch API's `mode` option determines the CORS behavior for each request. Understanding CORS is essential for building applications that communicate with APIs on different domains.

An **origin** is the combination of scheme, host, and port (e.g., `https://example.com:443`). Two URLs have the same origin if all three components match.

## Cross-Origin Modes

The `mode` option in `RequestInit` controls cross-origin behavior:

### cors (default)

Uses the CORS mechanism for cross-origin requests. The server must respond with appropriate CORS headers, or the browser blocks the response from JavaScript.

```js
// Default mode — works if server sends CORS headers
const response = await fetch("https://api.other-domain.com/data");
```

For **simple requests** (GET/HEAD/POST with safelisted headers), the request is always sent. The server must respond with `Access-Control-Allow-Origin` or the browser blocks the response.

For **non-simple requests**, the browser sends an OPTIONS preflight request first. The real request is only sent if the preflight succeeds with appropriate CORS headers.

### same-origin

Disallows cross-origin requests entirely. Results in a network error if the URL has a different origin.

```js
await fetch(url, { mode: "same-origin" });
// Network error if url is cross-origin
```

### no-cors

Disables CORS for cross-origin requests. The response is **opaque** — status is 0, headers and body are not accessible to JavaScript. Restrictions:

- Method limited to `HEAD`, `GET`, or `POST`
- Only CORS-safelisted request headers allowed (no `Range` header)
- Response cannot be read by JavaScript

Primary use case: service workers can cache opaque responses and serve them as responses to intercepted fetch requests, even though the response content is not readable.

```js
// Service worker: cache opaque response for later
await fetch("https://third-party.com/resource", { mode: "no-cors" });
```

## Simple vs Preflighted Requests

**Simple requests** bypass the preflight step and are sent directly. A request is simple if:

- Method is `GET`, `HEAD`, or `POST`
- Headers are limited to CORS-safelisted headers
- Body (for POST) is one of: `application/x-www-form-urlencoded`, `multipart/form-data`, or `text/plain`

**Preflighted requests** require an OPTIONS request before the actual request. Triggers:

- Method other than `GET`, `HEAD`, or `POST`
- Non-safelisted headers (e.g., custom `X-API-Key`)
- POST with `Content-Type: application/json`

```js
// Simple request — no preflight
await fetch("https://api.example.com/data", {
  method: "POST",
  body: new URLSearchParams({ key: "value" }),
});

// Preflighted request — OPTIONS sent first
await fetch("https://api.example.com/data", {
  method: "PUT",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ key: "value" }),
});
```

## Credentials in Cross-Origin Requests

By default, credentials (cookies, TLS certificates, auth headers) are only sent for same-origin requests. Use the `credentials` option to change this:

```js
// Send cookies cross-origin
const response = await fetch("https://api.example.com/data", {
  credentials: "include",
});
```

When using `credentials: "include"` cross-origin, the server must respond with:

1. `Access-Control-Allow-Credentials: true`
2. `Access-Control-Allow-Origin` set to the exact client origin (not `*`)

If these headers are missing, the browser returns a network error even if the server sends a valid response.

**CSRF protection**: Including credentials in cross-origin requests can expose sites to CSRF attacks. The `credentials: "include"` requirement that the server explicitly opt-in via `Access-Control-Allow-Credentials` is a security measure.

## Opaque Responses

When `mode` is `no-cors`, the response is opaque:

- `response.status` is always `0`
- `response.statusText` is empty
- `response.headers` is empty
- `response.body` is null
- `response.type` is `"opaque"` (or `"opaqueredirect"` if redirected)

Opaque responses cannot be read by JavaScript. They exist primarily for service workers, which can cache them and later use them as responses to intercepted requests:

```js
// Service worker
self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      return fetch(event.request, { mode: "no-cors" });
    })
  );
});
```

## Forbidden Headers

Some headers cannot be set by scripts because they are managed by the browser:

- `Accept-Charset`
- `Accept-Encoding`
- `Access-Control-Request-Headers`
- `Access-Control-Request-Method`
- `Connection`
- `Content-Length`
- `Cookie` / `Cookie2`
- `Date`
- `DNT`
- `Expect`
- `Host`
- `Keep-Alive`
- `Origin`
- `Referer`
- `TE`
- `Trailer`
- `Transfer-Encoding`
- `Upgrade`
- `Via`

Attempting to set these via the `Headers` object or `RequestInit.headers` throws a `TypeError`.

When `mode` is `no-cors`, the allowed headers are further restricted to only CORS-safelisted request headers.

## CORS-Safelisted Headers

These headers are allowed even in `no-cors` mode and do not trigger preflight:

- `Accept`
- `Accept-Language`
- `Content-Language`
- `Content-Type` (limited to safelisted values)
- `DPR`
- `Downlink`
- `Save-Data`
- `Viewport-Width`
- `Width`

The `Headers` object automatically normalizes header names to lowercase and strips leading/trailing whitespace from values.

## Content Security Policy

The `fetch()` method is controlled by the `connect-src` CSP directive, not the directive of the resources being fetched. This means:

```
Content-Security-Policy: connect-src https://api.example.com
```

This allows `fetch()` calls to `https://api.example.com` regardless of what type of resource is being retrieved. If the URL does not match `connect-src`, the fetch fails with a security error.
