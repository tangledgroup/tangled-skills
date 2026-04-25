# Core Concepts

This reference covers fundamental Axios concepts including request methods, response handling, error types, and basic configuration patterns.

## Request Methods

### Available Methods

Axios provides multiple ways to make HTTP requests:

```javascript
// Using axios method aliases (recommended)
axios.get(url[, config])
axios.delete(url[, config])
axios.head(url[, config])
axios.options(url[, config])
axios.post(url[, data[, config]])
axios.put(url[, data[, config]])
axios.patch(url[, data[, config]])

// Using generic request method
axios.request(config)

// Shorthand form (url as first argument)
axios(url[, config]) // Defaults to GET
```

### Method Aliases

When using alias methods, you don't need to specify `url`, `method`, or `data` in the config object as they're inferred from the arguments.

```javascript
// These are equivalent:
axios.get('/user/123');
axios({ method: 'get', url: '/user/123' });
```

### Request Examples

#### GET with Query Parameters

```javascript
// Method 1: URL string with query params
const response = await axios.get("/user?ID=12345&role=admin");

// Method 2: Params object (recommended)
const response = await axios.get("/user", {
  params: {
    ID: 12345,
    role: "admin"
  }
});

// Both produce: /user?ID=12345&role=admin
```

#### POST with JSON Body

```javascript
const response = await axios.post("/user", {
  firstName: "Fred",
  lastName: "Flintstone",
  email: "fred@example.com"
});

// Automatically sets Content-Type: application/json
// and stringifies the object to JSON
```

#### PUT/PATCH with Data

```javascript
// Update entire resource
await axios.put("/user/12345", {
  firstName: "Fred",
  lastName: "Flintstone",
  email: "fred@example.com"
});

// Partial update
await axios.patch("/user/12345", {
  email: "newemail@example.com"
});
```

#### DELETE with Body (if needed)

```javascript
await axios.delete("/user/12345", {
  data: { reason: "violation" }
});
```

## Response Schema

Every successful Axios request returns a response object with the following structure:

```javascript
{
  // The response data (auto-parsed if JSON)
  data: {},
  
  // HTTP status code
  status: 200,
  
  // HTTP status text
  statusText: 'OK',
  
  // Response headers (all lowercase)
  headers: {
    'content-type': 'application/json',
    'content-length': '1234'
  },
  
  // The config used for this request
  config: {},
  
  // The request that generated this response
  // XMLHttpRequest in browser, ClientRequest in Node.js
  request: {}
}
```

### Accessing Response Data

```javascript
const response = await axios.get("/user/12345");

console.log(response.data);        // Response body
console.log(response.status);      // 200
console.log(response.statusText);  // "OK"
console.log(response.headers);     // Headers object
console.log(response.config);      // Request config

// Access headers with bracket notation (case-insensitive)
console.log(response.headers['content-type']);
console.log(response.headers["Content-Type"]); // Also works
```

### Response Types

Configure how the response should be transformed:

```javascript
// JSON (default) - auto-parses JSON responses
const jsonResponse = await axios.get("/api/data");

// Text - returns raw response text
const textResponse = await axios.get("/api/data", {
  responseType: "text"
});

// Blob - for binary data in browser
const blobResponse = await axios.get("/file.pdf", {
  responseType: "blob"
});

// ArrayBuffer - for binary data
const arrayBufferResponse = await axios.get("/file.bin", {
  responseType: "arraybuffer"
});

// Stream - Node.js only, returns readable stream
const streamResponse = await axios.get("https://example.com/file", {
  responseType: "stream"
});

// Document - browser only, parses as XML document
const docResponse = await axios.get("/data.xml", {
  responseType: "document"
});
```

### Streaming Large Files (Node.js)

```javascript
const fs = require("fs");

const response = await axios({
  method: "get",
  url: "https://example.com/large-file.zip",
  responseType: "stream"
});

// Pipe to file
response.data.pipe(fs.createWriteStream("large-file.zip"));

// Or process chunks
response.data.on("data", chunk => {
  console.log(`Received ${chunk.length} bytes`);
});
```

## Error Handling

### Error Structure

Axios errors extend the standard Error class with additional properties:

```javascript
{
  // Error message
  message: "Request failed with status code 404",
  
  // Error name
  name: "AxiosError",
  
  // Stack trace
  stack: "Error: ...\n    at ...",
  
  // HTTP response (if available)
  response: {
    data: {},
    status: 404,
    statusText: "Not Found",
    headers: {},
    config: {}
  },
  
  // The request that was made
  request: {},
  
  // Axios-specific error code
  code: "ERR_BAD_REQUEST",
  
  // Config that caused the error
  config: {}
}
```

### Error Handling Pattern

```javascript
try {
  const response = await axios.get("/user/12345");
} catch (error) {
  if (axios.isAxiosError(error)) {
    if (error.response) {
      // Server responded with non-2xx status
      console.error("Status:", error.response.status);
      console.error("Data:", error.response.data);
      console.error("Headers:", error.response.headers);
    } else if (error.request) {
      // Request was made but no response received
      console.error("No response received:", error.request);
    } else {
      // Error in setting up the request
      console.error("Error:", error.message);
    }
  } else {
    // Non-Axios error
    console.error("Unexpected error:", error);
  }
}
```

### Error Types by Response Status

```javascript
axios.get("/api/data").catch(error => {
  if (error.response) {
    const status = error.response.status;
    
    if (status === 400) {
      // Bad request - invalid parameters
      console.error("Invalid request parameters");
    } else if (status === 401) {
      // Unauthorized - invalid/missing credentials
      console.error("Authentication required");
    } else if (status === 403) {
      // Forbidden - insufficient permissions
      console.error("Access denied");
    } else if (status === 404) {
      // Not found
      console.error("Resource not found");
    } else if (status >= 500) {
      // Server error
      console.error("Server error, try again later");
    }
  }
});
```

