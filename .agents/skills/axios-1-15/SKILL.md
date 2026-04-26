---
name: axios-1-15
description: A comprehensive toolkit for making HTTP requests using Axios 1.x, a promise-based HTTP client for browser and Node.js environments. Use when building applications that require REST API communication, file uploads/downloads, request/response interception, custom headers, authentication, form data handling, progress tracking, or advanced features like rate limiting and HTTP/2 support.
version: "1.15.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - http
  - rest
  - api
  - fetch
  - ajax
  - promises
  - nodejs
  - browser
category: development
external_references:
  - https://axios-http.com/
  - https://github.com/axios/axios
---

# Axios 1.x

## Overview

Axios is a promise-based HTTP client for the browser and Node.js. It provides a simple, consistent API for making HTTP requests across environments — using `XMLHttpRequest` in browsers, the native `http`/`https` modules in Node.js, and optionally the Fetch API. It supports interceptors, automatic JSON handling, form serialization, request cancellation, progress tracking, and TypeScript out of the box.

Key characteristics:

- **Isomorphic** — same API works in browser and Node.js
- **Promise-based** — full support for `async/await` and `.then()` chains
- **Interceptor system** — middleware-like hooks for request/response lifecycle
- **Automatic serialization** — JSON, `multipart/form-data`, and `x-www-form-urlencoded`
- **Progress capturing** — upload/download progress with speed and ETA (browser + Node.js)
- **Rate limiting** — bandwidth capping in Node.js via `maxRate`
- **Fetch adapter** — optional first-class Fetch API support (v1.7.0+)
- **HTTP/2** — experimental support in Node.js (v1.13.0+)

## When to Use

- Making REST API calls from frontend or backend JavaScript code
- Building isomorphic/universal applications that share HTTP logic between browser and server
- Needing request/response interceptors for auth tokens, logging, or error handling
- Uploading files with progress tracking
- Requiring automatic form data serialization (`FormData`, `URLSearchParams`)
- Implementing retry logic, token refresh, or rate limiting
- Working in environments that need the Fetch adapter (Cloudflare Workers, Deno, Tauri, SvelteKit)

## Core Concepts

### Making Requests

Every axios request returns a standard ES6 Promise. The recommended approach is `async/await`:

```js
import axios from "axios";

const { data } = await axios.get("https://api.example.com/users/1");
console.log(data);
```

All common HTTP methods have convenience aliases:

- `axios.get(url[, config])`
- `axios.post(url[, data[, config]])`
- `axios.put(url[, data[, config]])`
- `axios.patch(url[, data[, config]])`
- `axios.delete(url[, config])`
- `axios.head(url[, config])`
- `axios.options(url[, config])`
- `axios.request(config)` — explicit method in config

### Response Object

Every resolved request returns a response with this shape:

```js
{
  data: {},         // Response body (parsed JSON by default)
  status: 200,      // HTTP status code
  statusText: "OK", // HTTP status text
  headers: {},      // Response headers (AxiosHeaders instance, lower-cased keys)
  config: {},       // The full config used for this request
  request: {}       // Underlying request object (XMLHttpRequest or http.ClientRequest)
}
```

Destructure what you need:

```js
const { data, status, headers } = await axios.get("/api/users/1");
```

### Creating Instances

`axios.create()` produces a pre-configured instance — the recommended pattern for any application beyond a single file:

```js
const api = axios.create({
  baseURL: "https://api.example.com",
  timeout: 5000,
  headers: { "X-App-Version": "2.0.0" },
});

const { data } = await api.get("/users/1");
```

Instances support isolated interceptors, per-service base URLs, and independent timeouts. Request-time config always overrides instance defaults.

### Config Precedence

Config is merged in this order (later values override earlier):

1. Library defaults (`lib/defaults/index.js`)
2. Instance defaults (`axios.create({ ... })` or `instance.defaults`)
3. Request-time config (`api.get("/path", { ... })`)

### Parallel Requests

Use standard `Promise.all` for concurrent requests:

```js
const [users, posts] = await Promise.all([
  axios.get("/api/users"),
  axios.get("/api/posts"),
]);
```

Use `Promise.allSettled` to handle partial failures:

```js
const results = await Promise.allSettled([
  axios.get("/api/users"),
  axios.get("/api/posts"),
]);
```

## Installation / Setup

### Package Managers

```bash
npm install axios
# or
pnpm add axios
# or
yarn add axios
# or
bun add axios
```

### Deno

```bash
deno install npm:axios
```

### CDN

Pin the version in production to avoid unexpected changes:

```html
<!-- jsDelivr -->
<script src="https://cdn.jsdelivr.net/npm/axios@1.13.2/dist/axios.min.js"></script>

<!-- unpkg -->
<script src="https://unpkg.com/axios@1.13.2/dist/axios.min.js"></script>
```

### Importing

ES modules (recommended):

```js
import axios from "axios";
// Named exports are available:
import axios, { isCancel, AxiosError, AxiosHeaders } from "axios";
```

CommonJS:

```js
const axios = require("axios");
```

For legacy bundlers that struggle with dual ESM/CJS packages:

```js
import { default as axios } from "axios";
// or
const axios = require("axios/dist/browser/axios.cjs"); // browser ES2017 bundle
// const axios = require("axios/dist/node/axios.cjs");   // node ES2017 bundle
```

## Usage Examples

### Basic GET with query parameters

```js
const { data } = await axios.get("/users", {
  params: { page: 1, limit: 10 },
});
```

### POST with JSON body

```js
const { data } = await axios.post("/users", {
  name: "Jane",
  email: "jane@example.com",
});
```

### Custom timeout and headers

```js
const { data } = await axios.get("/slow-endpoint", {
  timeout: 30000,
  headers: { "Accept-Language": "en-US" },
});
```

### Response validation override

By default, only 2xx status codes resolve the promise. Override with `validateStatus`:

```js
const { data } = await axios.get("/api/resource", {
  validateStatus: (status) => status < 500, // resolve for anything below 500
});
```

### Stream response (Node.js)

```js
import fs from "fs";

const { data } = await axios.get("https://example.com/image.jpg", {
  responseType: "stream",
});

data.pipe(fs.createWriteStream("image.jpg"));
```

## Advanced Topics

**Request Config**: All config options including `transformRequest`, `paramsSerializer`, proxy, and socket paths → [Request Config](reference/01-request-config.md)

**Interceptors & Authentication**: Request/response interceptors, Bearer tokens, HTTP Basic auth, API keys, token refresh patterns → [Interceptors & Authentication](reference/02-interceptors-authentication.md)

**Error Handling & Retry**: AxiosError types, error codes, cancellation with AbortController, retry strategies with exponential backoff → [Error Handling & Retry](reference/03-error-handling-retry.md)

**Forms, Files & Progress**: `multipart/form-data`, `x-www-form-urlencoded`, file uploads, progress capturing, rate limiting → [Forms, Files & Progress](reference/04-forms-files-progress.md)

**Adapters & Advanced Features**: Built-in adapters (xhr, http, fetch), custom adapters, Fetch adapter, HTTP/2, testing with MockAdapter, TypeScript support → [Adapters & Advanced Features](reference/05-adapters-advanced.md)
