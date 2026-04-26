---
name: axios-1-15
description: A comprehensive toolkit for making HTTP requests using Axios 1.x, a promise-based HTTP client for browser and Node.js environments. Use when building applications that require REST API communication, file uploads/downloads, request/response interception, custom headers, authentication, form data handling, progress tracking, or advanced features like rate limiting and HTTP/2 support.
version: "0.3.0"
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

# Axios 1.15

## Overview

Axios is a promise-based HTTP client for the browser and Node.js. It provides a simple API for making HTTP requests with support for interceptors, automatic JSON transformation, request cancellation, progress capturing, and TypeScript definitions. It works in all modern browsers and Node.js environments as far back as v12.x, plus Bun and Deno.

Key features:

- Isomorphic — same API in browser and Node.js
- Promise-based with async/await support
- Request and response interceptors
- Automatic JSON data transformation
- Client-side protection against XSRF
- Progress capturing for uploads and downloads (with speed rate, remaining time)
- Request cancellation via AbortController
- Automatic form serialization to JSON, FormData, and URL-encoded formats
- HTML form posting as JSON or multipart/form-data
- Bandwidth rate limiting (Node.js)
- Experimental HTTP/2 support (Node.js, v1.13.0+)
- Fetch adapter alongside xhr and http adapters
- Full TypeScript support with built-in type definitions

## When to Use

- Making REST API calls from browser or Node.js applications
- Building HTTP client wrappers with shared configuration
- Implementing authentication flows (Bearer tokens, HTTP Basic, API keys, cookie-based)
- Handling file uploads and downloads with progress tracking
- Adding retry logic, exponential backoff, or rate-limit handling via interceptors
- Testing code that makes HTTP requests (with mock adapters)
- Working with multipart/form-data or URL-encoded form submissions
- Rate-limiting bandwidth for bulk operations in Node.js

## Core Concepts

**Promise-based API**: Every axios request returns a Promise that resolves to a response object or rejects with an AxiosError. Use async/await or .then/.catch chains.

**Response object shape**: Every successful request resolves to:

```js
{
  data: {},          // Response body (auto-parsed as JSON when applicable)
  status: 200,       // HTTP status code
  statusText: "OK",  // HTTP status text
  headers: {},       // Response headers (lower-cased keys, AxiosHeaders instance)
  config: {},        // The request config used
  request: {}        // Underlying request object (XMLHttpRequest or http.ClientRequest)
}
```

**Config merging**: Config is merged with order of precedence: library defaults → instance defaults → per-request config. Per-request options always override.

**Adapters**: Axios uses adapters to handle the actual HTTP transport. Default priority list is `['xhr', 'http', 'fetch']`. In browsers, `xhr` is used by default. In Node.js, `http` is used. The `fetch` adapter is available as an alternative in both environments.

## Usage Examples

### Basic GET request

```js
import axios from "axios";

const { data } = await axios.get("https://jsonplaceholder.typicode.com/posts/1");
console.log(data);
```

### POST with JSON body

```js
const { data } = await axios.post(
  "https://api.example.com/users",
  { name: "John", email: "john@example.com" }
);
```

### Query parameters

```js
const { data } = await axios.get("/api/search", {
  params: { q: "axios", limit: 10 },
});
// → GET /api/search?q=axios&limit=10
```

### Error handling with type guard

```js
try {
  const { data } = await axios.get("/api/resource");
} catch (error) {
  if (axios.isAxiosError(error)) {
    console.error("HTTP error", error.response?.status, error.message);
  } else {
    throw error; // Non-axios error
  }
}
```

### Creating a configured instance

```js
const api = axios.create({
  baseURL: "https://api.example.com",
  timeout: 5000,
  headers: { "X-Custom-Header": "value" },
});

const { data } = await api.get("/users");
```

### Request interceptor for auth tokens

```js
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.set("Authorization", `Bearer ${token}`);
  }
  return config;
});
```

### Canceling a request

```js
const controller = new AbortController();

axios.get("/api/data", { signal: controller.signal })
  .catch((error) => {
    if (axios.isCancel(error)) {
      console.log("Request was cancelled");
    }
  });

controller.abort("User navigated away");
```

## Advanced Topics

**Request Config**: Full reference of all configuration options → See [Request Config](reference/01-request-config.md)

**Interceptors**: Intercept and modify requests and responses → See [Interceptors](reference/02-interceptors.md)

**Error Handling**: AxiosError structure, error codes, and handling patterns → See [Error Handling](reference/03-error-handling.md)

**Authentication Patterns**: Bearer tokens, HTTP Basic, API keys, token refresh, cookies → See [Authentication](reference/04-authentication.md)

**Retry and Recovery**: Retry strategies, exponential backoff, 429 handling → See [Retry and Error Recovery](reference/05-retry.md)

**File Uploads and Forms**: File posting, HTML form processing, multipart/form-data → See [File Posting and Forms](reference/06-file-posting.md)

**Headers API**: AxiosHeaders class, setting/removing headers, case preservation → See [Headers](reference/07-headers.md)

**Adapters and Testing**: Built-in adapters, custom adapters, mocking strategies → See [Adapters and Testing](reference/08-adapters-testing.md)

**Progress and Rate Limiting**: Upload/download progress events, bandwidth limiting → See [Progress and Rate Limiting](reference/09-progress-rate-limiting.md)

**TypeScript Support**: Type definitions, module resolution settings, typed instances → See [TypeScript](reference/10-typescript.md)

**Security Considerations**: Decompression bomb protection, socket path restrictions, provenance verification → See [Security](reference/11-security.md)
