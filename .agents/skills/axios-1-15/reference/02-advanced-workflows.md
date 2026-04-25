# Advanced Workflows

This reference covers advanced Axios features including interceptors, request cancellation, form data handling, file uploads, progress tracking, and rate limiting.

## Interceptors

Interceptors allow you to transform requests before they're sent or responses before they're handled by your code.

### Request Interceptors

```javascript
const instance = axios.create();

// Add a request interceptor
const interceptorId = instance.interceptors.request.use(
  function (config) {
    // Do something before the request is sent
    
    // Add authentication token
    const token = localStorage.getItem("authToken");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add timestamp
    config.headers["X-Request-Time"] = Date.now();
    
    // Modify URL or params
    config.params.locale = "en-US";
    
    return config;
  },
  function (error) {
    // Handle request error
    return Promise.reject(error);
  }
);

// Remove interceptor later
instance.interceptors.request.eject(interceptorId);

// Clear all request interceptors
instance.interceptors.request.clear();
```

### Response Interceptors

```javascript
// Add a response interceptor
const interceptorId = instance.interceptors.response.use(
  function (response) {
    // Do something with successful response
    
    // Log response time
    const duration = Date.now() - response.config.headers["X-Request-Time"];
    console.log(`Request completed in ${duration}ms`);
    
    // Transform data
    if (response.data && response.data.payload) {
      response.data = response.data.payload;
    }
    
    return response;
  },
  function (error) {
    // Handle error response
    
    // Auto-refresh token on 401
    if (error.response && error.response.status === 401) {
      return refreshAccessToken()
        .then(newToken => {
          error.config.headers.Authorization = `Bearer ${newToken}`;
          return axios.request(error.config);
        })
        .catch(refreshError => {
          // Token refresh failed, redirect to login
          window.location.href = "/login";
          return Promise.reject(refreshError);
        });
    }
    
    return Promise.reject(error);
  }
);
```

### Interceptor Execution Order

**Critical:** Request and response interceptors execute in different orders!

```javascript
const instance = axios.create();

// Request interceptors: LIFO (Last In, First Out)
instance.interceptors.request.use(config => {
  console.log("Request 1"); // Executes THIRD
  return config;
});

instance.interceptors.request.use(config => {
  console.log("Request 2"); // Executes SECOND
  return config;
});

instance.interceptors.request.use(config => {
  console.log("Request 3"); // Executes FIRST
  return config;
});

// Response interceptors: FIFO (First In, First Out)
instance.interceptors.response.use(response => {
  console.log("Response 1"); // Executes FIRST
  return response;
});

instance.interceptors.response.use(response => {
  console.log("Response 2"); // Executes SECOND
  return response;
});

instance.interceptors.response.use(response => {
  console.log("Response 3"); // Executes THIRD
  return response;
});

// Output when making a request:
// Request 3
// Request 2
// Request 1
// [HTTP request made]
// Response 1
// Response 2
// Response 3
```

### Synchronous Interceptors

By default, interceptors are async. For synchronous interceptors (faster execution):

```javascript
instance.interceptors.request.use(
  function (config) {
    config.headers["X-Custom"] = "value";
    return config;
  },
  null,
  { synchronous: true } // Skip promise creation for faster sync execution
);
```

### Conditional Interceptors

Run interceptors only under specific conditions:

```javascript
function shouldAddLogging(config) {
  return config.method === "post" && config.url.includes("/api/");
}

instance.interceptors.request.use(
  function (config) {
    console.log("Logging request:", config);
    return config;
  },
  null,
  { runWhen: shouldAddLogging } // Only runs when condition is true
);
```

### Multiple Interceptors Pattern

```javascript
// Each interceptor receives the result of its predecessor
instance.interceptors.response.use(response => {
  console.log("Interceptor 1 - Original response");
  response.data.processed = true;
  return response;
});

instance.interceptors.response.use(response => {
  console.log("Interceptor 2 - Already processed:", response.data.processed);
  response.data.validated = true;
  return response;
});

// Only the last interceptor's result is returned to your code
```

## Request Cancellation

### AbortController (Recommended)

Modern approach using native AbortController API:

```javascript
const controller = new AbortController();

axios
  .get("/api/data", {
    signal: controller.signal,
    timeout: 10000
  })
  .then(response => {
    console.log(response);
  })
  .catch(error => {
    if (axios.isCancel(error) || error.code === "ERR_CANCELED") {
      console.log("Request canceled:", error.message);
    } else {
      console.error("Request error:", error);
    }
  });

// Cancel the request (e.g., on component unmount or user action)
controller.abort("User canceled the request");
```

### React Component Example

```jsx
import { useEffect, useState } from "react";
import axios from "axios";

function DataFetcher() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const controller = new AbortController();

    setLoading(true);
    axios.get("/api/data", { signal: controller.signal })
      .then(response => setData(response.data))
      .catch(error => {
        if (!axios.isCancel(error)) {
          console.error("Fetch error:", error);
        }
      })
      .finally(() => setLoading(false));

    // Cleanup: cancel request when component unmounts
    return () => controller.abort();
  }, []);

  return <div>{loading ? "Loading..." : JSON.stringify(data)}</div>;
}
```

