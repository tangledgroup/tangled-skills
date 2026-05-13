# Request Options (RequestInit)

## Contents
- Overview
- method
- body
- headers
- credentials
- mode
- cache
- redirect
- signal
- keepalive
- integrity
- duplex
- referrerPolicy
- priority
- Deferred Fetch (fetchLater)

## Overview

The `RequestInit` dictionary configures fetch requests. Pass it as the second argument to `fetch()` or to the `Request()` constructor. When passing options to both `Request()` and `fetch()`, the value passed directly to `fetch()` takes precedence for overlapping properties.

```js
const response = await fetch(url, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ key: "value" }),
});
```

## method

The HTTP request method. Defaults to `GET`.

```js
// Common methods
await fetch(url, { method: "GET" });
await fetch(url, { method: "POST" });
await fetch(url, { method: "PUT" });
await fetch(url, { method: "DELETE" });
```

When `mode` is set to `no-cors`, method must be one of `GET`, `HEAD`, or `POST`.

## body

The request payload. Cannot be used with `GET` requests. Supported types:

- `string` — plain text
- `ArrayBuffer` / `TypedArray` / `DataView` — binary data
- `Blob` / `File` — file uploads
- `FormData` — form data (multipart/form-encoded)
- `URLSearchParams` — URL-encoded form data
- `ReadableStream` — streaming body (requires `duplex: "half"`)

```js
// JSON body
await fetch(url, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ name: "example" }),
});

// Form data
const formData = new FormData();
formData.append("name", "example");
await fetch(url, { method: "POST", body: formData });

// URL-encoded data
const params = new URLSearchParams({ name: "example" });
await fetch(url, {
  method: "POST",
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body: params,
});
```

**Body is a stream**: Once consumed, the body cannot be read again. Use `request.clone()` before sending if you need to reuse it:

```js
const request1 = new Request(url, { method: "POST", body: data });
const request2 = request1.clone();
await fetch(request1);
await fetch(request2); // Works because cloned
```

## headers

Request headers as an object literal or `Headers` instance. The `Headers` object provides input sanitization: normalizes names to lowercase, strips whitespace, and blocks forbidden headers.

```js
// Object literal
await fetch(url, {
  headers: {
    "Content-Type": "application/json",
    "Authorization": "Bearer token",
  },
});

// Headers instance
const myHeaders = new Headers();
myHeaders.append("Content-Type", "application/json");
await fetch(url, { headers: myHeaders });
```

Many headers are set automatically by the browser and cannot be overridden (forbidden request headers). When `mode` is `no-cors`, only CORS-safelisted request headers are allowed.

## credentials

Controls whether cookies, TLS client certificates, and authentication headers are sent. Defaults to `same-origin`.

| Value | Behavior |
|---|---|
| `omit` | Never send or receive credentials |
| `same-origin` | Only for same-origin requests (default) |
| `include` | Always include, even cross-origin |

```js
// Cross-origin with cookies
await fetch("https://api.example.com/data", {
  credentials: "include",
});
```

When using `credentials: "include"` cross-origin, the server must respond with `Access-Control-Allow-Credentials: true` and specify the exact origin in `Access-Control-Allow-Origin` (wildcard `*` is not allowed).

## mode

Controls cross-origin behavior. Defaults to `cors`.

| Value | Behavior |
|---|---|
| `cors` | Uses CORS for cross-origin requests (default) |
| `same-origin` | Disallows cross-origin requests entirely |
| `no-cors` | Disables CORS; response is opaque (status 0, no headers/body accessible) |
| `navigate` | Used only by HTML navigation between documents |

```js
// Force same-origin only
await fetch(url, { mode: "same-origin" });
```

## cache

Controls HTTP cache behavior.

| Value | Behavior |
|---|---|
| `default` | Use cache if fresh; conditional request if stale; normal request if no match |
| `no-store` | Bypass cache entirely, do not update |
| `reload` | Bypass cache, update with new response |
| `no-cache` | Conditional request for any cached entry (fresh or stale) |
| `force-cache` | Use cache even if stale; only fetch if no match |
| `only-if-cached` | Use cache only; network error if no match (requires `same-origin` mode) |

```js
// Force fresh data from server
await fetch(url, { cache: "reload" });

// Offline-friendly: use cache or fail
await fetch(url, { cache: "only-if-cached", mode: "same-origin" });
```

## redirect

Controls redirect handling. Defaults to `follow`.

| Value | Behavior |
|---|---|
| `follow` | Automatically follow redirects (default) |
| `error` | Reject with network error on redirect |
| `manual` | Return opaque response for service worker replay |

```js
// Fail if server redirects
await fetch(url, { redirect: "error" });
```

## signal

An `AbortSignal` from an `AbortController` to cancel the request.

```js
const controller = new AbortController();
const response = await fetch(url, { signal: controller.signal });
controller.abort(); // Rejects with AbortError
```

The signal also cancels response body consumption. If aborted after `fetch()` resolves but before the body is read, reading the body rejects with `AbortError`.

## keepalive

When `true`, the request continues even if the page unloads. Useful for sending analytics or final data when the user navigates away. Body size limited to 64 KiB.

```js
await fetch("/analytics", {
  method: "POST",
  body: JSON.stringify({ event: "page_exit" }),
  keepalive: true,
});
```

## integrity

Subresource integrity (SRI) hash to verify the fetched resource. Format: `<algorithm>-<base64-hash>`.

```js
await fetch(url, {
  integrity: "sha256-BpfBw7ivV8q2jLiT13fxDYAe2tJllusRSZ273h2nFSE=",
});
```

Supported algorithms: `sha256`, `sha384`, `sha512`. If the hash does not match, the request fails with a network error.

## duplex

Controls duplex behavior. Must be `half` (browser sends entire request before processing response). Required when `body` is a `ReadableStream`.

```js
const stream = new ReadableStream({ /* ... */ });
await fetch(url, {
  method: "POST",
  body: stream,
  duplex: "half",
});
```

## referrerPolicy

Sets the policy for the `Referer` header. Same values as the `Referrer-Policy` HTTP header.

```js
await fetch(url, {
  referrerPolicy: "no-referrer",
});
```

Common values: `no-referrer`, `origin`, `origin-when-cross-origin`, `same-origin`, `strict-origin`, `strict-origin-when-cross-origin`, `unsafe-url`.

## priority

Specifies request priority relative to other requests of the same type.

| Value | Behavior |
|---|---|
| `auto` | No preference (default) |
| `high` | High priority |
| `low` | Low priority |

```js
// Deprioritize non-critical data
await fetch(url, { priority: "low" });
```

## Deferred Fetch (fetchLater)

The `fetchLater()` method defers a request until the page navigates away or an `activateAfter` timeout elapses. Returns a `FetchLaterResult` with an `activated` boolean. The actual response is ignored.

```js
try {
  const result = fetchLater("/analytics", {
    method: "POST",
    body: JSON.stringify({ event: "view" }),
    activateAfter: 60000, // 1 minute timeout
  });

  console.log(result.activated); // true if already sent
} catch (e) {
  if (e instanceof QuotaExceededError) {
    // Handle quota exceeded
  }
}
```

Constraints: body cannot be a `ReadableStream`, URL must be trustworthy (HTTPS), and quotas apply per origin. Catch `QuotaExceededError` defensively.
