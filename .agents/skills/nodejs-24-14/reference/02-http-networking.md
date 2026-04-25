# HTTP and Networking Reference

This document covers Node.js 24.14 networking APIs including HTTP/1.1, HTTP/2, HTTPS, TCP, UDP, and DNS.

## HTTP Module (HTTP/1.1)

### Creating an HTTP Server

```javascript
import http from 'node:http';

const server = http.createServer((req, res) => {
  // req: IncomingMessage (request object)
  // res: ServerResponse (response object)
  
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('Hello World\n');
});

server.listen(3000, () => {
  console.log('Server running on http://localhost:3000');
});
```

### Request Object (IncomingMessage)

Properties available on `req`:

```javascript
import http from 'node:http';

http.createServer((req, res) => {
  // Request method: GET, POST, PUT, DELETE, etc.
  console.log('Method:', req.method);
  
  // URL path with query string
  console.log('URL:', req.url);
  
  // Request headers (all lowercase)
  console.log('Headers:', req.headers);
  console.log('Content-Type:', req.headers['content-type']);
  
  // HTTP version: '1.1', '2.0'
  console.log('HTTP Version:', req.httpVersion);
  
  // Remote address and port
  console.log('Client:', req.socket.remoteAddress);
  
  // Check if request was upgraded (e.g., to WebSocket)
  console.log('Upgraded:', req.upgrade);
}).listen(3000);
```

### Response Object (ServerResponse)

Common methods on `res`:

```javascript
import http from 'node:http';

http.createServer((req, res) => {
  // Set status code and headers
  res.writeHead(200, {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength('{"hello":"world"}'),
    'Cache-Control': 'no-cache'
  });
  
  // Or use shortcut methods
  res.statusCode = 200;
  res.setHeader('Content-Type', 'application/json');
  
  // Send response body
  res.end('{"hello":"world"}');
  
  // Alternative: write in chunks
  res.write('Part 1\n');
  res.write('Part 2\n');
  res.end('Part 3\n');
  
  // Check if headers were sent
  console.log('Headers sent:', res.headersSent);
}).listen(3000);
```

### Handling Request Body

#### JSON Body Parsing

```javascript
import http from 'node:http';

function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    
    req.on('data', chunk => {
      body += chunk.toString();
    });
    
    req.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (err) {
        reject(err);
      }
    });
    
    req.on('error', reject);
  });
}

http.createServer(async (req, res) => {
  if (req.method === 'POST') {
    try {
      const body = await parseBody(req);
      console.log('Received:', body);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ received: body }));
    } catch (err) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Invalid JSON' }));
    }
  } else {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('Send POST request with JSON body');
  }
}).listen(3000);
```

#### Streaming Body Handling

```javascript
import http from 'node:http';
import fs from 'node:fs';

http.createServer((req, res) => {
  if (req.method === 'POST' && req.url === '/upload') {
    // Pipe request body directly to file
    const writeStream = fs.createWriteStream('upload.txt');
    
    req.pipe(writeStream);
    
    writeStream.on('finish', () => {
      res.writeHead(200, { 'Content-Type': 'text/plain' });
      res.end('File uploaded successfully');
    });
    
    writeStream.on('error', (err) => {
      res.writeHead(500, { 'Content-Type': 'text/plain' });
      res.end('Upload failed: ' + err.message);
    });
  } else {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('POST to /upload to upload a file');
  }
}).listen(3000);
```

### HTTP Client Requests

#### Basic GET Request

```javascript
import http from 'node:http';

function get(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let data = '';
      
      res.on('data', chunk => {
        data += chunk;
      });
      
      res.on('end', () => {
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          body: data
        });
      });
    }).on('error', reject);
  });
}

// Usage
try {
  const response = await get('http://example.com');
  console.log('Status:', response.statusCode);
  console.log('Body:', response.body);
} catch (err) {
  console.error('Request failed:', err.message);
}
```

#### POST Request with JSON

```javascript
import http from 'node:http';

function postJson(url, data) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify(data);
    
    const options = {
      hostname: new URL(url).hostname,
      path: new URL(url).pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body)
      }
    };
    
    const req = http.request(options, (res) => {
      let responseData = '';
      
      res.on('data', chunk => {
        responseData += chunk;
      });
      
      res.on('end', () => {
        try {
          resolve({
            statusCode: res.statusCode,
            headers: res.headers,
            body: JSON.parse(responseData)
          });
        } catch {
          resolve({
            statusCode: res.statusCode,
            headers: res.headers,
            body: responseData
          });
        }
      });
    });
    
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

// Usage
try {
  const response = await postJson('http://example.com/api/users', {
    name: 'John Doe',
    email: 'john@example.com'
  });
  console.log('Created user:', response.body);
} catch (err) {
  console.error('Request failed:', err.message);
}
```

