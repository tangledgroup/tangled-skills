# Request Config

The request config object controls every aspect of an axios request. Only `url` is required. The default method is `GET`.

## URL and Base

### `url`

The server URL for the request. Can be a string or `URL` instance.

```js
axios.get("/users/1");
```

### `baseURL`

Prepended to `url` unless `url` is absolute (and `allowAbsoluteUrls` is `true`, the default).

```js
const api = axios.create({ baseURL: "https://api.example.com" });
await api.get("/users"); // → https://api.example.com/users
```

### `allowAbsoluteUrls`

When `true` (default), absolute URLs override `baseURL`. When `false`, absolute URLs are always prepended by `baseURL`.

## Method and Data

### `method`

HTTP method. Default: `"get"`.

### `data`

Request body for `PUT`, `POST`, `PATCH`, and `DELETE`. Supported types:

- string, plain object, ArrayBuffer, ArrayBufferView, URLSearchParams
- Browser only: FormData, File, Blob
- Node.js only: Stream, Buffer, FormData (form-data package)

When no `transformRequest` is set, axios auto-serializes plain objects to JSON.

### `transformRequest`

Array of functions that modify request data before it is sent. Only for `PUT`, `POST`, `PATCH`, `DELETE`. The last function must return a string, Buffer, ArrayBuffer, FormData, or Stream.

```js
axios.post("/api/data", { key: "value" }, {
  transformRequest: [(data, headers) => {
    // Modify data and/or headers
    return JSON.stringify(data);
  }],
});
```

### `transformResponse`

Array of functions that modify response data before it reaches `.then()` / `await`.

```js
axios.get("/api/data", {
  transformResponse: [(data) => {
    // Parse or transform response
    return data;
  }],
});
```

## Headers

### `headers`

Custom HTTP headers. Default `Content-Type` is `application/json`. Use the `AxiosHeaders` API in interceptors:

```js
config.headers.set("Authorization", "Bearer token");
```

See [Interceptors & Authentication](reference/02-interceptors-authentication.md) for header management details.

## Query Parameters

### `params`

URL query parameters as a plain object or URLSearchParams. Merged with any query string already in `url`.

```js
axios.get("/search", { params: { q: "axios", page: 1 } });
// → /search?q=axios&page=1
```

### `paramsSerializer`

Customize how `params` are serialized:

- `encode` — custom encoder function for key/value pairs
- `serialize` — custom serializer for the entire params object
- `indexes` — array bracket format: `null` (no brackets), `false` (empty brackets, default), `true` (indexed brackets)
- `maxDepth` — maximum nesting depth (default: 100)

## Timeout

### `timeout`

Milliseconds before the request is aborted. Default: `0` (no timeout).

```js
axios.get("/api/data", { timeout: 5000 });
```

## Credentials and XSRF

### `withCredentials`

Whether cross-site requests should include cookies, authorization headers, or TLS client certificates. Default: `false`.

### `xsrfCookieName`

Name of the cookie to read the XSRF token from. Default: `"XSRF-TOKEN"`.

### `xsrfHeaderName`

Name of the header to send the XSRF token in. Default: `"X-XSRF-TOKEN"`.

### `withXSRFToken`

Whether to send the XSRF token. Default: `undefined` (same-origin only). Can be a function:

```js
axios.get("/api/data", {
  withXSRFToken: (config) => config.method === "post",
});
```

## Response Handling

### `responseType`

Expected response type. Options:

- `json` (default) — parse as JSON
- `text` — raw text
- `arraybuffer` — ArrayBuffer
- `blob` — Blob (browser only)
- `document` — Document (browser only)
- `stream` — Stream (Node.js only)
- `formdata` — FormData (fetch adapter only)

### `responseEncoding`

Encoding for decoding responses (Node.js only, ignored for `stream`). Default: `"utf8"`. Options include `ascii`, `base64`, `hex`, `latin1`, `utf-8`, `utf16le`, and others.

### `decompress`

Whether to automatically decompress responses (Node.js only). Default: `true`.

### `validateStatus`

Function that determines whether the promise resolves or rejects. Default: `status >= 200 && status < 300`.

```js
axios.get("/api/data", {
  validateStatus: (status) => status < 500,
});
```

## Adapters

### `adapter`

Request adapter to use. Built-in options:

- `"xhr"` — XMLHttpRequest (browser default)
- `"http"` — Node.js http/https (Node.js default)
- `"fetch"` — Fetch API (v1.7.0+)
- Array of names — uses first available in the environment

```js
axios.create({ adapter: "fetch" });
axios.create({ adapter: ["fetch", "xhr", "http"] });
```

## Authentication

### `auth`

HTTP Basic authentication credentials. Sets the `Authorization` header automatically. For Bearer tokens, use the `headers` option instead.

