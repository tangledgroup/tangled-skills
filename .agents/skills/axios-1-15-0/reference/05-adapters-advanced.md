# Adapters & Advanced Features

## Adapters

Adapters control how axios makes the actual HTTP request. By default, axios uses a priority list of `["xhr", "http", "fetch"]` and selects the first one supported by the environment:

- **Browser** → `xhr` (XMLHttpRequest)
- **Node.js** → `http` (native http/https modules)
- **Other** → `fetch` (Cloudflare Workers, Deno, etc.)

### Built-in Adapters

Select explicitly via the `adapter` config option:

```js
// Use fetch adapter
const instance = axios.create({ adapter: "fetch" });

// Use xhr adapter (browser default)
const instance = axios.create({ adapter: "xhr" });

// Use http adapter (Node.js default)
const instance = axios.create({ adapter: "http" });

// Try in order, use first available
const instance = axios.create({ adapter: ["fetch", "xhr", "http"] });
```

### Custom Adapters

Write a function that accepts a `config` object and returns a Promise resolving to a valid axios response:

```js
import { settle } from "axios/unsafe/core/settle.js";

function myAdapter(config) {
  return new Promise((resolve, reject) => {
    fetch(config.url, {
      method: config.method?.toUpperCase() ?? "GET",
      headers: config.headers?.toJSON() ?? {},
      body: config.data,
      signal: config.signal,
    })
      .then(async (fetchResponse) => {
        const responseData = await fetchResponse.text();

        const response = {
          data: responseData,
          status: fetchResponse.status,
          statusText: fetchResponse.statusText,
          headers: Object.fromEntries(fetchResponse.headers.entries()),
          config,
          request: null,
        };

        // settle resolves for 2xx, rejects otherwise
        settle(resolve, reject, response);
      })
      .catch(reject);
  });
}

const instance = axios.create({ adapter: myAdapter });
```

> The `settle` helper resolves the promise for 2xx status codes and rejects for everything else, matching axios's default behavior. For custom status validation, use the `validateStatus` config option.

## Fetch Adapter

The fetch adapter (v1.7.0+) provides first-class Fetch API support with the same axios interface as xhr. It supports upload/download progress capturing and additional response types (`stream`, `formdata`).

### Enabling the Fetch Adapter

```js
const instance = axios.create({ adapter: "fetch" });
```

### Custom Fetch (v1.12.0+)

Pass a custom `fetch` function via the `env` config option:

```js
const instance = axios.create({
  adapter: "fetch",
  env: {
    fetch: customFetchFunction,
    Request: null, // null disables the constructor
    Response: null,
  },
});
```

> When using a custom `fetch`, you may need matching `Request` and `Response` constructors. Setting them to `null` disables upload/download progress capturing.

### Using with Tauri

Tauri provides a platform `fetch` that bypasses browser CORS:

```js
import { fetch } from "@tauri-apps/plugin-http";
import axios from "axios";

const instance = axios.create({
  adapter: "fetch",
  env: { fetch },
});

const { data } = await instance.get("https://google.com");
```

### Using with SvelteKit

SvelteKit's server-side `fetch` handles cookie forwarding and relative URLs:

```js
export async function load({ fetch }) {
  const { data: post } = await axios.get(
    "https://jsonplaceholder.typicode.com/posts/1",
    {
      adapter: "fetch",
      env: {
        fetch,
        Request: null,
        Response: null,
      },
    }
  );

  return { post };
}
```

## HTTP/2

Experimental HTTP/2 support in the `http` adapter (v1.13.0+, Node.js only).

### Basic Usage

```js
const { data } = await axios.post("https://httpbin.org/post", formData, {
  httpVersion: 2,
});
```

### HTTP/2 Options

```js
{
  httpVersion: 2,
  http2Options: {
    rejectUnauthorized: false, // accept self-signed certs (dev only)
    sessionTimeout: 5000,      // keep idle session alive for 5 seconds
  },
}
```

### Full Example with Progress

```js
const form = new FormData();
form.append("foo", "123");

const { data } = await axios.post("https://httpbin.org/post", form, {
  httpVersion: 2,
  http2Options: { sessionTimeout: 5000 },
  onUploadProgress: (e) => console.log("upload", e),
  onDownloadProgress: (e) => console.log("download", e),
  responseType: "arraybuffer",
});
```

