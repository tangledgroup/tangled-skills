# Networking and HTTP

## http — HTTP Server

### Basic Server

```javascript
import http from 'node:http';

const server = http.createServer((req, res) => {
  const { method, url, headers } = req;

  // Parse URL
  const parsedUrl = new URL(url, `http://${headers.host}`);

  // Route handling
  if (parsedUrl.pathname === '/api/data' && method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ message: 'Hello' }));
  } else if (parsedUrl.pathname === '/api/submit' && method === 'POST') {
    let body = '';
    req.on('data', (chunk) => { body += chunk; });
    req.on('end', () => {
      const data = JSON.parse(body);
      res.writeHead(201, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ received: data }));
    });
  } else {
    res.writeHead(404);
    res.end('Not Found');
  }
});

server.listen(3000, () => {
  console.log('Server running at http://localhost:3000');
});

// Graceful shutdown
process.on('SIGTERM', () => {
  server.close(() => {
    console.log('HTTP server closed');
    process.exit(0);
  });
});
```

### Reading Request Body

```javascript
import http from 'node:http';

function getRequestBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', (chunk) => { body += chunk; });
    req.on('end', () => resolve(body));
    req.on('error', reject);
  });
}

const server = http.createServer(async (req, res) => {
  const body = await getRequestBody(req);
  const data = JSON.parse(body);
  res.end(JSON.stringify({ echo: data }));
});
```

### HTTP Agent and Keep-Alive

```javascript
import http from 'node:http';

// Reuse connections for multiple requests
const agent = new http.Agent({
  keepAlive: true,
  maxSockets: 50,
});

const req = http.request({
  hostname: 'api.example.com',
  path: '/data',
  agent, // reuse connection
}, (res) => {
  let data = '';
  res.on('data', (chunk) => { data += chunk; });
  res.on('end', () => console.log(data));
});
req.end();
```

### Timeouts

```javascript
const server = http.createServer((req, res) => {
  res.setTimeout(5000, () => {
    res.end('Request took too long');
  });
  // process request...
});

// Client timeout
const req = http.request('http://example.com', { timeout: 5000 }, (res) => {
  // handle response
});
req.on('timeout', () => {
  req.destroy(new Error('Request timed out'));
});
```

## https — HTTPS Server

```javascript
import https from 'node:https';
import fs from 'node:fs/promises';

const server = https.createServer({
  key: await fs.readFile('server-key.pem'),
  cert: await fs.readFile('server-cert.pem'),
  // Optional: CA chain for intermediate certificates
  ca: await fs.readFile('ca-cert.pem'),
}, (req, res) => {
  res.writeHead(200);
  res.end('Secure response');
});

server.listen(443);
```

### Self-Signed Certificate (Development)

```javascript
import crypto from 'node:crypto';

// Generate a self-signed cert at runtime
const { privateKey, publicKey } = crypto.generateKeyPairSync('rsa', {
  modulusLength: 2048,
});
// For production, use proper certificate authorities
```

## http2 — HTTP/2

### HTTP/2 Server

```javascript
import http2 from 'node:http2';
import fs from 'node:fs/promises';

const server = http2.createServer({
  key: await fs.readFile('server-key.pem'),
  cert: await fs.readFile('server-cert.pem'),
});

server.on('stream', (stream, headers) => {
  stream.respond({
    'content-type': 'text/plain',
    ':status': 200,
  });
  stream.end('Hello World');
});

server.listen(8443);
```

### HTTP/2 Client

```javascript
import http2 from 'node:http2';

const client = http2.connect('https://example.com');
const request = client.request({ ':path': '/api/data' });

let data = '';
request.on('data', (chunk) => { data += chunk; });
request.on('end', () => {
  console.log(data);
  client.close();
});
request.end();
```

### HTTP/2 Compatibility API

```javascript
import http2 from 'node:http2';

// Works like http module but upgrades to HTTP/2 when possible
const server = http2.createSecureServer({ key, cert });

server.on('request', (req, res) => {
  // Same API as http
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ hello: 'world' }));
});
```

## fetch — Built-in HTTP Client

Node.js includes the Web Fetch API (no npm package needed):

```javascript
// GET request
const response = await fetch('https://api.example.com/data');
const json = await response.json();

// POST with JSON body
const postResponse = await fetch('https://api.example.com/users', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: 'Alice', email: 'alice@example.com' }),
});

// POST with form data
const formData = new FormData();
formData.append('name', 'Alice');
formData.append('file', new Blob([fileContent], { type: 'text/plain' }), 'file.txt');

const formResponse = await fetch('https://api.example.com/upload', {
  method: 'POST',
  body: formData,
});

// With timeout
const controller = new AbortController();
setTimeout(() => controller.abort(), 5000);
const timedResponse = await fetch('https://api.example.com/slow', {
  signal: controller.signal,
});

// Follow redirects (default: 'follow')
const noRedirect = await fetch('https://example.com', { redirect: 'manual' });