### Axios Error Codes

| Code | Definition |
|------|------------|
| `ERR_BAD_OPTION_VALUE` | Invalid value in axios configuration |
| `ERR_BAD_OPTION` | Invalid option in axios configuration |
| `ERR_NOT_SUPPORT` | Feature not supported in current environment |
| `ERR_DEPRECATED` | Deprecated feature used |
| `ERR_INVALID_URL` | Invalid URL provided |
| `ECONNABORTED` | Request timed out or aborted |
| `ERR_CANCELED` | Request canceled by AbortSignal or CancelToken |
| `ETIMEDOUT` | Request timed out (requires `transitional.clarifyTimeoutError: true`) |
| `ERR_NETWORK` | Network error, CORS violation, or mixed content |
| `ERR_FR_TOO_MANY_REDIRECTS` | Exceeded maximum redirects |
| `ERR_BAD_RESPONSE` | Response cannot be parsed or unexpected format |
| `ERR_BAD_REQUEST` | Request has unexpected format or missing parameters |

### Custom Error Validation

Override default status code validation:

```javascript
// Resolve for any status < 500
const response = await axios.get("/api/data", {
  validateStatus: (status) => status < 500
});

// Reject only on specific status codes
const response = await axios.get("/api/data", {
  validateStatus: (status) => status === 200 || status === 201
});
```

### Type Guard for Axios Errors

```typescript
import { isAxiosError } from "axios";

try {
  const { data } = await axios.get("/user");
} catch (error) {
  if (isAxiosError(error)) {
    // Type-safe access to axios error properties
    if (error.response) {
      console.error("HTTP error:", error.response.status);
    }
  } else {
    // Handle non-Axios errors
    console.error("Other error:", error);
  }
}
```

## Basic Configuration

### URL and Base URL

```javascript
// Absolute URL
await axios.get("https://api.example.com/users");

// Relative URL with baseURL
const instance = axios.create({
  baseURL: "https://api.example.com/v1"
});

await instance.get("/users"); // -> https://api.example.com/v1/users

// Allow or disallow absolute URLs overriding baseURL
await axios.get("https://other-api.com/data", {
  allowAbsoluteUrls: true // default: true
});
```

### Headers

```javascript
// Set custom headers
await axios.get("/api/data", {
  headers: {
    "Authorization": "Bearer token123",
    "X-Custom-Header": "custom-value",
    "Accept": "application/json"
  }
});

// Common headers for all methods
axios.defaults.headers.common["Authorization"] = "Bearer token";

// Method-specific headers
axios.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";
```

### Timeout Configuration

```javascript
// Request timeout in milliseconds (default: 0 = no timeout)
await axios.get("/api/data", {
  timeout: 5000 // 5 seconds
});

// Handle timeout errors
try {
  await axios.get("/api/slow-endpoint", { timeout: 1000 });
} catch (error) {
  if (error.code === "ECONNABORTED") {
    console.error("Request timed out");
  }
}
```

### Authentication

#### Basic Auth

```javascript
// Method 1: auth config
await axios.get("/api/protected", {
  auth: {
    username: "user",
    password: "pass"
  }
});

// Method 2: Authorization header (manual)
await axios.get("/api/protected", {
  headers: {
    "Authorization": "Basic dXNlcjpwYXNz" // base64 encoded
  }
});
```

#### Bearer Token

```javascript
await axios.get("/api/protected", {
  headers: {
    "Authorization": "Bearer your-jwt-token-here"
  }
});
```

### Transform Request/Response Data

```javascript
// Transform request data before sending
await axios.post("/api/data", myData, {
  transformRequest: [(data, headers) => {
    // Add timestamp
    data.timestamp = Date.now();
    return JSON.stringify(data);
  }]
});

// Transform response data before returning
const response = await axios.get("/api/data", {
  transformResponse: [(data) => {
    // Custom parsing or transformation
    if (typeof data === "string") {
      return JSON.parse(data);
    }
    return data;
  }]
});
```

### Proxy Configuration

```javascript
// HTTP proxy
await axios.get("/api/data", {
  proxy: {
    protocol: "http",
    host: "127.0.0.1",
    port: 8080,
    auth: {
      username: "proxy-user",
      password: "proxy-pass"
    }
  }
});

// HTTPS proxy
await axios.get("/api/data", {
  proxy: {
    protocol: "https",
    host: "proxy.example.com",
    port: 443
  }
});

// Disable proxy (ignore environment variables)
await axios.get("/api/data", {
  proxy: false
});
```

### With Credentials and XSRF

```javascript
// Send cookies with cross-origin requests
await axios.get("/api/data", {
  withCredentials: true
});

// XSRF token configuration
await axios.get("/api/data", {
  xsrfCookieName: "XSRF-TOKEN", // default
  xsrfHeaderName: "X-XSRF-TOKEN" // default
});

// Conditional XSRF token
await axios.get("/api/data", {
  withXSRFToken: (config) => {
    return config.baseURL === "https://same-origin.com";
  }
});
```

## Response Interceptors Basics

Simple response transformation without complex interceptor chains:

```javascript
// Using transformResponse for simple cases
const response = await axios.get("/api/data", {
  transformResponse: [(data) => {
    // Strip wrapper object if present
    if (data && data.result) {
      return data.result;
    }
    return data;
  }]
});
```

For advanced interceptor patterns, see [Advanced Workflows](02-advanced-workflows.md).