#### Streaming Large Responses

```javascript
import http from 'node:http';
import fs from 'node:fs';

function downloadToFile(url, filepath) {
  return new Promise((resolve, reject) => {
    const writeStream = fs.createWriteStream(filepath);
    
    http.get(url, (res) => {
      // Check status code
      if (res.statusCode !== 200) {
        res.resume(); // Consume response data to free up memory
        reject(new Error(`Request failed with status ${res.statusCode}`));
        return;
      }
      
      // Pipe response to file
      res.pipe(writeStream);
      
      writeStream.on('finish', () => {
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          path: filepath
        });
      });
    }).on('error', reject);
    
    writeStream.on('error', reject);
  });
}

// Usage
try {
  const result = await downloadToFile(
    'http://example.com/large-file.zip',
    '/tmp/download.zip'
  );
  console.log('Downloaded to:', result.path);
} catch (err) {
  console.error('Download failed:', err.message);
}
```

### Request Timeout and Cancellation

```javascript
import http from 'node:http';

function getWithTimeout(url, timeoutMs = 5000) {
  return new Promise((resolve, reject) => {
    const req = http.get(url, (res) => {
      let data = '';
      
      res.on('data', chunk => {
        data += chunk;
      });
      
      res.on('end', () => {
        clearTimeout(timeout);
        resolve({ statusCode: res.statusCode, body: data });
      });
    });
    
    req.on('error', (err) => {
      clearTimeout(timeout);
      reject(err);
    });
    
    const timeout = setTimeout(() => {
      req.destroy();
      reject(new Error('Request timeout'));
    }, timeoutMs);
  });
}

// Usage with AbortController (Node.js 15+)
function getWithAbort(url) {
  const controller = new AbortController();
  
  const promise = new Promise((resolve, reject) => {
    const req = http.get(url, { signal: controller.signal }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({ statusCode: res.statusCode, body: data }));
    });
    
    req.on('error', (err) => {
      if (err.name === 'AbortError') {
        reject(new Error('Request was aborted'));
      } else {
        reject(err);
      }
    });
  });
  
  return { promise, abort: controller.abort.bind(controller) };
}

// Usage
const { promise, abort } = getWithAbort('http://example.com/slow');
setTimeout(abort, 1000); // Abort after 1 second

try {
  const response = await promise;
  console.log(response.body);
} catch (err) {
  console.error(err.message);
}
```

### HTTP Agents and Connection Pooling

```javascript
import http from 'node:http';

// Create custom agent with connection pooling settings
const agent = new http.Agent({
  keepAlive: true,        // Enable keep-alive
  maxSockets: 50,         // Max sockets per host
  maxFreeSockets: 10,     // Max free sockets to keep alive
  timeout: 60000          // Socket timeout (ms)
});

// Use agent for requests
const options = {
  hostname: 'api.example.com',
  path: '/endpoint',
  method: 'GET',
  agent: agent
};

const req = http.request(options, (res) => {
  console.log('Response received');
  res.resume(); // Consume response
});

req.end();

// Monitor agent statistics
console.log('Free sockets:', Object.keys(agent.freeSockets).length);
console.log('Active sockets:', Object.keys(agent.sockets).length);
```

## HTTP/2 Module

### Creating an HTTP/2 Server

```javascript
import http2 from 'node:http2';
import fs from 'node:fs';

// Load TLS certificates
const options = {
  key: fs.readFileSync('server-key.pem'),
  cert: fs.readFileSync('server-cert.pem')
};

const server = http2.createSecureServer(options, (req, res) => {
  res.writeHead(200);
  res.end('Hello HTTP/2\n');
});

server.listen(443, () => {
  console.log('HTTP/2 server running on https://localhost:443');
});
```

### HTTP/2 Server Push

```javascript
import http2 from 'node:http2';
import fs from 'node:fs';

const server = http2.createSecureServer(options, (req, res) => {
  if (req.url === '/') {
    // Send main HTML
    const html = '<html><body><img src="/image.png"></body></html>';
    
    // Push image proactively
    const pushStream = res.pushStream({
      ':path': '/image.png',
      ':status': 200
    });
    
    fs.createReadStream('image.png').pipe(pushStream);
    
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(html);
  } else if (req.url === '/image.png') {
    // Handle direct image requests too
    fs.createReadStream('image.png').pipe(res);
  }
});
```

### HTTP/2 Client

```javascript
import http2 from 'node:http2';

// Connect to HTTP/2 server
const client = http2.connect('https://example.com:443', {
  // Optionally provide CA certificate for verification
  // rejectUnauthorized: false // For testing only
});

client.on('error', (err) => {
  console.error('HTTP/2 error:', err);
});

// Make request
const req = client.request({
  ':path': '/api/data',
  ':method': 'GET'
});

req.setEncoding('utf8');

let data = '';
req.on('data', chunk => {
  data += chunk;
});

req.on('end', () => {
  console.log('Response:', data);
  client.close();
});

req.end();
```

