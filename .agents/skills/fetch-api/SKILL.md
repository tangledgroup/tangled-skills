---
name: fetch-api
description: JavaScript Fetch API for making HTTP requests from browsers and workers using promise-based fetch(). Covers Request/Response/Headers interfaces, body handling (JSON/text/blob/streaming), abort signals, CORS modes, credentials, caching, and deferred fetch. Use when building web applications that need to communicate with servers, load data via AJAX, upload files, cancel in-flight requests, or work with cross-origin resources.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - fetch
  - http
  - javascript
  - web-api
  - browser
  - xhr-alternative
category: web-framework
external_references:
  - https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
  - https://developer.mozilla.org/en-US/docs/Web/API/Window/fetch
  - https://fetch.spec.whatwg.org/
---

# Fetch API

## Overview

The Fetch API provides a JavaScript interface for fetching resources across the network. It is the modern replacement for `XMLHttpRequest`, using promises instead of callbacks and integrating with service workers and CORS. The global `fetch()` method is available in both `Window` and `Worker` contexts.

Core interfaces:

- **`fetch()`** — Global method that starts a network request, returning a promise that resolves to a `Response`.
- **`Request`** — Represents a resource request with properties for method, headers, body, credentials, and more.
- **`Response`** — Represents the server's response with status, headers, and body content accessible via methods like `json()`, `text()`, `blob()`.
- **`Headers`** — Manipulates HTTP request/response headers with methods for getting, setting, appending, and deleting.

The WHATWG Fetch Standard defines the unified architecture used by all web platform fetching features, including HTML elements, CSS, and JavaScript APIs.

## When to Use

- Making HTTP requests (GET, POST, PUT, DELETE) from browser or worker code
- Loading JSON data from APIs
- Uploading files or form data to servers
- Streaming large responses incrementally
- Canceling in-flight requests with `AbortController`
- Working with cross-origin resources and CORS
- Implementing cache-first strategies with service workers
- Sending deferred analytics/beacon requests with `fetchLater()`

## Core Concepts

### Basic Request Pattern

The standard pattern: call `fetch()`, check `response.ok`, read the body.

```js
async function getData(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP error! Status: ${response.status}`);
  }
  return response.json();
}
```

`fetch()` rejects only on network errors (bad URL, no connectivity). HTTP error statuses (404, 500) resolve normally — always check `response.ok` or `response.status`.

### Request Options

Pass an options object as the second argument to configure the request:

```js
const response = await fetch("https://api.example.com/data", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ key: "value" }),
});
```

### Response Body Methods

Read the response body in the format you need. Each method returns a promise and can only be called once (the body stream is consumed):

| Method | Returns |
|---|---|
| `response.json()` | Parsed JSON object |
| `response.text()` | Plain text string |
| `response.blob()` | Binary blob (images, files) |
| `response.arrayBuffer()` | Raw ArrayBuffer |
| `response.formData()` | Parsed FormData |

To read the body multiple times, clone first: `const clone = response.clone()`.

### Canceling Requests

Use `AbortController` to cancel in-flight requests:

```js
const controller = new AbortController();
const response = await fetch(url, { signal: controller.signal });
// Later:
controller.abort(); // Rejects with AbortError
```

### Streaming Large Responses

Access `response.body` as a `ReadableStream` to process content incrementally:

```js
const stream = response.body.pipeThrough(new TextDecoderStream());
for await (const chunk of stream) {
  console.log(chunk);
}
```

## Usage Examples

### GET with JSON Response

```js
async function fetchProducts() {
  const response = await fetch("https://api.example.com/products");
  if (!response.ok) throw new Error(`Status: ${response.status}`);
  return response.json();
}
```

### POST with JSON Body

```js
async function createProduct(product) {
  const response = await fetch("https://api.example.com/products", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(product),
  });
  if (!response.ok) throw new Error(`Status: ${response.status}`);
  return response.json();
}
```

### File Upload with FormData

```js
async function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("https://api.example.com/upload", {
    method: "POST",
    body: formData,
  });
  if (!response.ok) throw new Error(`Status: ${response.status}`);
  return response.json();
}
```

### Fetch with Timeout

```js
async function fetchWithTimeout(url, timeoutMs) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, { signal: controller.signal });
    if (!response.ok) throw new Error(`Status: ${response.status}`);
    return response.json();
  } finally {
    clearTimeout(timeout);
  }
}
```

### Image Fetch and Display

```js
async function loadImage(imgElement, url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Status: ${response.status}`);
  const blob = await response.blob();
  imgElement.src = URL.createObjectURL(blob);
}
```

## Advanced Topics

**Request Options**: All `RequestInit` properties including credentials, mode, cache, redirect, keepalive, integrity, duplex, referrerPolicy → [Request Options](reference/01-request-options.md)

**Response Handling**: Status checking, body methods, streaming with ReadableStream, clone pattern, locked/disturbed streams → [Response Handling](reference/02-response-handling.md)

**CORS and Security**: Cross-origin modes (cors/same-origin/no-cors), credentials handling, opaque responses, forbidden headers, preflighted requests → [CORS and Security](reference/03-cors-and-security.md)
