# Troubleshooting Guide

Common issues, error handling patterns, and debugging techniques for Axios.

## Error Codes Reference

### Network Errors

| Code | Cause | Solution |
|------|-------|----------|
| `ERR_NETWORK` | Network failure, CORS violation, or mixed content | Check browser console for CORS errors; verify network connectivity |
| `ECONNABORTED` | Request timeout or abort | Increase timeout value; check if request was manually canceled |
| `ETIMEDOUT` | Request exceeded timeout (requires `transitional.clarifyTimeoutError: true`) | Handle timeout specifically in error handler |
| `ERR_CANCELED` | Request was canceled via AbortSignal or CancelToken | Check cancellation logic; ensure controller isn't aborted prematurely |

### Configuration Errors

| Code | Cause | Solution |
|------|-------|----------|
| `ERR_BAD_OPTION_VALUE` | Invalid config value | Check parameter types and values |
| `ERR_BAD_OPTION` | Unknown config option | Verify option name spelling |
| `ERR_INVALID_URL` | Malformed URL | Validate URL format; use absolute URLs when needed |

### Response Errors

| Code | Cause | Solution |
|------|-------|----------|
| `ERR_BAD_RESPONSE` | Invalid response format or parsing error | Check server response; verify `responseType` setting |
| `ERR_BAD_REQUEST` | Invalid request format or missing parameters | Validate request data and headers |
| `ERR_FR_TOO_MANY_REDIRECTS` | Exceeded max redirects (default: 21) | Increase `maxRedirects` or fix redirect loop |

### Environment Errors

| Code | Cause | Solution |
|------|-------|----------|
| `ERR_NOT_SUPPORT` | Feature not supported in environment | Check browser/Node.js version; use polyfills if needed |
| `ERR_DEPRECATED` | Using deprecated API | Update to recommended alternative (e.g., AbortController instead of CancelToken) |

## Common Issues and Solutions

### CORS Errors

**Problem:** `Network Error` or CORS policy violation in browser console.

**Causes:**
- Server doesn't send proper CORS headers
- Preflight (OPTIONS) request failing
- Credentials mode mismatch

**Solutions:**

```javascript
// 1. Ensure server sends CORS headers:
// Access-Control-Allow-Origin: https://your-domain.com
// Access-Control-Allow-Credentials: true
// Access-Control-Allow-Methods: GET, POST, PUT, DELETE
// Access-Control-Allow-Headers: Content-Type, Authorization

// 2. Use withCredentials for cookies/auth headers
await axios.get('/api/protected', {
  withCredentials: true
});

// 3. For development, use proxy to avoid CORS
// webpack devServer.proxy or similar
```

**Check browser console:** CORS errors show detailed information about missing headers.

### Timeout Handling

**Problem:** Requests hang or fail silently on slow networks.

**Solution:**

```javascript
// Set appropriate timeout
const response = await axios.get('/api/slow-endpoint', {
  timeout: 30000 // 30 seconds
});

// Handle timeout specifically
try {
  await axios.get('/api/data', {
    timeout: 5000,
    transitional: {
      clarifyTimeoutError: true // Throws ETIMEDOUT instead of ECONNABORTED
    }
  });
} catch (error) {
  if (error.code === 'ETIMEDOUT') {
    console.error('Request timed out - retry or show user message');
    // Implement retry logic or user notification
  } else if (error.code === 'ECONNABORTED') {
    console.error('Request was aborted');
  }
}

// Retry with exponential backoff
async function fetchWithRetry(url, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await axios.get(url, { timeout: 5000 });
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      
      // Wait before retry (exponential backoff)
      await new Promise(resolve => 
        setTimeout(resolve, 1000 * Math.pow(2, i))
      );
    }
  }
}
```

### Request Cancellation Issues

**Problem:** Memory leaks from uncanceled requests in SPAs.

**Solution:**