## HTTPS Module

### HTTPS Server

```javascript
import https from 'node:https';
import fs from 'node:fs';

const options = {
  key: fs.readFileSync('server-key.pem'),
  cert: fs.readFileSync('server-cert.pem'),
  
  // Optional: CA certificate for client authentication
  // ca: fs.readFileSync('ca-cert.pem'),
  
  // Require client certificate
  // requestCert: true,
  
  // Reject unauthorized clients
  // rejectUnauthorized: true
};

const server = https.createServer(options, (req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  
  // Check if client provided certificate
  const clientCert = req.socket.getPeerCertificate();
  if (clientCert) {
    res.end('Client authenticated with certificate\n');
  } else {
    res.end('No client certificate provided\n');
  }
});

server.listen(443, () => {
  console.log('HTTPS server running on https://localhost:443');
});
```

### HTTPS Client

```javascript
import https from 'node:https';

function httpsGet(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      
      res.on('data', chunk => {
        data += chunk;
      });
      
      res.on('end', () => {
        resolve({ statusCode: res.statusCode, body: data });
      });
    }).on('error', reject);
  });
}

// Usage with custom CA certificate
import fs from 'node:fs';

const options = {
  ca: fs.readFileSync('ca-cert.pem')
};

https.get('https://internal-service.local/api', options, (res) => {
  console.log('Connected to internal service');
}).on('error', (err) => {
  console.error('Connection failed:', err.message);
});
```

## Net Module (TCP)

### TCP Server

```javascript
import net from 'node:net';

const server = net.createServer((socket) => {
  console.log('Client connected');
  
  // Handle incoming data
  socket.on('data', (data) => {
    console.log('Received:', data.toString());
    
    // Echo back
    socket.write('Echo: ' + data);
  });
  
  // Handle errors
  socket.on('error', (err) => {
    console.error('Socket error:', err);
  });
  
  // Handle disconnection
  socket.on('close', () => {
    console.log('Client disconnected');
  });
  
  // Send welcome message
  socket.write('Welcome to the server!\n');
});

server.listen(8080, () => {
  console.log('TCP server listening on port 8080');
});
```

### TCP Client

```javascript
import net from 'node:net';

function connectToServer(host, port) {
  return new Promise((resolve, reject) => {
    const client = net.createConnection(
      { host, port },
      () => {
        console.log('Connected to server');
        resolve(client);
      }
    );
    
    client.setEncoding('utf8');
    
    client.on('data', (data) => {
      console.log('Received:', data);
    });
    
    client.on('error', (err) => {
      reject(err);
    });
    
    client.on('close', () => {
      console.log('Connection closed');
    });
  });
}

// Usage
try {
  const client = await connectToServer('localhost', 8080);
  
  // Send data
  client.write('Hello Server\n');
  
  // Close after some time
  setTimeout(() => {
    client.end();
  }, 2000);
} catch (err) {
  console.error('Connection failed:', err.message);
}
```

### TCP Server with Protocol

```javascript
import net from 'node:net';

// Simple line-based protocol server
const server = net.createServer((socket) => {
  let buffer = '';
  
  socket.on('data', (data) => {
    buffer += data.toString();
    
    // Process complete lines
    let newlineIndex;
    while ((newlineIndex = buffer.indexOf('\n')) >= 0) {
      const line = buffer.slice(0, newlineIndex).trim();
      buffer = buffer.slice(newlineIndex + 1);
      
      // Handle commands
      if (line === 'PING') {
        socket.write('PONG\n');
      } else if (line.startsWith('ECHO ')) {
        socket.write('ECHO: ' + line.slice(5) + '\n');
      } else if (line === 'QUIT') {
        socket.end('Goodbye!\n');
      } else {
        socket.write('UNKNOWN: ' + line + '\n');
      }
    }
  });
  
  socket.on('error', (err) => {
    console.error('Socket error:', err);
  });
});

server.listen(9000, () => {
  console.log('Protocol server on port 9000');
});
```

## DNS Module

### Resolution Methods

```javascript
import dns from 'node:dns';
import { promisify } from 'node:util';

// Promisified versions
const resolve4 = promisify(dns.resolve4);
const lookup = promisify(dns.lookup);

// Async/await usage
async function dnsLookup(domain) {
  try {
    // Basic lookup (uses system resolver)
    const result = await lookup(domain);
    console.log('Address:', result.address);
    console.log('Family:', result.family);
    
    // Get all A records
    const addresses = await resolve4(domain);
    console.log('All IPv4 addresses:', addresses);
    
    // Get AAAA records (IPv6)
    const ipv6Addresses = await dns.promises.resolve6(domain);
    console.log('IPv6 addresses:', ipv6Addresses);
    
    // Get MX records
    const mxRecords = await dns.promises.resolveMx(domain);
    console.log('MX records:', mxRecords);
    
    // Get TXT records
    const txtRecords = await dns.promises.resolveTxt(domain);
    console.log('TXT records:', txtRecords);
    
  } catch (err) {
    console.error('DNS error:', err.message);
  }
}

dnsLookup('example.com');
```

