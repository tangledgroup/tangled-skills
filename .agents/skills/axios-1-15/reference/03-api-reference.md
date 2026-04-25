# API Reference

Complete reference for Axios configuration options, instance methods, AxiosHeaders API, and adapter settings.

## Request Configuration

All available configuration options for axios requests:

```javascript
{
  // --- URL Configuration ---
  
  // Server URL (required)
  url: '/user',
  
  // Base URL prepended to relative URLs
  baseURL: 'https://api.example.com/',
  
  // Allow absolute URLs to override baseURL (default: true)
  allowAbsoluteUrls: true,
  
  // --- Request Method ---
  
  // HTTP method (default: 'get')
  method: 'get', // | 'post' | 'put' | 'patch' | 'delete' | 'head' | 'options'
  
  // --- Data and Headers ---
  
  // Request body data (for POST, PUT, PATCH, DELETE)
  // Types: string, plain object, ArrayBuffer, ArrayBufferView, URLSearchParams
  // Browser only: FormData, File, Blob
  // Node only: Stream, Buffer, FormData (form-data package)
  data: {
    firstName: 'Fred'
  },
  
  // Alternative syntax for POST body (string only)
  data: 'Country=Brasil&City=Belo Horizonte',
  
  // Custom headers object
  headers: {
    'X-Custom-Header': 'foobar',
    'Content-Type': 'application/json'
  },
  
  // URL query parameters (plain object or URLSearchParams)
  params: {
    ID: 12345,
    active: true
  },
  
  // Custom params serialization
  paramsSerializer: {
    encode: (param) => {
      // Custom encoding function for key/value pairs
      return encodeURIComponent(param);
    },
    serialize: (params, options) => {
      // Custom serializer for entire params object
      return myCustomSerializer(params, options);
    },
    indexes: false // null (no brackets), false (empty brackets), true (with indexes)
  },
  
  // --- Data Transformation ---
  
  // Transform request data before sending (array of functions)
  // Only applicable for PUT, POST, PATCH, DELETE
  transformRequest: [function (data, headers) {
    // Must return string, Buffer, ArrayBuffer, FormData, or Stream
    if (data && typeof data === 'object') {
      data = JSON.stringify(data);
    }
    return data;
  }],
  
  // Transform response data before returning (array of functions)
  transformResponse: [function (data) {
    if (typeof data === 'string') {
      data = JSON.parse(data);
    }
    return data;
  }],
  
  // --- Timeout and Retry ---
  
  // Request timeout in milliseconds (default: 0 = no timeout)
  timeout: 1000,
  
  // Maximum redirects to follow (Node.js, default: 21)
  maxRedirects: 21,
  
  // --- Authentication ---
  
  // HTTP Basic authentication
  auth: {
    username: 'janedoe',
    password: 's00pers3cret'
  },
  
  // --- Credentials and Cookies ---
  
  // Send cookies with cross-origin requests (default: false)
  withCredentials: false,
  
  // XSRF cookie name (default: 'XSRF-TOKEN')
  xsrfCookieName: 'XSRF-TOKEN',
  
  // XSRF header name (default: 'X-XSRF-TOKEN')
  xsrfHeaderName: 'X-XSRF-TOKEN',
  
  // Conditional XSRF token inclusion
  withXSRFToken: undefined | boolean | ((config) => boolean),
  
  // --- Response Handling ---
  
  // Expected response type (default: 'json')
  // Options: 'arraybuffer', 'blob', 'document', 'json', 'text', 'stream'
  responseType: 'json',
  
  // Response encoding for Node.js (ignored for stream responseType)
  // Options: 'ascii', 'base64', 'binary', 'hex', 'latin1', 'utf8', 'utf16le', etc.
  responseEncoding: 'utf8',
  
  // Custom status code validation function
  validateStatus: function (status) {
    return status >= 200 && status < 300; // default
  },
  
  // --- Progress Tracking ---
  
  // Upload progress handler (browser and Node.js)
  onUploadProgress: function ({ loaded, total, progress, bytes, estimated, rate, upload }) {
    const percent = Math.round((progress * 100));
    console.log(`Upload: ${percent}%`);
  },
  
  // Download progress handler (browser and Node.js)
  onDownloadProgress: function ({ loaded, total, progress, bytes, estimated, rate, download }) {
    const percent = Math.round((progress * 100));
    console.log(`Download: ${percent}%`);
  },
  
  // --- Cancellation ---
  
  // AbortSignal for request cancellation (recommended)
  signal: new AbortController().signal,
  
  // CancelToken (deprecated, use signal instead)
  cancelToken: new CancelToken(function (cancel) {
    // ...
  }),
  
  // --- Adapter Configuration ---
  
  // Custom adapter function or built-in adapter name
  // Options: 'xhr', 'http', 'fetch', or array like ['xhr', 'http', 'fetch']
  adapter: 'xhr',
  
  // --- Size Limits (Node.js) ---
  
  // Maximum response content size in bytes (default: 2000 * 1024)
  maxContentLength: 2000,
  
  // Maximum request body size in bytes (default: 2000 * 1024)
  maxBodyLength: 2000,
  
  // --- Rate Limiting (Node.js, http adapter only) ---
  
  // [uploadLimit, downloadLimit] in bytes per second
  maxRate: [
    100 * 1024, // 100 KB/s upload limit
    100 * 1024  // 100 KB/s download limit
  ],
  
  // --- Proxy Configuration ---
  
  // Proxy server configuration
  proxy: {
    protocol: 'http', // or 'https'
    host: '127.0.0.1', // or hostname: 'example.com'
    port: 9000,
    auth: {
      username: 'proxy-user',
      password: 'proxy-pass'
    }
  },
  
  // Disable proxy (ignore environment variables)
  proxy: false,
  
  // --- Unix Socket (Node.js) ---
  
  // Unix domain socket path (alternative to proxy)
  socketPath: null, // e.g., '/var/run/docker.sock'
  
  // --- Redirect Handling (Node.js) ---
  
  // Function called before each redirect
  beforeRedirect: function (options, { headers }) {
    // Modify options or throw error to cancel
    if (options.hostname === 'example.com') {
      options.auth = 'user:password';
    }
  },
  
  // --- HTTP Agent Configuration (Node.js) ---
  
  // Custom HTTP agent
  httpAgent: new http.Agent({ keepAlive: true }),
  
  // Custom HTTPS agent
  httpsAgent: new https.Agent({ keepAlive: true }),
  
  // --- Decompression (Node.js) ---
  
  // Auto-decompress response body (default: true)
  decompress: true,
  
  // --- HTTP Parser (Node.js) ---
  
  // Use insecure HTTP parser for non-conformant servers
  insecureHTTPParser: undefined,
  
  // --- Transport (Node.js) ---
  
  // Custom transport method
  transport: undefined,
  
  // --- HTTP/2 Options (Node.js, experimental) ---
  
  // HTTP version: 1.1 or 2
  httpVersion: 1.1,
  
  // HTTP/2 session options
  http2Options: {
    rejectUnauthorized: true,
    sessionTimeout: 1000
  },
  
  // --- Form Serialization ---
  
  // FormData class to use for automatic serialization
  env: {
    FormData: window?.FormData || global?.FormData
  },
  
  // Custom form serialization options
  formSerializer: {
    visitor: (value, key, path, helpers) => {},
    dots: false,        // Use dots instead of brackets
    metaTokens: true,   // Keep special endings like {}
    indexes: false      // Array index format
  },
  
  // --- Transitional Options (Backward Compatibility) ---
  
  transitional: {
    // Ignore JSON parsing errors (old behavior) vs throw SyntaxError
    silentJSONParsing: true,
    
    // Parse JSON even when responseType is not 'json'
    forcedJSONParsing: true,
    
    // Throw ETIMEDOUT instead of ECONNABORTED on timeout
    clarifyTimeoutError: false
  }
}
```