> HTTP/2 support is experimental. The API may change in future releases.

## Testing

### Mocking with Vitest or Jest

Mock the axios module at the module level:

```js
// user-service.js
import axios from "axios";

export async function getUser(id) {
  const { data } = await axios.get(`/api/users/${id}`);
  return data;
}
```

```js
// user-service.test.js
import { describe, it, expect, vi } from "vitest";
import axios from "axios";
import { getUser } from "./user-service";

vi.mock("axios");

describe("getUser", () => {
  it("returns user data on success", async () => {
    const mockUser = { id: 1, name: "Jay" };
    axios.get.mockResolvedValueOnce({ data: mockUser });

    const result = await getUser(1);

    expect(result).toEqual(mockUser);
    expect(axios.get).toHaveBeenCalledWith("/api/users/1");
  });

  it("throws when the request fails", async () => {
    axios.get.mockRejectedValueOnce(new Error("Network error"));
    await expect(getUser(1)).rejects.toThrow("Network error");
  });
});
```

### Mocking AxiosError

```js
import { AxiosError } from "axios";

const mockError = new AxiosError(
  "Not Found",
  "ERR_BAD_REQUEST",
  {},   // config
  {},   // request
  {     // response
    status: 404,
    statusText: "Not Found",
    data: { message: "User not found" },
    headers: {},
    config: {},
  }
);

axios.get.mockRejectedValueOnce(mockError);
```

### Using axios-mock-adapter

`axios-mock-adapter` installs a custom adapter, so interceptors still run — better for integration tests:

```js
import axios from "axios";
import MockAdapter from "axios-mock-adapter";

const mock = new MockAdapter(axios);

mock.onGet("/api/users/1").reply(200, { id: 1, name: "Jay" });
mock.onPost("/api/users").reply(201, { id: 2, name: "New User" });
mock.onGet("/api/failing").networkError();
mock.onGet("/api/slow").timeout();

// Reset between tests
afterEach(() => { mock.reset(); });
```

### Testing Interceptors

Create a fresh instance per test:

```js
import axios from "axios";
import MockAdapter from "axios-mock-adapter";

describe("auth interceptor", () => {
  it("attaches a Bearer token to every request", async () => {
    const instance = axios.create();
    const mock = new MockAdapter(instance);

    instance.interceptors.request.use((config) => {
      config.headers.set("Authorization", "Bearer test-token");
      return config;
    });

    let capturedConfig;
    mock.onGet("/api/data").reply((config) => {
      capturedConfig = config;
      return [200, {}];
    });

    await instance.get("/api/data");
    expect(capturedConfig.headers["Authorization"]).toBe("Bearer test-token");
  });
});
```

### Testing Tips

- Always mock at the module level or use `MockAdapter` — avoid mocking individual methods on a shared instance
- Use `mockResolvedValueOnce` / `mockRejectedValueOnce` for test isolation
- When testing retry logic, use `MockAdapter` so interceptors run on each attempt

## TypeScript

Axios includes type definitions (`index.d.ts`) in the npm package.

### Recommended tsconfig Settings

```json
{
  "compilerOptions": {
    "moduleResolution": "node16"
  }
}
```

- `"moduleResolution": "node16"` is recommended (requires TypeScript 4.7+)
- For ESM projects, default settings are usually sufficient
- For CJS compilation without `node16`, enable `esModuleInterop`
- When type-checking CJS JavaScript code, use `"moduleResolution": "node16"`

### Type Imports

```ts
import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from "axios";

async function fetchUser(id: number): Promise<AxiosResponse<User>> {
  return axios.get(`/api/users/${id}`);
}
```

## Promises

Axios is built on the native ES6 Promise API. Every request returns a standard Promise.

### then / catch / finally

```js
axios.get("/api/users")
  .then((response) => console.log(response.data))
  .catch((error) => console.error("Failed:", error.message))
  .finally(() => console.log("Request finished"));
```

### Chaining Requests

Pass data from one request to the next:

```js
axios.get("/api/user/1")
  .then(({ data: user }) => axios.get(`/api/posts?userId=${user.id}`))
  .then(({ data: posts }) => console.log("Posts:", posts))
  .catch(console.error);
```
