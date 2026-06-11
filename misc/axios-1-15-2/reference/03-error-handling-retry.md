# Error Handling & Retry

## AxiosError Structure

All axios errors are instances of `AxiosError` with the following properties:

- `message` — summary of the error
- `name` — always `"AxiosError"`
- `stack` — stack trace
- `config` — the full config used for the failed request
- `code` — axios-specific error code
- `status` — HTTP response status code (if the server responded)
- `request` — underlying request object (XMLHttpRequest or http.ClientRequest)
- `response` — the full response object (if the server responded with a non-2xx status)

### Error Codes

- `ERR_BAD_OPTION_VALUE` — invalid or unsupported config value
- `ERR_BAD_OPTION` — invalid config option
- `ECONNABORTED` — request timed out or aborted (unless `transitional.clarifyTimeoutError` is set)
- `ETIMEDOUT` — request timed out (requires `transitional.clarifyTimeoutError: true`)
- `ERR_NETWORK` — network error, CORS violation, or mixed content policy
- `ERR_FR_TOO_MANY_REDIRECTS` — exceeded max redirects
- `ERR_DEPRECATED` — deprecated feature used
- `ERR_BAD_RESPONSE` — response cannot be parsed (usually 5xx)
- `ERR_BAD_REQUEST` — request has unexpected format (usually 4xx)
- `ERR_CANCELED` — request cancelled via AbortSignal or CancelToken
- `ERR_NOT_SUPPORT` — feature not supported in current environment
- `ERR_INVALID_URL` — invalid URL

## Handling Errors

### Promise-based Error Handling

```js
axios.get("/user/12345").catch((error) => {
  if (error.response) {
    // Server responded with a status outside 2xx range
    console.log(error.response.data);
    console.log(error.response.status);
    console.log(error.response.headers);
  } else if (error.request) {
    // Request was made but no response received
    console.log(error.request);
  } else {
    // Something happened setting up the request
    console.log("Error", error.message);
  }
  console.log(error.config);
});
```

### async/await Error Handling

```js
async function fetchUser(id) {
  try {
    const response = await axios.get(`/api/users/${id}`);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error("Status:", error.response?.status);
      console.error("Data:", error.response?.data);
    }
    throw error;
  }
}
```

### Error as JSON

```js
axios.get("/user/12345").catch((error) => {
  console.log(error.toJSON());
});
```

## Cancellation

### AbortController (Recommended)

Use the standard `AbortController` API to cancel requests:

```js
const controller = new AbortController();

axios
  .get("/foo/bar", { signal: controller.signal })
  .then((response) => {
    // handle response
  });

// Cancel the request
controller.abort();
```

Check for cancellation in error handlers:

```js
try {
  await axios.get("/api/data", { signal: controller.signal });
} catch (error) {
  if (axios.isCancel(error)) {
    console.log("Request canceled:", error.message);
  }
}
```

One AbortController can cancel multiple requests. If the signal is already aborted when the request starts, it fails immediately without attempting a network call.

### CancelToken (Deprecated)

The legacy `CancelToken` API is deprecated and will be removed in the next major release. Use `AbortController` instead.

```js
const CancelToken = axios.CancelToken;
const source = CancelToken.source();

axios.get("/user/12345", { cancelToken: source.token });
source.cancel("Operation canceled by the user.");
```

## Retry Strategies

### Basic Retry

Retry transient failures (network errors, 5xx) a limited number of times using a response interceptor:

```js
const api = axios.create({ baseURL: "https://api.example.com" });
const MAX_RETRIES = 3;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;

    const shouldRetry =
      !error.response ||
      (error.response.status >= 500 && error.response.status < 600);

    if (!shouldRetry) return Promise.reject(error);

    config._retryCount = config._retryCount ?? 0;
    if (config._retryCount >= MAX_RETRIES) return Promise.reject(error);

    config._retryCount += 1;
    return api(config);
  }
);
```

### Exponential Backoff

Wait progressively longer between retries to avoid overwhelming a struggling server:

```js
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;

    const shouldRetry =
      !error.response ||
      (error.response.status >= 500 && error.response.status < 600);

    if (!shouldRetry) return Promise.reject(error);

    config._retryCount = config._retryCount ?? 0;
    if (config._retryCount >= 3) return Promise.reject(error);

    config._retryCount += 1;

    // Wait 200ms, 400ms, 800ms...
    const backoff = 100 * 2 ** config._retryCount;
    await delay(backoff);

    return api(config);
  }
);
```

### Retry on 429 (Rate Limit)

Respect the `Retry-After` header when the server returns 429:

```js
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;

    if (error.response?.status !== 429) return Promise.reject(error);

    config._retryCount = config._retryCount ?? 0;
    if (config._retryCount >= 3) return Promise.reject(error);

    config._retryCount += 1;

    const retryAfter = error.response.headers["retry-after"];
    const waitMs = retryAfter ? parseFloat(retryAfter) * 1000 : 1000;

    await new Promise((resolve) => setTimeout(resolve, waitMs));
    return api(config);
  }
);
```

### Opting Out of Retries

Prevent specific requests from being retried (useful for non-idempotent mutations):

```js
// In your retry interceptor, add:
if (config._noRetry) return Promise.reject(error);

// Then opt out on specific calls:
await api.post("/payments/charge", body, { _noRetry: true });
```

### Combining Retry with Cancellation

Use `AbortController` to cancel a request that is waiting for a backoff delay:

```js
const controller = new AbortController();

try {
  await api.get("/api/data", { signal: controller.signal });
} catch (error) {
  if (axios.isCancel(error)) {
    console.log("Request aborted by user");
  }
}

// Cancel from elsewhere:
controller.abort();
```