```javascript
// React component example
function UserList() {
  const [users, setUsers] = useState([]);
  
  useEffect(() => {
    const controller = new AbortController();
    
    axios.get('/api/users', { signal: controller.signal })
      .then(res => setUsers(res.data))
      .catch(err => {
        if (err.code !== 'ERR_CANCELED') {
          console.error('Fetch error:', err);
        }
      });
    
    // Cleanup: cancel request on unmount
    return () => controller.abort();
  }, []);
  
  return <div>{users.map(u => <User key={u.id} user={u} />)}</div>;
}

// Vue 3 example
export default {
  setup() {
    const controller = new AbortController();
    
    onMounted(() => {
      axios.get('/api/data', { signal: controller.signal })
        .then(res => console.log(res.data));
    });
    
    onBeforeUnmount(() => {
      controller.abort();
    });
  }
};
```

### JSON Parsing Errors

**Problem:** `Unexpected token < in JSON at position 0` or silent failures.

**Solution:**

```javascript
// Ensure server returns proper Content-Type
// Server should send: Content-Type: application/json

// Check response before parsing
const response = await axios.get('/api/data', {
  responseType: 'json',
  transitional: {
    silentJSONParsing: false // Throw on JSON parse error (default in newer versions)
  }
});

// Handle HTML responses (e.g., from authentication redirects)
try {
  const response = await axios.get('/api/data');
} catch (error) {
  if (error.response && error.response.data.startsWith('<!DOCTYPE')) {
    console.error('Received HTML instead of JSON - possible auth redirect');
    window.location.href = '/login';
  }
}

// Manual parsing with error handling
const response = await axios.get('/api/data', {
  responseType: 'text',
  transformResponse: [(data) => {
    try {
      return JSON.parse(data);
    } catch (error) {
      console.error('JSON parse error:', error);
      throw new Error('Invalid JSON response');
    }
  }]
});
```

### FormData Upload Issues

**Problem:** Files not uploading or incorrect format.

**Solutions:**

```javascript
// Browser: Ensure you're getting the File object correctly
const fileInput = document.querySelector('#fileInput');
const file = fileInput.files[0]; // Get first file

if (!file) {
  console.error('No file selected');
  return;
}

const formData = new FormData();
formData.append('file', file);
formData.append('description', 'My upload');

// Don't set Content-Type manually - axios sets it with boundary
await axios.post('/upload', formData, {
  // headers: { 'Content-Type': 'multipart/form-data' } // WRONG!
  // Let axios set the boundary automatically
});

// Node.js: Use form-data package
const FormData = require('form-data');
const fs = require('fs');

const form = new FormData();
form.append('file', fs.createReadStream('/path/to/file.jpg'));

await axios.post('https://example.com/upload', form);
```

### Base URL Issues

**Problem:** URLs not resolving correctly with baseURL.

**Solutions:**

```javascript
// Correct baseURL usage
const instance = axios.create({
  baseURL: 'https://api.example.com/v1' // Trailing slash optional
});

await instance.get('/users'); // -> https://api.example.com/v1/users
await instance.get('users');  // -> https://api.example.com/v1/users

// Absolute URLs override baseURL by default
await instance.get('https://other-api.com/data'); // -> https://other-api.com/data

// Prevent absolute URL override
await instance.get('https://other-api.com/data', {
  allowAbsoluteUrls: false
}); // -> https://api.example.com/v1/https://other-api.com/data

// Leading slash matters
await instance.get('//users'); // Protocol-relative: https://users (WRONG!)
await instance.get('/users');  // Correct: https://api.example.com/v1/users
```

### Interceptor Issues

**Problem:** Interceptors not executing or wrong order.

**Solutions:**