## Instance Methods

Methods available on axios instances (created via `axios.create()`):

```javascript
const instance = axios.create({ baseURL: 'https://api.example.com' });

// All instance methods accept config as second parameter
instance.request(config)
instance.get(url[, config])
instance.delete(url[, config])
instance.head(url[, config])
instance.options(url[, config])
instance.post(url[, data[, config]])
instance.put(url[, data[, config]])
instance.patch(url[, data[, config]])

// Get resolved URL without making request
instance.getUri([config])
```

### getUri() Method

```javascript
// Generate full URL with query parameters
const url = instance.getUri({
  url: '/user',
  params: { ID: 12345 }
});
// Returns: 'https://api.example.com/user?ID=12345'

// Use for pre-generating URLs (e.g., for <a> tags)
const downloadUrl = instance.getUri({
  url: '/files/document.pdf',
  responseType: 'blob'
});
```

## AxiosHeaders API

AxiosHeaders provides a Map-like interface for manipulating HTTP headers with case-insensitive access.

### Constructor

```javascript
import { AxiosHeaders } from 'axios';

// From object
const headers = new AxiosHeaders({
  'Content-Type': 'application/json',
  'Authorization': 'Bearer token'
});

// From string (raw HTTP headers)
const rawHeaders = `
Host: www.example.com
User-Agent: axios/1.0.0
Accept: */*`;
const headersFromString = new AxiosHeaders(rawHeaders);

// From existing AxiosHeaders
const copy = new AxiosHeaders(existingHeaders);
```

### Set Headers

```javascript
headers.set('Content-Type', 'application/json');
headers.set('X-Custom-Header', 'value');

// Set multiple headers at once
headers.set({
  'Accept': 'application/json',
  'Content-Type': 'application/json'
});

// With rewrite control
headers.set('User-Agent', 'axios/1.0', false); // Don't overwrite if exists
headers.set('User-Agent', 'axios/2.0', true);  // Force overwrite

// Disable header (won't be sent)
headers.set('User-Agent', false);

// With custom rewrite function
headers.set('Authorization', 'Bearer new-token', (value, name, headers) => {
  return value !== 'Bearer old-token';
});
```

### Get Headers

```javascript
// Get raw value
const contentType = headers.get('Content-Type'); // 'application/json'

// Case-insensitive access
const ct1 = headers.get('content-type');
const ct2 = headers.get('CONTENT-TYPE');
const ct3 = headers.get('Content-Type');
// All return the same value

// Parse key-value pairs from header value
const parsed = headers.get('Content-Type', true);
// { 'multipart/form-data': undefined, boundary: 'Asrf456BGe4h' }

// Parse with custom function
const modified = headers.get('Content-Type', (value) => {
  return value.toUpperCase();
});

// Parse with RegExp
const match = headers.get('Content-Type', /boundary=(\w+)/);
// ['boundary=Asrf456BGe4h', 'Asrf456BGe4h']
```

### Check and Delete Headers

```javascript
// Check if header exists
headers.has('Content-Type'); // true
headers.has('X-Missing');     // false

// Delete single header
headers.delete('Content-Type'); // true if deleted

// Delete multiple headers
headers.delete(['Content-Type', 'X-Custom']); // true if any deleted

// Clear all headers
headers.clear(); // true

// Clear matching headers (by name pattern)
headers.clear(/^X-/); // Removes all headers starting with 'X-'
```

### Normalize Headers

Combine duplicate keys with different cases:

```javascript
const headers = new AxiosHeaders({ foo: '1' });
headers.Foo = '2';
headers.FOO = '3';

console.log(headers.toJSON());
// { foo: '1', Foo: '2', FOO: '3' }

// Normalize to single key
headers.normalize();
console.log(headers.toJSON());
// { foo: '3' } (last value wins)

// Normalize with capitalization
headers.normalize(true);
console.log(headers.toJSON());
// { Foo: '3' }
```

### Concatenate Headers

```javascript
const headers1 = new AxiosHeaders({ 'Content-Type': 'application/json' });
const headers2 = { 'Authorization': 'Bearer token' };
const rawString = 'X-Custom: value';

const merged = headers1.concat(headers2, rawString);
// New AxiosHeaders instance with all headers combined

// Static method
const combined = AxiosHeaders.concat(headers1, headers2, rawString);
```

### Convert to Object

```javascript
// Get plain object with string values
const obj = headers.toJSON();
// { 'content-type': 'application/json', 'authorization': 'Bearer token' }

// Arrays as comma-separated strings
const objWithStrings = headers.toJSON(true);
// { 'set-cookie': 'a=1, b=2, c=3' }
```

### Static Methods

```javascript
// Create from raw headers or return as-is if already AxiosHeaders
const headers = AxiosHeaders.from(rawHeadersOrObject);

// Merge multiple header sources
const merged = AxiosHeaders.concat(headers1, headers2, rawString);
```

### Header Shortcuts

Convenience methods for common headers:

```javascript
// Content-Type
headers.setContentType('application/json');
headers.getContentType();
headers.hasContentType();

// Content-Length
headers.setContentLength(1234);
headers.getContentLength();
headers.hasContentLength();

// Accept
headers.setAccept('application/json');
headers.getAccept();
headers.hasAccept();

// User-Agent
headers.setUserAgent('axios/1.0');
headers.getUserAgent();
headers.hasUserAgent();

// Content-Encoding
headers.setContentEncoding('gzip');
headers.getContentEncoding();
headers.hasContentEncoding();
```

### Iterate Headers

```javascript
for (const [name, value] of headers) {
  console.log(`${name}: ${value}`);
}

// Convert to array
const entries = Array.from(headers.entries());
const keys = Array.from(headers.keys());
const values = Array.from(headers.values());
```

## Creating Instances

### Basic Instance Creation

```javascript
const instance = axios.create({
  baseURL: 'https://api.example.com',
  timeout: 10000,
  headers: {
    'X-Custom-Header': 'custom-value'
  }
});

// Use instance methods
instance.get('/users');
instance.post('/users', { name: 'John' });
```

### Instance with Defaults

```javascript
const apiClient = axios.create({
  baseURL: 'https://api.example.com/v1',
  timeout: 30000,
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  }
});

// Modify defaults after creation
apiClient.defaults.baseURL = 'https://api.example.com/v2';
apiClient.defaults.headers.common['Authorization'] = 'Bearer token';
```

### Multiple Instances Pattern

```javascript
// Public API (no auth)
const publicApi = axios.create({
  baseURL: 'https://api.example.com/public'
});

// Protected API (with auth)
const protectedApi = axios.create({
  baseURL: 'https://api.example.com/protected',
  headers: {
    'Authorization': `Bearer ${getToken()}`
  }
});

// Third-party API
const thirdPartyApi = axios.create({
  baseURL: 'https://third-party.com/api',
  timeout: 5000,
  validateStatus: (status) => status < 500
});
```

## Config Defaults Hierarchy

Configuration is merged in this order of precedence (lowest to highest):

1. **Library defaults** (`lib/defaults/index.js`)
2. **Instance defaults** (`instance.defaults`)
3. **Request config** (passed to individual requests)

```javascript
// 1. Library defaults (timeout: 0)
const instance = axios.create();

// 2. Instance defaults override library
instance.defaults.timeout = 2500; // All requests wait 2.5s

// 3. Request config overrides instance
instance.get('/slow-endpoint', {
  timeout: 5000 // This request waits 5s
});

// Headers merge strategy
axios.defaults.headers.common['Authorization'] = 'Bearer global-token';

const instance = axios.create({
  headers: {
    'Authorization': 'Bearer instance-token', // Overrides global
    'X-Custom': 'instance-custom'
  }
});

instance.get('/endpoint', {
  headers: {
    'X-Request': 'specific' // Added to instance headers
  }
});
// Final headers: Authorization (instance), X-Custom (instance), X-Request (specific)
```

## Adapter Configuration

### Built-in Adapters

```javascript
// Use specific adapter
axios.get('/api', { adapter: 'xhr' });    // Browser XMLHttpRequest
axios.get('/api', { adapter: 'http' });   // Node.js http/https
axios.get('/api', { adapter: 'fetch' });  // Fetch API

// Adapter priority array (first available wins)
axios.get('/api', { adapter: ['xhr', 'http', 'fetch'] });
```

### Custom Adapter

```javascript
const customAdapter = async (config) => {
  // Implement custom request logic
  const response = {
    data: await myCustomFetch(config.url, config),
    status: 200,
    statusText: 'OK',
    headers: {},
    config,
    request: {}
  };
  
  return response;
};

const instance = axios.create({
  adapter: customAdapter
});
```

### Fetch Adapter Customization

```javascript
import customFetch from 'custom-fetch';

const instance = axios.create({
  adapter: 'fetch',
  env: {
    fetch: customFetch,      // Custom fetch function
    Request: CustomRequest,  // Optional custom Request constructor
    Response: CustomResponse // Optional custom Response constructor
  }
});

// Disable progress tracking if custom fetch incompatible
const noProgressInstance = axios.create({
  adapter: 'fetch',
  env: {
    fetch: customFetch,
    Request: null, // Disable built-in Request
    Response: null // Disable built-in Response
  }
});
```

## TypeScript Support

### Basic Type Usage

```typescript
import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

// Generic response type
type User = { id: number; name: string };

async function getUser(id: number): Promise<User> {
  const response: AxiosResponse<User> = await axios.get(`/users/${id}`);
  return response.data;
}

// Error handling with type guard
try {
  const user = await getUser(123);
} catch (error) {
  if (axios.isAxiosError(error)) {
    if (error.response) {
      console.error('HTTP error:', error.response.status);
    }
  } else {
    console.error('Unexpected error:', error);
  }
}
```

### Typed Instances

```typescript
import axios, { InternalAxiosRequestConfig } from 'axios';

interface ApiConfig {
  baseURL: string;
  timeout: number;
}

const apiClient: AxiosInstance = axios.create({
  baseURL: 'https://api.example.com',
  timeout: 10000
});

// Typed interceptors
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  config.headers['X-Request-ID'] = generateRequestId();
  return config;
});
```

### Response Type Configuration

```typescript
// Specify response type
const textResponse = await axios.get<string>('/data', {
  responseType: 'text'
});

const blobResponse = await axios.get<Blob>('/file.pdf', {
  responseType: 'blob'
});
```