### Custom Resolver

```javascript
import dns from 'node:dns';

// Create custom resolver
const resolver = new dns.Resolver();

// Set custom DNS servers
resolver.setServers([
  '8.8.8.8',      // Google DNS
  '1.1.1.1',      // Cloudflare DNS
  '208.67.222.222' // OpenDNS
]);

// Use custom resolver
resolver.resolve4('example.com', (err, addresses) => {
  if (err) {
    console.error('Resolution failed:', err);
    return;
  }
  console.log('Addresses via custom DNS:', addresses);
});

// Async/await version
const resolve4 = dns.promises.resolve4.bind(dns.promises);

async function resolveWithCustom(domain) {
  const addresses = await resolver.resolve4(domain);
  return addresses;
}
```

### Reverse DNS Lookup

```javascript
import dns from 'node:dns';

async function reverseLookup(ipAddress) {
  try {
    const hostnames = await dns.promises.reverse(ipAddress);
    console.log('Hostnames for', ipAddress, ':', hostnames);
  } catch (err) {
    console.error('Reverse lookup failed:', err.message);
  }
}

reverseLookup('8.8.8.8');
```

## UDP/Dgram Module

### UDP Server

```javascript
import dgram from 'node:dgram';

const server = dgram.createSocket('udp4');

server.on('error', (err) => {
  console.error('UDP error:', err);
  server.close();
});

server.on('message', (msg, rinfo) => {
  console.log(`Received from ${rinfo.address}:${rinfo.port}:`, msg.toString());
  
  // Send response back
  server.send('Echo: ' + msg, rinfo.port, rinfo.address, (err) => {
    if (err) console.error('Send error:', err);
  });
});

server.on('listening', () => {
  const address = server.address();
  console.log(`UDP server listening on ${address.address}:${address.port}`);
});

server.bind(41234);
```

### UDP Client

```javascript
import dgram from 'node:dgram';

function sendUdpMessage(message, host, port) {
  return new Promise((resolve, reject) => {
    const client = dgram.createSocket('udp4');
    
    // Set timeout for response
    const timeout = setTimeout(() => {
      client.close();
      reject(new Error('Response timeout'));
    }, 5000);
    
    // Send message
    const msg = Buffer.from(message);
    client.send(msg, port, host, (err) => {
      if (err) {
        clearTimeout(timeout);
        client.close();
        reject(err);
      }
    });
    
    // Handle response
    client.on('message', (response, rinfo) => {
      clearTimeout(timeout);
      client.close();
      resolve({
        data: response.toString(),
        from: `${rinfo.address}:${rinfo.port}`
      });
    });
    
    client.on('error', (err) => {
      clearTimeout(timeout);
      client.close();
      reject(err);
    });
  });
}

// Usage
try {
  const response = await sendUdpMessage('Hello', 'localhost', 41234);
  console.log('Response:', response.data);
} catch (err) {
  console.error('UDP failed:', err.message);
}
```

## Best Practices

### HTTP Security Headers

```javascript
import http from 'node:http';

const server = http.createServer((req, res) => {
  // Set security headers
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  res.setHeader('Content-Security-Policy', "default-src 'self'");
  
  // Continue with response...
  res.writeHead(200, { 'Content-Type': 'text/html' });
  res.end('<h1>Secure Content</h1>');
});
```

### Request Size Limits

```javascript
import http from 'node:http';

const server = http.createServer((req, res) => {
  // Limit request body size
  let receivedSize = 0;
  const maxSize = 10 * 1024 * 1024; // 10MB
  
  req.on('data', (chunk) => {
    receivedSize += chunk.length;
    if (receivedSize > maxSize) {
      req.destroy();
      res.writeHead(413, { 'Content-Type': 'text/plain' });
      res.end('Payload too large');
    }
  });
  
  // Handle request...
}).listen(3000);
```

### Graceful Shutdown

```javascript
import http from 'node:http';

const server = http.createServer((req, res) => {
  res.end('Hello');
});

server.listen(3000);

// Graceful shutdown handler
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, shutting down gracefully...');
  
  // Stop accepting new connections
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
  
  // Force exit after 10 seconds
  setTimeout(() => {
    console.error('Could not close connections in time, forcefully shutting down');
    process.exit(1);
  }, 10000);
});
```