### Cancel Multiple Requests

```javascript
const controller = new AbortController();

// Multiple requests share the same abort signal
Promise.all([
  axios.get("/api/users", { signal: controller.signal }),
  axios.get("/api/posts", { signal: controller.signal }),
  axios.get("/api/comments", { signal: controller.signal })
])
.then(results => console.log(results))
.catch(error => {
  if (error.code === "ERR_CANCELED") {
    console.log("All requests canceled");
  }
});

// Cancel all at once
controller.abort();
```

### CancelToken (Deprecated)

The CancelToken API is deprecated since v0.22.0 but still supported:

```javascript
const CancelToken = axios.CancelToken;
const source = CancelToken.source();

axios
  .get("/api/data", {
    cancelToken: source.token
  })
  .catch(thrown => {
    if (axios.isCancel(thrown)) {
      console.log("Request canceled:", thrown.message);
    }
  });

// Cancel later
source.cancel("Operation canceled by user");
```

## Form Data Handling

### URL-Encoded Forms

#### Using URLSearchParams (Recommended)

```javascript
const params = new URLSearchParams();
params.append("username", "john_doe");
params.append("password", "secret123");
params.append("remember", "true");

await axios.post("/login", params);
// Automatically sets Content-Type: application/x-www-form-urlencoded
```

#### Automatic Serialization

Axios automatically serializes objects when the correct Content-Type is set:

```javascript
const data = {
  username: "john_doe",
  password: "secret123",
  preferences: { theme: "dark", lang: "en" }
};

await axios.post("/api/data", data, {
  headers: {
    "Content-Type": "application/x-www-form-urlencoded"
  }
});

// Server receives:
// username=john_doe&password=secret123&preferences[theme]=dark&preferences[lang]=en
```

#### Using qs Library (Older Browsers)

```javascript
import qs from "qs";

const data = { user: { name: "John", age: 30 } };

await axios.post("/api/data", qs.stringify(data), {
  headers: {
    "Content-Type": "application/x-www-form-urlencoded"
  }
});
```

### Multipart Form Data

#### Using FormData (Browser)

```javascript
const formData = new FormData();
formData.append("username", "john_doe");
formData.append("avatar", fileInput.files[0]); // File from input element
formData.append("settings", JSON.stringify({ theme: "dark" }));

await axios.post("/upload", formData);
// Content-Type automatically set to multipart/form-data with boundary
```

#### Using FormData (Node.js)

```javascript
const FormData = require("form-data");
const fs = require("fs");

const form = new FormData();
form.append("my_field", "my value");
form.append("my_file", fs.createReadStream("/path/to/file.jpg"));

await axios.post("https://example.com/upload", form);
```

#### Automatic Serialization to FormData

```javascript
const data = {
  username: "john_doe",
  avatar: fileInput.files[0],
  tags: ["tag1", "tag2"],
  metadata: { uploaded: true, timestamp: Date.now() }
};

await axios.postForm("/upload", data);
// Shortcut method that sets Content-Type: multipart/form-data
```

#### Special FormData Syntax

```javascript
const data = {
  // JSON serialization with {} suffix
  "config{}": { theme: "dark", lang: "en" },
  
  // Array expansion with [] suffix
  "tags[]": ["tag1", "tag2", "tag3"],
  
  // Nested objects
  "user[name]": "John",
  "user[email]": "john@example.com"
};

await axios.postForm("/api/data", data);
```

#### Custom FormData Serialization Options

```javascript
await axios.post("/upload", data, {
  headers: {
    "Content-Type": "multipart/form-data"
  },
  formSerializer: {
    // Use dots instead of brackets
    dots: true,
    
    // Keep meta tokens like {} in parameter names
    metaTokens: true,
    
    // Array index format: null (no brackets), false (empty brackets), true (with indexes)
    indexes: false,
    
    // Custom visitor function for complex serialization
    visitor: (value, key, path, helpers) => {
      if (key === "password") {
        return btoa(value); // Encode password
      }
      return value;
    }
  }
});
```

### HTML Form Submission

```javascript
// Submit entire HTML form as multipart/form-data
const form = document.querySelector("#myForm");
await axios.postForm("/submit", form);

// Submit form as JSON instead
const response = await axios.post("/submit", form, {
  headers: {
    "Content-Type": "application/json"
  }
});

// Form:
// <form id="myForm">
//   <input name="foo" value="1">
//   <input name="deep.prop" value="2">
//   <select name="user.age">
//     <option value="25" selected>25</option>
//   </select>
// </form>

// JSON result:
// { foo: "1", deep: { prop: "2" }, user: { age: "25" } }
```

## File Uploads

### Single File Upload

```javascript
const file = document.querySelector("#fileInput").files[0];

await axios.postForm("/upload", {
  description: "My file",
  file: file
});
```

### Multiple Files Upload

```javascript
// Using FileList
const files = document.querySelector("#fileInput").files;

await axios.postForm("/upload", {
  "files[]": files // All files sent with same field name
});

// Or pass FileList directly
await axios.postForm("/upload", files);
```

