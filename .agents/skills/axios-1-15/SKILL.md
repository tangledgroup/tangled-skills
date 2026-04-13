---
name: axios-1-15
description: A comprehensive toolkit for making HTTP requests using Axios 1.x, a promise-based HTTP client for browser and Node.js environments. Use when building applications that require REST API communication, file uploads/downloads, request/response interception, custom headers, authentication, form data handling, progress tracking, or advanced features like rate limiting and HTTP/2 support.
version: "0.2.0"
author: Your Name <email@example.com>
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
required_environment_variables: []
---

# Axios 1.15

Axios is a promise-based HTTP client for the browser and Node.js that provides an elegant API for making XMLHttpRequests in browsers and http requests in Node.js environments. It supports request/response interception, automatic JSON transformation, file uploads with progress tracking, cancellation, and cross-platform compatibility.

## When to Use

- Making REST API calls from browser or Node.js applications
- Handling HTTP requests with authentication (Basic Auth, Bearer tokens, cookies)
- Uploading files with progress tracking
- Downloading large files with progress monitoring
- Implementing request/response interceptors for logging, error handling, or token injection
- Working with FormData or URL-encoded form data
- Cancelling in-flight requests
- Configuring custom HTTP adapters or environments (React Native, SvelteKit, Tauri)
- Rate limiting uploads/downloads in Node.js
- Using HTTP/2 protocols

## Setup

### Installation

```bash
# npm
npm install axios

# yarn
yarn add axios

# pnpm
pnpm add axios

# bun
bun add axios
```

### Import

```javascript
// ES modules (recommended)
import axios, { isCancel, AxiosError } from "axios";

// CommonJS
const axios = require("axios");

// Default export alternative for some bundlers
import { default as axios } from "axios";
```

### CDN Usage

```html
<!-- jsDelivr CDN -->
<script src="https://cdn.jsdelivr.net/npm/axios@1.13.2/dist/axios.min.js"></script>

<!-- unpkg CDN -->
<script src="https://unpkg.com/axios@1.13.2/dist/axios.min.js"></script>
```

## Quick Start

### GET Request

```javascript
// Using async/await
const response = await axios.get("/user?ID=12345");
console.log(response.data);

// With query parameters in config
const response = await axios.get("/user", {
  params: { ID: 12345 }
});

// Promise syntax
axios.get("/user?ID=12345")
  .then(response => console.log(response))
  .catch(error => console.error(error));
```

### POST Request

```javascript
const response = await axios.post("/user", {
  firstName: "Fred",
  lastName: "Flintstone"
});
console.log(response);
```

### Multiple Concurrent Requests

```javascript
const [userAccount, userPermissions] = await Promise.all([
  axios.get("/user/12345"),
  axios.get("/user/12345/permissions")
]);
```

See [Core Concepts](references/01-core-concepts.md) for detailed request/response handling.  
Refer to [Advanced Workflows](references/02-advanced-workflows.md) for interceptors, cancellation, and form data.  
Check [API Reference](references/03-api-reference.md) for complete configuration options.

## Reference Files

- [`references/01-core-concepts.md`](references/01-core-concepts.md) - Request methods, response handling, error types, and basic configuration
- [`references/02-advanced-workflows.md`](references/02-advanced-workflows.md) - Interceptors, cancellation, form data, file uploads, progress tracking, rate limiting
- [`references/03-api-reference.md`](references/03-api-reference.md) - Complete config options, AxiosHeaders API, instance methods, adapter configuration
- [`references/04-troubleshooting.md`](references/04-troubleshooting.md) - Common issues, error codes, CORS problems, timeout handling, migration guides

**Note:** `{baseDir}` refers to the skill's base directory (e.g., `.agents/skills/axios-1-15/`). All paths are relative to this directory.

## Troubleshooting

### Request Timed Out

```javascript
try {
  const response = await axios.get("https://example.com/data", {
    timeout: 5000 // 5 seconds
  });
} catch (error) {
  if (axios.isAxiosError(error) && error.code === "ECONNABORTED") {
    console.error("Request timed out!");
  } else {
    console.error("Error:", error.message);
  }
}
```

### Network Errors and CORS

```javascript
axios.get("/api/data").catch(error => {
  if (error.code === "ERR_NETWORK") {
    // Network issue, CORS violation, or mixed content
    console.error("Network error - check browser console for details");
  }
});
```

### Handling Different Error Types

See [Troubleshooting Guide](references/04-troubleshooting.md) for comprehensive error handling patterns.

## Key Features

- **Promise-based API** - Modern async/await support
- **Request/response interception** - Transform data before sending or after receiving
- **Automatic JSON transformation** - No manual stringify/parsing needed
- **Form data support** - Automatic serialization to FormData or URLSearchParams
- **Request cancellation** - AbortController or CancelToken (deprecated)
- **Progress tracking** - Upload/download progress events
- **Rate limiting** - Control upload/download speeds in Node.js
- **Cross-platform** - Works in browser, Node.js, React Native, SvelteKit, Tauri
- **TypeScript support** - Built-in type definitions
- **HTTP/2 support** - Experimental HTTP/2 adapter (v1.13.0+)

## Browser Support

Chrome, Firefox, Safari, Opera, Edge (latest versions)

## Node.js Support

Node.js 14.x and above recommended for full feature support
