# Interceptors & Authentication

## Interceptors

Interceptors are middleware-like hooks that execute before requests are sent and before responses reach your code. They are the primary mechanism for cross-cutting concerns like authentication, logging, and error handling.

### Adding Interceptors

```js
// Request interceptor — runs before the request is sent
axios.interceptors.request.use(
  function (config) {
    // Modify config (headers, params, etc.)
    return config;
  },
  function (error) {
    // Handle request setup errors
    return Promise.reject(error);
  }
);

// Response interceptor — runs after the response is received
axios.interceptors.response.use(
  function (response) {
    // Modify or log response data
    return response;
  },
  function (error) {
    // Handle HTTP errors (non-2xx status codes)
    return Promise.reject(error);
  }
);
```

### Removing Interceptors

Eject a single interceptor by storing its ID:

```js
const myInterceptor = axios.interceptors.request.use((config) => config);
axios.interceptors.request.eject(myInterceptor);
```

Clear all interceptors on an instance:

```js
instance.interceptors.request.clear();
instance.interceptors.response.clear();
```

### Execution Order

- **Request interceptors** execute in **reverse order** (LIFO — last added, first run)
- **Response interceptors** execute in **order added** (FIFO — first added, first run)

```js
const api = axios.create();
api.interceptors.request.use((c) => { console.log("req-1"); return c; });
api.interceptors.request.use((c) => { console.log("req-2"); return c; });
api.interceptors.response.use((r) => { console.log("res-1"); return r; });
api.interceptors.response.use((r) => { console.log("res-2"); return r; });

await api.get("/data");
// Output: req-2 → req-1 → [HTTP request] → res-1 → res-2
```

### Synchronous Interceptors

By default, interceptors are asynchronous (a Promise is created, pushing the request to the bottom of the call stack). For purely synchronous logic, use `{ synchronous: true }`:

```js
axios.interceptors.request.use(
  (config) => {
    config.headers.set("X-Trace", "sync");
    return config;
  },
  null,
  { synchronous: true }
);
```

### Conditional Interceptors with `runWhen`

Skip interceptor execution based on a runtime check:

```js
axios.interceptors.request.use(
  (config) => {
    config.headers.set("X-Special", "get-only");
    return config;
  },
  null,
  { runWhen: (config) => config.method === "get" }
);
```

### Instance-Scoped Interceptors

Interceptors added to an instance only apply to that instance:

```js
const loggingApi = axios.create({ baseURL: "https://api.example.com" });

loggingApi.interceptors.request.use((config) => {
  console.log(`→ ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

// This interceptor does NOT affect the default axios instance
```

## AxiosHeaders

Axios provides an `AxiosHeaders` class for case-insensitive header manipulation with a Map-like API.

### Setting Headers

```js
// In an interceptor
config.headers.set("Authorization", "Bearer token");
config.headers.setContentType("application/json");

// On a request
await axios.get("/api/data", {
  headers: { "Accept-Language": "en-US" },
});

// On an instance
const api = axios.create({
  headers: { "X-App-Version": "2.0.0" },
});
```

### Header Value Types

- `string` — normal value sent to the server
- `null` — skip when converting to JSON
- `false` — skip and prevent axios from overwriting (use `rewrite: true` to force)
- `undefined` — not set

### Removing a Default Header

Set to `false` to opt out of axios's default headers:

```js
await axios.post("/api/data", payload, {
  headers: { "Content-Type": false }, // let browser set it (e.g., for FormData)
});
```

### Reading Response Headers

```js
const response = await axios.get("/api/data");
console.log(response.headers["content-type"]);  // bracket notation
console.log(response.headers.get("x-request-id")); // .get() method
```

### Preserving Header Case

`AxiosHeaders` keeps the case of the first matching key. Seed with `undefined` to control casing:

```js
const api = axios.create();
api.defaults.headers.common = {
  "content-type": undefined,
  accept: undefined,
};

await api.put(url, data, {
  headers: {
    "Content-Type": "application/octet-stream",
    Accept: "application/json",
  },
});
```

### Header Methods

- `set(name, value, rewrite?)` — set one or multiple headers
- `get(name, parser?)` — get a header value, optionally parsed
- `has(name)` — check if a header is set
- `delete(name)` — remove a header
- `clear(matcher?)` — clear all or matching headers
- `normalize(format?)` — merge duplicate keys (different cases)
- `concat(...targets)` — merge into a new AxiosHeaders instance
- `toJSON(asStrings?)` — resolve to a plain object
- `from(thing)` — create from raw headers or string

Shortcut methods: `setContentType`, `getContentType`, `hasContentType`, `setContentLength`, `getContentLength`, `hasContentLength`, `setAccept`, `getAccept`, `hasAccept`, `setUserAgent`, `getUserAgent`, `hasUserAgent`, `setContentEncoding`, `getContentEncoding`, `hasContentEncoding`.

## Authentication Patterns

### Bearer Tokens (JWT)

The most common pattern — attach a JWT via request interceptor so the token is read fresh on every request:

```js
const api = axios.create({ baseURL: "https://api.example.com" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.set("Authorization", `Bearer ${token}`);
  }
  return config;
});
```

### HTTP Basic Auth

Use the `auth` config option for HTTP Basic authentication:

```js
const response = await axios.get("https://api.example.com/data", {
  auth: { username: "myUser", password: "myPassword" },
});
```

> The `auth` option is only for HTTP Basic. For Bearer tokens and API keys, use the `Authorization` header directly.

### API Keys

Pass as a header or query parameter depending on the API:

```js
// As a header
const api = axios.create({
  baseURL: "https://api.example.com",
  headers: { "X-API-Key": "your-api-key-here" },
});

// As a query parameter
const response = await axios.get("https://api.example.com/data", {
  params: { apiKey: "your-api-key-here" },
});
```

### Cookie-Based Authentication

Set `withCredentials: true` to include cookies in cross-origin requests:

```js
const api = axios.create({
  baseURL: "https://api.example.com",
  withCredentials: true,
});
```

> `withCredentials: true` requires the server to respond with `Access-Control-Allow-Credentials: true` and a specific (non-wildcard) `Access-Control-Allow-Origin`.

### Token Refresh

Implement silent token refresh with a response interceptor. This pattern queues failed requests while the refresh is in progress:

```js
const api = axios.create({ baseURL: "https://api.example.com" });

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    error ? prom.reject(error) : prom.resolve(token);
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers["Authorization"] = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const { data } = await axios.post("/auth/refresh", {
          refreshToken: localStorage.getItem("refresh_token"),
        });

        const newToken = data.access_token;
        localStorage.setItem("access_token", newToken);
        processQueue(null, newToken);
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        localStorage.removeItem("access_token");
        window.location.href = "/login";
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);
```
