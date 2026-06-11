# Response Handling

## Contents
- Overview
- Response Properties
- Checking Status
- Response Types
- Reading the Body
- Streaming the Body
- Clone Pattern
- Locked and Disturbed Streams
- Static Methods

## Overview

The `Response` object represents the server's response to a request. The promise from `fetch()` resolves to a `Response` as soon as headers arrive — even before the body is fully downloaded. HTTP error statuses (4xx, 5xx) do not reject the promise; they resolve normally with status properties set accordingly.

## Response Properties

| Property | Type | Description |
|---|---|---|
| `response.ok` | boolean | `true` if status is 200-299 |
| `response.status` | number | HTTP status code (e.g., 200, 404) |
| `response.statusText` | string | Status text (e.g., "OK", "Not Found") |
| `response.type` | string | Response type (`basic`, `cors`, `opaque`, `opaqueredirect`) |
| `response.headers` | Headers | Response headers object |
| `response.url` | string | URL of the response |
| `response.redirected` | boolean | `true` if the response was redirected |
| `response.body` | ReadableStream | Raw body as a stream |
| `response.bodyUsed` | boolean | `true` if body has been consumed |

## Checking Status

Always check `response.ok` before reading the body. The standard pattern:

```js
const response = await fetch(url);
if (!response.ok) {
  throw new Error(`HTTP error! Status: ${response.status}`);
}
const data = await response.json();
```

For more granular handling:

```js
const response = await fetch(url);
switch (response.status) {
  case 200: return response.json();
  case 401: throw new Error("Unauthorized");
  case 404: throw new Error("Not found");
  case 429: throw new Error("Rate limited");
  default: throw new Error(`Unexpected status: ${response.status}`);
}
```

## Response Types

The `type` property determines what is accessible in the response:

| Type | When | Accessible Content |
|---|---|---|
| `basic` | Same-origin request | Full headers (except forbidden) and body |
| `cors` | Cross-origin CORS request | Only CORS-safelisted headers and body |
| `opaque` | Cross-origin with `no-cors` mode | Status 0, empty headers, null body |
| `opaqueredirect` | `redirect: "manual"` with redirect response | Same as opaque |

Opaque responses cannot be read by JavaScript — they are primarily used for service worker caching.

## Reading the Body

Each body method returns a promise and consumes the stream. Only one can be called per response:

```js
// JSON
const data = await response.json();

// Plain text
const text = await response.text();

// Binary (images, files)
const blob = await response.blob();

// Raw bytes
const buffer = await response.arrayBuffer();

// Parsed form data
const formData = await response.formData();
```

The method throws if the content cannot be parsed in the expected format (e.g., calling `json()` on non-JSON content).

Check content type before parsing:

```js
const contentType = response.headers.get("content-type");
if (contentType && contentType.includes("application/json")) {
  return response.json();
}
throw new TypeError("Expected JSON response");
```

## Streaming the Body

Access `response.body` as a `ReadableStream` to process large responses incrementally without buffering the entire body in memory:

```js
const response = await fetch(url);
if (!response.ok) throw new Error(`Status: ${response.status}`);

// Stream text chunks
const stream = response.body.pipeThrough(new TextDecoderStream());
for await (const chunk of stream) {
  console.log(chunk);
}
```

**Line-by-line processing**:

```js
async function* makeTextFileLineIterator(fileURL) {
  const response = await fetch(fileURL);
  const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();

  let { value: chunk = "", done: readerDone } = await reader.read();
  const newline = /\r?\n/g;
  let startIndex = 0;

  while (true) {
    const result = newline.exec(chunk);
    if (!result) {
      if (readerDone) break;
      const remainder = chunk.slice(startIndex);
      ({ value: chunk, done: readerDone } = await reader.read());
      chunk = remainder + (chunk || "");
      startIndex = newline.lastIndex = 0;
      continue;
    }
    yield chunk.substring(startIndex, result.index);
    startIndex = newline.lastIndex;
  }

  if (startIndex < chunk.length) {
    yield chunk.substring(startIndex);
  }
}

// Usage
for await (const line of makeTextFileLineIterator(url)) {
  processLine(line);
}
```

## Clone Pattern

When you need to read the body more than once, clone the response before consuming:

```js
const response = await fetch(url);
if (!response.ok) throw new Error(`Status: ${response.status}`);

const responseClone = response.clone();

// Read twice independently
const json1 = await response.json();
const json2 = await responseClone.json();
```

**Service worker cache pattern**: Return the original response to the app, cache the clone:

```js
async function cacheFirst(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) return cachedResponse;

  const networkResponse = await fetch(request);
  if (networkResponse.ok) {
    const cache = await caches.open("MyCache_1");
    cache.put(request, networkResponse.clone());
  }
  return networkResponse;
}

self.addEventListener("fetch", (event) => {
  event.respondWith(cacheFirst(event.request));
});
```

## Locked and Disturbed Streams

Body streams have two states that prevent re-reading:

- **Locked**: A reader is attached via `ReadableStream.getReader()`. Nothing else can read the stream.
- **Disturbed**: Any content has been read from the stream. The stream cannot be re-read.

This means calling any body method twice throws:

```js
const response = await fetch(url);
const result1 = await response.json();
const result2 = await response.json(); // Throws: "Body already consumed"
```

Use `response.clone()` to get an independent copy before reading, or check `response.bodyUsed` to see if the body has been consumed.

## Static Methods

Create synthetic responses without making network requests:

```js
// Network error response
Response.error();

// Redirect response
Response.redirect("/new-url", 302);

// JSON response (useful in service workers)
Response.json({ status: "ok" }, {
  status: 200,
  headers: { "Content-Type": "application/json" },
});
```

The `Response()` constructor also allows creating custom responses for testing or service worker interception.