```javascript
// Remember: Request interceptors execute LIFO (reverse order)
const instance = axios.create();

instance.interceptors.request.use(config => {
  console.log('Interceptor 1'); // Executes LAST
  return config;
});

instance.interceptors.request.use(config => {
  console.log('Interceptor 2'); // Executes FIRST
  return config;
});

// Response interceptors execute FIFO (normal order)
instance.interceptors.response.use(response => {
  console.log('Response 1'); // Executes FIRST
  return response;
});

instance.interceptors.response.use(response => {
  console.log('Response 2'); // Executes LAST
  return response;
});

// Always return config/response (or Promise)
instance.interceptors.request.use(config => {
  // WRONG: implicit undefined return
  config.headers['X-Custom'] = 'value';
  
  // CORRECT: explicit return
  return config;
});

// Error handling in interceptors
instance.interceptors.response.use(
  response => response,
  async error => {
    // Handle 401 token refresh
    if (error.response?.status === 401 && !error.config.__retry) {
      error.config.__retry = true;
      
      try {
        const newToken = await refreshToken();
        error.config.headers.Authorization = `Bearer ${newToken}`;
        return axios.request(error.config); // Retry with new token
      } catch (refreshError) {
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Remove interceptors to prevent duplicates
const interceptorId = instance.interceptors.request.use(config => config);
// Later...
instance.interceptors.request.eject(interceptorId);

// Clear all interceptors
instance.interceptors.request.clear();
instance.interceptors.response.clear();
```

### Proxy Configuration Issues

**Problem:** Requests not going through proxy or authentication failing.

**Solutions:**

```javascript
// Explicit proxy configuration
await axios.get('/api/data', {
  proxy: {
    protocol: 'http',
    host: 'proxy.example.com',
    port: 8080,
    auth: {
      username: 'proxy-user',
      password: 'proxy-pass'
    }
  }
});

// Environment variables (Node.js)
// http_proxy=http://proxy.example.com:8080
// https_proxy=https://proxy.example.com:8080
// no_proxy=.localhost,127.0.0.1

// Disable proxy
await axios.get('/api/data', {
  proxy: false
});

// HTTPS proxy
await axios.get('https://api.example.com/data', {
  proxy: {
    protocol: 'https',
    host: 'secure-proxy.example.com',
    port: 443
  }
});
```

### Headers Issues

**Problem:** Headers not being sent or overwritten.

**Solutions:**

```javascript
// Use AxiosHeaders for proper manipulation
import { AxiosHeaders } from 'axios';

const headers = new AxiosHeaders();
headers.set('Content-Type', 'application/json');
headers.set('Authorization', 'Bearer token');

await axios.get('/api/data', { headers });

// Case-insensitive header access
console.log(response.headers['content-type']);
console.log(response.headers['Content-Type']); // Same value
console.log(response.headers['CONTENT-TYPE']); // Same value

// Don't set Content-Type manually for FormData
const formData = new FormData();
formData.append('file', file);

await axios.post('/upload', formData, {
  // headers: { 'Content-Type': 'multipart/form-data' } // WRONG!
  // Axios automatically sets Content-Type with boundary parameter
});

// Disable default headers
axios.defaults.headers.common['User-Agent'] = false; // Prevent axios from setting it

// Override specific headers
await axios.get('/api/data', {
  headers: {
    'Accept': 'application/json' // Overrides default
  }
});
```

## Debugging Techniques

### Enable Request/Response Logging

```javascript
// Log all requests and responses
axios.interceptors.request.use(config => {
  console.log('Request:', {
    url: config.url,
    method: config.method,
    headers: config.headers,
    data: config.data
  });
  return config;
});

axios.interceptors.response.use(response => {
  console.log('Response:', {
    url: response.config.url,
    status: response.status,
    data: response.data
  });
  return response;
}, error => {
  console.error('Error:', {
    url: error.config?.url,
    status: error.response?.status,
    message: error.message,
    data: error.response?.data
  });
  return Promise.reject(error);
});
```

### Performance Monitoring