// Read response as stream
const streamResponse = await fetch('https://example.com/large-file');
for await (const chunk of streamResponse.body) {
  process.stdout.write(chunk);
}
```

### Headers API

```javascript
const headers = new Headers();
headers.set('Content-Type', 'application/json');
headers.append('Accept', 'text/plain');
headers.get('Content-Type');      // 'application/json'
headers.has('Authorization');     // false
headers.delete('Accept');
headers.entries();                // iterator
```

## EventSource — Server-Sent Events (SSE)

```javascript
// Client
const eventSource = new EventSource('https://example.com/events');
eventSource.addEventListener('message', (event) => {
  console.log('Message:', event.data);
});
eventSource.addEventListener('alert', (event) => {
  console.log('Alert:', event.data);
});
eventSource.onerror = (err) => {
  console.error('SSE error');
  eventSource.close();
};

// Server (manual SSE implementation)
import http from 'node:http';

const server = http.createServer((req, res) => {
  if (req.url === '/events') {
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    });

    // Send events periodically
    const interval = setInterval(() => {
      res.write(`data: ${JSON.stringify({ time: Date.now() })}\n\n`);
    }, 1000);

    req.on('close', () => {
      clearInterval(interval);
    });
  }
});
```

## net — TCP

### TCP Server with Multiple Clients

```javascript
import net from 'node:net';

const server = net.createServer((socket) => {
  console.log('Client connected:', socket.remoteAddress);

  socket.setEncoding('utf-8');
  socket.write('Welcome! Type "quit" to exit.\n');

  let buffer = '';
  socket.on('data', (data) => {
    buffer += data;
    const lines = buffer.split('\n');
    buffer = lines.pop(); // keep incomplete line

    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed === 'quit') {
        socket.end('Goodbye!\n');
        return;
      }
      socket.write(`Echo: ${trimmed}\n`);
    }
  });

  socket.on('end', () => console.log('Client disconnected'));
  socket.on('error', (err) => console.error('Socket error:', err));
});

server.listen(8124, () => console.log('TCP server on port 8124'));
```

### TCP Client with Reconnection

```javascript
import net from 'node:net';

function connectWithRetry(port, host = 'localhost', maxRetries = 5) {
  let retries = 0;

  function connect() {
    const socket = new net.Socket();

    socket.connect(port, host, () => {
      console.log('Connected');
      retries = 0;
    });

    socket.on('error', (err) => {
      console.error(`Connection error (${retries + 1}/${maxRetries}):`, err.message);
      retries++;
      if (retries < maxRetries) {
        setTimeout(connect, 1000 * Math.min(2 ** retries, 30000));
      } else {
        console.error('Max retries reached');
      }
    });

    return socket;
  }

  return connect();
}
```

### TLS/TCP Combined

```javascript
import tls from 'node:tls';
import fs from 'node:fs/promises';

// TLS Server
const server = tls.createServer({
  key: await fs.readFile('key.pem'),
  cert: await fs.readFile('cert.pem'),
}, (socket) => {
  socket.write('Secure connection established\n');
  socket.pipe(socket); // echo
});
server.listen(8443);

// TLS Client
const socket = tls.connect(8443, {
  rejectUnauthorized: false, // only for dev!
}, () => {
  console.log('Connected:', socket.authorized ? 'authorized' : 'NOT authorized');
  console.log('Cipher:', socket.getCipher().name);
  console.log('Protocol:', socket.getProtocol());
});
socket.pipe(process.stdout);
process.stdin.pipe(socket);
```

## dns — DNS

### Resolution Methods

```javascript
import dns from 'node:dns';

// Lookup (uses system config, may use cache)
const { address, family } = await dns.promises.lookup('google.com');

// resolve4 — A records
const ips = await dns.promises.resolve4('google.com');

// resolve6 — AAAA records
const ipv6s = await dns.promises.resolve6('google.com');

// resolveMx — mail servers
const mx = await dns.promises.resolveMx('gmail.com');

// resolveTxt — text records
const txt = await dns.promises.resolveTxt('google.com');

// resolveNs — name servers
const ns = await dns.promises.resolveNs('google.com');

// resolveCname — canonical names
const cnames = await dns.promises.resolveCname('www.google.com');

// Reverse DNS
const hostnames = await dns.promises.reverse('8.8.8.8');

// Any record type
const any = await dns.promises.resolveAny('google.com');
```

### Custom DNS Resolver

```javascript
import { Resolver } from 'node:dns';

const resolver = new Resolver();
resolver.setServers(['1.1.1.1', '9.9.9.9']); // Cloudflare + Quad9

const addresses = await resolver.resolve4('example.com');
```

### Result Order

```javascript
// Prefer IPv4 or IPv6
dns.promises.setDefaultResultOrder('ipv4first');
dns.promises.setDefaultResultOrder('ipv6first');
```

## dgram — UDP

```javascript
import dgram from 'node:dgram';

// Server
const server = dgram.createSocket('udp4');
server.on('message', (msg, rinfo) => {
  console.log(`Got ${msg.length} bytes from ${rinfo.address}:${rinfo.port}`);
  server.send('ACK', rinfo.port, rinfo.address);
});
server.on('error', (err) => console.error('UDP error:', err));
server.bind(41234, () => console.log(`UDP server on port ${server.address().port}`));

// Client
const client = dgram.createSocket('udp4');
client.send('hello world', 41234, 'localhost', (err) => {
  if (err) console.error('Send error:', err);
  client.close();
});
```