```js
axios.get("/api/data", {
  auth: { username: "user", password: "pass" },
});
```

## Cancellation

### `signal`

An `AbortSignal` from `AbortController` for cancelling requests:

```js
const controller = new AbortController();
axios.get("/api/data", { signal: controller.signal });
controller.abort(); // cancels the request
```

### `cancelToken`

Deprecated. Use `signal` instead.

## Node.js Options

The following options are only available in Node.js environments.

### `maxContentLength`

Maximum response body size in bytes. Default: `-1` (unlimited).

> **Security:** Set an explicit limit when requesting servers you do not fully trust to prevent decompression-bomb DoS.

### `maxBodyLength`

Maximum request body size in bytes.

### `maxRedirects`

Maximum redirects to follow. Default: `21`. Set to `0` to disable redirects.

### `beforeRedirect`

Function called before each redirect to modify the request, inspect headers, or cancel by throwing.

```js
axios.get("/api/data", {
  beforeRedirect: (options, { headers }) => {
    if (options.hostname === "example.com") {
      options.auth = "user:password";
    }
  },
});
```

### `socketPath`

UNIX socket path instead of TCP connection (e.g., `/var/run/docker.sock`).

> **Security:** If request config is derived from user input, an attacker can inject `socketPath` to redirect traffic to privileged local sockets (CWE-918). Use `allowedSocketPaths` to restrict.

### `allowedSocketPaths`

Allowlist of permitted socket paths. Empty array blocks all.

```js
axios.create({
  allowedSocketPaths: ["/var/run/docker.sock"],
});
```

### `httpAgent` / `httpsAgent`

Custom http/https agents for Node.js (e.g., to enable `keepAlive`).

### `proxy`

Proxy server configuration. Also reads from `http_proxy` and `https_proxy` environment variables. Use `no_proxy` to exclude domains. Set to `false` to disable.

```js
proxy: {
  protocol: "https",
  host: "127.0.0.1",
  port: 9000,
  auth: { username: "user", password: "pass" },
}
```

### `transport`

Custom transport module for the request.

### `maxRate`

Bandwidth limit in bytes per second. Single number applies to both directions. Array `[upload, download]` sets each independently.

```js
axios.get("/large-file", { maxRate: 100 * 1024 }); // 100 KB/s both ways
axios.get("/large-file", { maxRate: [100 * 1024, 500 * 1024] }); // 100 KB/s up, 500 KB/s down
```

### `insecureHTTPParser`

Use an insecure HTTP parser that accepts invalid headers. Avoid in production. Available Node.js 12.10.0+.

## Transitional Options

### `transitional`

Backward-compatibility options that may be removed in future versions:

- `silentJSONParsing` — `true`: ignore JSON parse errors (old behavior). `false`: throw SyntaxError.
- `forcedJSONParsing` — Parse response as JSON even if not valid JSON.
- `clarifyTimeoutError` — Throw `ETIMEDOUT` instead of generic `ECONNABORTED` on timeout.
- `legacyInterceptorReqResOrdering` — Use legacy interceptor ordering.

## Environment Options

### `env`

Override environment globals used by axios:

```js
env: {
  FormData: window?.FormData || global?.FormData,
}
```

### `formSerializer`

Configure automatic object-to-FormData serialization:

- `visitor` — custom recursive visitor function
- `dots` — use dot notation instead of brackets (`user.name` vs `user[name]`)
- `metaTokens` — preserve special key endings like `{}`
- `indexes` — array bracket format (`null`, `false`, `true`)
- `maxDepth` — maximum nesting depth (default: 100, set to `Infinity` to disable)

## Full Config Example

```js
{
  url: "/posts",
  method: "get",
  baseURL: "https://jsonplaceholder.typicode.com",
  transformRequest: [(data, headers) => data],
  transformResponse: [(data) => data],
  headers: { "X-Requested-With": "XMLHttpRequest" },
  params: { postId: 5 },
  data: { firstName: "Fred" },
  timeout: 1000,
  withCredentials: false,
  adapter: ["xhr", "http", "fetch"],
  auth: { username: "janedoe", password: "s00pers3cret" },
  responseType: "json",
  xsrfCookieName: "XSRF-TOKEN",
  xsrfHeaderName: "X-XSRF-TOKEN",
  onUploadProgress: ({ loaded, total, progress }) => {},
  onDownloadProgress: ({ loaded, total, progress }) => {},
  maxContentLength: 2000,
  maxBodyLength: 2000,
  validateStatus: (status) => status >= 200 && status < 300,
  maxRedirects: 21,
  proxy: { host: "127.0.0.1", port: 9000 },
  httpAgent: new http.Agent({ keepAlive: true }),
  httpsAgent: new https.Agent({ keepAlive: true }),
}
```