```javascript
axios.interceptors.request.use(config => {
  config.metadata = { startTime: Date.now() };
  return config;
});

axios.interceptors.response.use(response => {
  const duration = Date.now() - response.config.metadata.startTime;
  console.log(`${response.config.method} ${response.config.url}: ${duration}ms`);
  return response;
});
```

### Request ID Tracking

```javascript
function generateRequestId() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

axios.interceptors.request.use(config => {
  const requestId = generateRequestId();
  config.headers['X-Request-ID'] = requestId;
  config.metadata = { requestId };
  return config;
});

axios.interceptors.response.use(response => {
  console.log(`Request ${response.config.metadata.requestId} completed`);
  return response;
}, error => {
  const requestId = error.config?.metadata?.requestId;
  console.error(`Request ${requestId} failed:`, error.message);
  return Promise.reject(error);
});
```

## Migration from Axios 0.x to 1.x

### CancelToken → AbortController

**Old (deprecated):**
```javascript
const CancelToken = axios.CancelToken;
const source = CancelToken.source();

axios.get('/api/data', { cancelToken: source.token })
  .catch(thrown => {
    if (axios.isCancel(thrown)) {
      console.log('Canceled:', thrown.message);
    }
  });

source.cancel('User canceled');
```

**New (recommended):**
```javascript
const controller = new AbortController();

axios.get('/api/data', { signal: controller.signal })
  .catch(error => {
    if (error.code === 'ERR_CANCELED') {
      console.log('Canceled:', error.message);
    }
  });

controller.abort('User canceled');
```

### Headers Manipulation

**Old:**
```javascript
config.headers['Content-Type'] = 'application/json';
```

**New (recommended):**
```javascript
config.headers.set('Content-Type', 'application/json');
```

### Adapter Selection

**Old:** Automatic adapter selection based on environment.

**New:** Explicit adapter configuration available:
```javascript
axios.get('/api/data', { adapter: 'fetch' }); // Use fetch API
axios.get('/api/data', { adapter: ['xhr', 'http', 'fetch'] }); // Priority list
```

## Environment-Specific Issues

### React Native

```javascript
// React Native uses XMLHttpRequest by default
import axios from 'axios';

// For custom configurations
const api = axios.create({
  baseURL: 'https://api.example.com',
  timeout: 30000
});

// Note: Some features like rate limiting are Node.js only
```

### Server-Side Rendering (Next.js, Nuxt)

```javascript
// Create separate instances for client and server
import axios from 'axios';

// Server-side (Node.js http adapter)
const serverAxios = axios.create({
  baseURL: process.env.API_URL,
  timeout: 5000
});

// Client-side (browser XHR/fetch adapter)
export const clientAxios = axios.create({
  baseURL: '/api',
  withCredentials: true
});

// Use appropriate instance based on environment
const api = typeof window === 'undefined' ? serverAxios : clientAxios;
```

### Web Workers

```javascript
// Axios works in Web Workers
import axios from 'axios';

self.addEventListener('message', async (event) => {
  const response = await axios.get(event.data.url);
  self.postMessage(response.data);
});
```

## Performance Best Practices

### Reuse Instances

```javascript
// Create instance once and reuse
const api = axios.create({
  baseURL: 'https://api.example.com',
  timeout: 10000
});

// Don't create new instance for each request
// BAD: const response = await axios.create({ baseURL }).get('/users');
// GOOD: const response = await api.get('/users');
```

### Connection Pooling (Node.js)

```javascript
const http = require('http');
const https = require('https');

const api = axios.create({
  httpAgent: new http.Agent({ keepAlive: true }),
  httpsAgent: new https.Agent({ keepAlive: true })
});

// Enables connection reuse for better performance
```

### Request Debouncing

```javascript
function debounce(fn, delay) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn(...args), delay);
  };
}

const fetchUser = debounce(async (userId) => {
  const response = await axios.get(`/users/${userId}`);
  setUser(response.data);
}, 300); // Wait 300ms after last call
```