### Upload with Progress Tracking

```javascript
await axios.post("/upload", formData, {
  onUploadProgress: (progressEvent) => {
    const { loaded, total, progress, bytes, estimated, rate } = progressEvent;
    
    const percentCompleted = Math.round((progress * 100));
    console.log(`Upload: ${percentCompleted}% (${loaded}/${total} bytes)`);
    console.log(`Speed: ${(rate / 1024).toFixed(2)} KB/s`);
    console.log(`ETA: ${estimated.toFixed(1)}s`);
  }
});
```

### Stream Upload (Node.js)

```javascript
const fs = require("fs");

const stream = fs.createReadStream("large-file.zip");
const contentLength = fs.statSync("large-file.zip").size;

await axios.post("/upload", stream, {
  headers: {
    "Content-Length": contentLength
  },
  maxRedirects: 0, // Disable redirects to avoid buffering entire stream
  onUploadProgress: ({ progress }) => {
    console.log(`Upload progress: ${(progress * 100).toFixed(2)}%`);
  }
});

// Warning: Without maxRedirects: 0, follow-redirects buffers entire stream in RAM
```

## Download Progress

### File Download with Progress

```javascript
await axios.get("/large-file.zip", {
  responseType: "blob",
  onDownloadProgress: (progressEvent) => {
    const { loaded, total, progress, rate } = progressEvent;
    
    const percentCompleted = Math.round((progress * 100));
    console.log(`Download: ${percentCompleted}%`);
    console.log(`Speed: ${(rate / 1024 / 1024).toFixed(2)} MB/s`);
  }
});
```

### Save Downloaded File (Browser)

```javascript
const response = await axios.get("/file.zip", {
  responseType: "blob",
  onDownloadProgress: (e) => {
    console.log(`Downloaded ${(e.progress * 100).toFixed(2)}%`);
  }
});

// Create download link
const url = window.URL.createObjectURL(new Blob([response.data]));
const link = document.createElement("a");
link.href = url;
link.setAttribute("download", "file.zip");
document.body.appendChild(link);
link.click();
document.body.removeChild(link);
window.URL.revokeObjectURL(url);
```

## Progress Event Structure

Both upload and download progress events provide:

```javascript
{
  loaded: number,        // Bytes transferred so far
  total?: number,        // Total bytes (may be unavailable)
  progress?: number,     // Progress ratio [0..1]
  bytes: number,         // Bytes transferred since last event (delta)
  estimated?: number,    // Estimated time remaining in seconds
  rate?: number,         // Transfer speed in bytes/second
  upload: boolean,       // true for upload, false for download
  download: boolean      // true for download, false for upload
}
```

**Note:** Progress events are throttled to 3 times per second.

## Rate Limiting (Node.js Only)

Control upload and download speeds:

```javascript
await axios.post("/upload", largeBuffer, {
  maxRate: [
    100 * 1024, // Upload limit: 100 KB/s
    100 * 1024  // Download limit: 100 KB/s
  ],
  onUploadProgress: ({ progress, rate }) => {
    console.log(
      `Upload [${(progress * 100).toFixed(2)}%]: ` +
      `${(rate / 1024).toFixed(2)} KB/s`
    );
  }
});
```

## HTTP/2 Support (Experimental)

Available since v1.13.0:

```javascript
const formData = new FormData();
formData.append("file", fileInput.files[0]);

const response = await axios.post(
  "https://httpbin.org/post",
  formData,
  {
    httpVersion: 2, // Enable HTTP/2
    
    http2Options: {
      rejectUnauthorized: false, // For self-signed certificates
      sessionTimeout: 1000       // Session timeout in ms (default: 1000)
    },
    
    onUploadProgress(e) {
      console.log("HTTP/2 upload progress", e.progress);
    },
    
    onDownloadProgress(e) {
      console.log("HTTP/2 download progress", e.progress);
    }
  }
);
```

## Custom Fetch Adapter

For environments with custom fetch implementations:

### SvelteKit

```javascript
export async function load({ fetch }) {
  const { data } = await axios.get("https://api.example.com/data", {
    adapter: "fetch",
    env: {
      fetch,        // Use SvelteKit's fetch
      Request: null, // Disable progress tracking if incompatible
      Response: null
    }
  });

  return { data };
}
```

### Tauri

```javascript
import { fetch } from "@tauri-apps/plugin-http";
import axios from "axios";

const api = axios.create({
  adapter: "fetch",
  env: {
    fetch // Use Tauri's fetch (bypasses CORS)
  }
});

const { data } = await api.get("https://api.example.com/data");
```

### Custom Fetch Implementation

```javascript
import customFetch from "custom-fetch-implementation";

const instance = axios.create({
  adapter: "fetch",
  env: {
    fetch: customFetch,
    Request: CustomRequest, // Optional custom Request constructor
    Response: CustomResponse // Optional custom Response constructor
  }
});
```

**Note:** Setting `Request` and `Response` to `null` disables progress tracking in the fetch adapter.
