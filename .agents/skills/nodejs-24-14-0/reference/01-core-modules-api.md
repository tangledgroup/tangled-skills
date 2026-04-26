# Core Modules API Reference

## fs — File System

Three APIs: Promises (`node:fs/promises`), Callbacks (`node:fs`), and Synchronous (`node:fs`).

### Reading Files

```javascript
import fs from 'node:fs/promises';

// Read as string
const content = await fs.readFile('file.txt', 'utf-8');

// Read as Buffer
const buffer = await fs.readFile('image.png');

// Read directory
const entries = await fs.readdir('/path/to/dir', { withFileTypes: true });

// Read directory recursively (Node 20+)
for await (const entry of fs.glob('/path/**/*.js')) {
  console.log(entry);
}
```

### Writing Files

```javascript
import fs from 'node:fs/promises';
import path from 'node:path';

// Write file
await fs.writeFile('output.txt', 'content', 'utf-8');

// Append to file
await fs.appendFile('log.txt', 'new line\n');

// Atomic write with temp file
const tmpPath = `${path.join('output.json')}.tmp`;
await fs.writeFile(tmpPath, JSON.stringify({ data: true }));
await fs.rename(tmpPath, 'output.json');
```

### File Stats and Metadata

```javascript
import fs from 'node:fs/promises';

const stats = await fs.stat('file.txt');
console.log(stats.isFile());      // true
console.log(stats.isDirectory()); // false
console.log(stats.size);          // bytes
console.log(stats.mtime);         // last modified Date

// Check existence without try/catch
const { error, data: fd } = await fs.open('file.txt', 'r').catch(e => ({ error: e }));
```

### Watch and Truncate

```javascript
import fs from 'node:fs/promises';

// Watch for file changes
const watcher = fs.watch('file.txt', (eventType, filename) => {
  console.log(`Event: ${eventType}, File: ${filename}`);
});

// Truncate file
await fs.truncate('file.txt', 100); // keep first 100 bytes
```

### Common Objects

- `fs.Dir` — directory handle from `fs.opendir()`
- `fs.FileHandle` — file descriptor handle from `fs.open()`
- `fs.ReadStream` / `fs.WriteStream` — stream-based file access
- `fs.Stats` — file metadata from `fs.stat()`
- `fs.Dirent` — directory entry from `fs.readdir({ withFileTypes: true })`

### Callback API (legacy)

```javascript
import fs from 'node:fs';

fs.readFile('file.txt', 'utf-8', (err, data) => {
  if (err) throw err;
  console.log(data);
});
```

---

## http — HTTP Server and Client

### Creating an HTTP Server

```javascript
import http from 'node:http';

const server = http.createServer((req, res) => {
  // req: IncomingMessage (Readable stream)
  // res: ServerResponse (Writable stream)

  res.writeHead(200, {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache'
  });
  res.end(JSON.stringify({ message: 'ok' }));
});

server.listen(3000);

// Events
server.on('request', (req, res) => { /* ... */ });
server.on('connection', (socket) => { /* ... */ });
server.on('close', () => { /* ... */ });
```

### Making HTTP Requests

```javascript
import http from 'node:http';

const response = await fetch('http://example.com/api/data');
const data = await response.json();

// Or using http.request for more control
const req = http.request('http://example.com/api', { method: 'POST' }, (res) => {
  let body = '';
  res.on('data', (chunk) => { body += chunk; });
  res.on('end', () => console.log(body));
});
req.write(JSON.stringify({ key: 'value' }));
req.end();
```

### Request/Response Objects

`IncomingMessage` (req):
- `req.method` — HTTP method (GET, POST, etc.)
- `req.url` — request path and query string
- `req.headers` — incoming headers object
- `req.socket` — underlying net.Socket
- Readable stream for request body

`ServerResponse` (res):
- `res.writeHead(statusCode, headers)` — write response header
- `res.write(chunk)` — write response body chunk
- `res.end([data])` — finish response
- `res.statusCode` / `res.statusMessage`

---

## https — HTTPS

```javascript
import https from 'node:https';
import fs from 'node:fs/promises';

const server = https.createServer({
  key: await fs.readFile('server-key.pem'),
  cert: await fs.readFile('server-cert.pem'),
}, (req, res) => {
  res.end('Secure response');
});

// HTTPS client (fetch supports https natively)
const data = await fetch('https://api.example.com/data', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ key: 'value' }),
});
```

---

## net — TCP Sockets

### TCP Server

```javascript
import net from 'node:net';

const server = net.createServer((socket) => {
  socket.write('Echo server\r\n');
  socket.pipe(socket); // echo back
});

server.listen(8124, () => console.log('TCP server on port 8124'));
```

### TCP Client

```javascript
import net from 'node:net';

const client = net.connect({ port: 8124 }, () => {
  client.write('Hello server!\n');
});

client.on('data', (data) => {
  console.log(`Received: ${data}`);
  client.end();
});
```

### IPC via Unix Socket

```javascript
// Server
const server = net.createServer((socket) => {
  socket.end('response from unix socket');
});
server.listen('/tmp/my-ipc.sock');

// Client
const client = net.connect('/tmp/my-ipc.sock', () => {
  client.write('hello');
});
client.on('data', (data) => console.log(data.toString()));
```

---

## dns — DNS Resolution

```javascript
import dns from 'node:dns';

// Promise-based (uses system resolver by default)
const addresses = await dns.promises.resolve4('example.com');
const AAAA = await dns.promises.resolve6('example.com');
const mx = await dns.promises.resolveMx('example.com');
const txt = await dns.promises.resolveTxt('example.com');

// Reverse DNS
const hostnames = await dns.promises.reverse('93.184.216.34');

// Lookup (uses c-ares by default)
const { address, family } = await dns.promises.lookup('example.com');

// Resolver instance for custom servers
const resolver = new dns.Resolver();
resolver.setServers(['8.8.8.8', '8.8.4.4']);
const result = await resolver.resolve4('example.com');
```

---

## dgram — UDP

```javascript
import dgram from 'node:dgram';

// Server
const server = dgram.createSocket('udp4');
server.on('message', (msg, rinfo) => {
  console.log(`Received ${msg.length} bytes from ${rinfo.address}:${rinfo.port}`);
  server.send('response', rinfo.port, rinfo.address);
});
server.bind(41234);

// Client
const client = dgram.createSocket('udp4');
client.send('hello', 41234, 'localhost', (err) => {
  client.close();
});
```

---

## os — Operating System Information

```javascript
import os from 'node:os';

console.log(os.platform());        // 'linux', 'darwin', 'win32'
console.log(os.arch());            // 'x64', 'arm64'
console.log(os.hostname());        // machine hostname
console.log(os.homedir());         // user home directory
console.log(os.tmpdir());          // temp directory path
console.log(os.type());            // 'Linux', 'Darwin', 'Windows_NT'
console.log(os.release());         // OS kernel version
console.log(os.endianness());      // 'BE' or 'LE'
console.log(os.availableParallelism()); // number of available CPU cores
console.log(os.cpus());            // array of CPU info objects
console.log(os.totalmem());        // total system memory in bytes
console.log(os.freemem());         // free memory in bytes
console.log(os.loadavg());         // 1, 5, 15 min load averages
console.log(os.networkInterfaces()); // network interface details
console.log(os.userInfo());        // { uid, gid, username, homedir, shell }
console.log(os.EOL);               // '\n' (POSIX) or '\r\n' (Windows)
```

---

## path — Path Manipulation

```javascript
import path from 'node:path';

// Cross-platform: use path.posix or path.win32 for explicit behavior
path.join('a', 'b', 'c');           // 'a/b/c' (POSIX)
path.resolve('/foo', 'bar', '..');  // '/foo'
path.normalize('./foo/../bar');     // './bar'
path.basename('/foo/bar/baz.txt');  // 'baz.txt'
path.extname('/foo/bar/baz.txt');   // '.txt'
path.dirname('/foo/bar/baz.txt');   // '/foo/bar'
path.isAbsolute('/foo/bar');        // true

const parsed = path.parse('/home/user/file.txt');
// { root: '/', dir: '/home/user', base: 'file.txt', ext: '.txt', name: 'file' }

const formatted = path.format({ dir: '/home/user', base: 'file.txt' });
// '/home/user/file.txt'

path.relative('/a/b/c', '/a/d/e');  // '../../d/e'
path.delimiter;                     // ':' (POSIX) or ';' (Windows)
```

---

## url — URL Parsing

```javascript
import { fileURLToPath, pathToFileURL } from 'node:url';

// WHATWG URL API (preferred)
const url = new URL('https://example.com:8080/path?query=value#hash');
url.protocol;   // 'https:'
url.hostname;   // 'example.com'
url.port;       // '8080'
url.pathname;   // '/path'
url.search;     // '?query=value'
url.hash;       // '#hash'
url.searchParams.get('query');  // 'value'

// File URL conversion
const filePath = fileURLToPath(import.meta.url);
const fileUrl = pathToFileURL('/path/to/file.txt');
// file:///path/to/file.txt

// URL pattern matching (Node 22+)
const pattern = new URLPattern('https://example.com/users/:id');
pattern.test('https://example.com/users/42');  // true
pattern.exec('https://example.com/users/42').pathname.groups.id;  // '42'
```

---

## util — Utilities

```javascript
import util from 'node:util';

// Convert callback function to promise
const { exec } = await import('node:child_process');
const execAsync = util.promisify(exec);
const { stdout } = await execAsync('ls -la');

// Convert promise function to callback
const callbackFn = util.callbackify(async (x) => x * 2);
callbackFn(5, (err, result) => console.log(result)); // 10

// Deep equality check
util.isDeepStrictEqual({ a: [1] }, { a: [1] }); // true

// Inspect objects
console.log(util.inspect(obj, { depth: null, colors: true }));

// Format strings
util.format('Hello %s, you have %d messages', 'Alice', 5);

// Debug logging (set NODE_DEBUG=module*)
const log = util.debuglog('myapp');
log('debug info:', data);

// Parse command-line arguments
const { values, positionals, tokens } = util.parseArgs({
  options: {
    help: { type: 'boolean', short: 'h' },
    name: { type: 'string', short: 'n' },
  },
});
```

---

## buffer — Binary Data

```javascript
// Creating buffers
const buf1 = Buffer.alloc(10);              // zero-filled, 10 bytes
const buf2 = Buffer.from('hello', 'utf-8'); // from string
const buf3 = Buffer.from([1, 2, 3, 4]);     // from array
const buf4 = Buffer.allocUnsafe(10);        // faster, may contain garbage

// Reading/writing
buf2[0];                    // 104 ('h')
buf2.toString('utf-8');     // 'hello'
buf2.toString('hex');       // '68656c6c6f'
buf2.length;                // 5

// Methods
buf2.slice(0, 3);           // Buffer [104, 101, 108]
Buffer.concat([buf1, buf2]); // concatenated buffer
buf2.copy(target, 0, 0, 3); // copy bytes
buf2.includes(Buffer.from('he')); // true
buf2.indexOf('lo');         // 3

// Number operations
const numBuf = Buffer.alloc(8);
numBuf.writeBigUInt64BE(BigInt(9007199254740991), 0);
numBuf.readBigUInt64BE(0);  // 9007199254740991n

// Blob and File (web-compatible)
const blob = new Blob([buf2], { type: 'text/plain' });
const arrayBuffer = await blob.arrayBuffer();
```

---

## console — Output

```javascript
console.log('message');
console.error('error message');
console.warn('warning');
console.debug('debug info'); // shown with NODE_DEBUG=*

// Formatted output
console.table({ a: 1, b: 2 });
console.time('operation');
// ... do work ...
console.timeEnd('operation');

// Grouping
console.group('Group 1');
console.log('inside group');
console.groupEnd();

// Tracing
console.trace('stack trace here');

// Custom console with streams
import { Console } from 'node:console';
const out = fs.createWriteStream('./out.log');
const err = fs.createWriteStream('./err.log');
const logger = new Console({ stdout: out, stderr: err });
```

---

## timers — Scheduling

```javascript
import timers from 'node:timers';

// setTimeout — run once after delay
const timer = setTimeout(() => {
  console.log('runs after 1 second');
}, 1000);
clearTimeout(timer);

// setInterval — repeat every interval
const interval = setInterval(() => {
  console.log('every 500ms');
}, 500);
clearInterval(interval);

// setImmediate — run in check phase (after poll)
setImmediate(() => {
  console.log('runs in check phase');
});

// Promise-based (Node 16+)
await new Promise((resolve) => setTimeout(resolve, 1000));

// timers/promises API
import { setTimeout as sleep } from 'node:timers/promises';
await sleep(1000); // wait 1 second

import { setImmediate as immediate } from 'node:timers/promises';
await immediate(); // yield to next check phase

// Ref/unref — control whether timer keeps process alive
timer.unref(); // timer won't prevent process exit
```

---

## readline — Line-by-Line Input

```javascript
import readline from 'node:readline';
import { stdin, stdout } from 'node:process';

const rl = readline.createInterface({ input: stdin, output: stdout });

// Prompt user
const answer = await rl.question('What is your name? ');
console.log(`Hello, ${answer}!`);
rl.close();

// Read file line by line
import fs from 'node:fs';
const fileStream = fs.createReadStream('large-file.txt');
const fileRl = readline.createInterface({ input: fileStream });
for await (const line of fileRl) {
  console.log(line);
}

// History interface (Node 20+)
import { createInterface } from 'node:readline';
const history = [];
const rl2 = createInterface({
  input: process.stdin,
  output: process.stdout,
  history: history, // enables up/down arrow navigation
});
```

---

## zlib — Compression

```javascript
import zlib from 'node:zlib';
import fs from 'node:fs/promises';

// Compress/decompress data
const input = await fs.readFile('large-file.json');
const compressed = zlib.gzipSync(input);
await fs.writeFile('large-file.json.gz', compressed);

const decompressed = zlib.gunzipSync(compressed);

// Streaming compression
import { createGzip, createGunzip, createBrotliCompress, createBrotliDecompress } from 'node:zlib';

// gzip stream
fs.createReadStream('input.txt').pipe(createGzip()).pipe(fs.createWriteStream('output.txt.gz'));

// brotli (best compression ratio)
const brotliCompressed = zlib.brotliCompressSync(input, { params: { [zlib.constants.BROTLI_PARAM_QUALITY]: 11 } });

// zstd (fast, good ratio)
const zstdCompressed = zlib.zstdCompressSync(input);
const zstdDecompressed = zlib.zstdDecompressSync(zstdCompressed);

// Convenience methods
zlib.deflateSync(data);
zlib.inflateSync(data);
zlib.deflateRawSync(data);
zlib.inflateRawSync(data);
```

---

## assert — Assertions

```javascript
import assert from 'node:assert/strict'; // prefer strict mode

assert.strictEqual(actual, expected);      // === check
assert.notStrictEqual(actual, expected);   // !== check
assert.deepEqual(actual, expected);        // loose deep equality
assert.deepStrictEqual(actual, expected);  // strict deep equality
assert.partialDeepStrictEqual(obj, { a: 1 }); // partial match

// Async assertions
await assert.rejects(asyncFn, { name: 'TypeError' });
await assert.doesNotReject(asyncFn);

// Function behavior
assert.throws(() => { throw new Error('fail'); }, /fail/);
assert.doesNotThrow(() => console.log('ok'));

// Pattern matching
assert.match('hello world', /world/);
assert.doesNotMatch('hello', /world/);

// ifError — fail if value is truthy (error-first callback pattern)
fs.readFile('file.txt', (err, data) => {
  assert.ifError(err);
});
```

---

## v8 — V8 Engine APIs

```javascript
import v8 from 'node:v8';

// Heap statistics
const stats = v8.getHeapStatistics();
console.log(stats.heap_size_limit);
console.log(stats.total_heap_size);
console.log(stats.used_heap_size);

// Write heap snapshot for profiling
v8.writeHeapSnapshot('heap-snapshot.heapsnapshot');

// Get CPU profile
const profile = v8.startCpuProfile('profile-name');
// ... do work ...
const result = v8.stopCpuProfile('profile-name');

// Serialize/deserialize objects
const serialized = v8.serialize({ data: 'hello' });
const deserialized = v8.deserialize(serialized);

// Query objects in heap (debugging)
const instances = v8.queryObjects(String, 10); // up to 10 String instances
```

---

## perf_hooks — Performance

```javascript
import { performance, PerformanceObserver, eventLoopUtilization } from 'node:perf_hooks';

// Simple timing
performance.mark('start');
doWork();
performance.mark('end');
performance.measure('work-duration', 'start', 'end');
const measure = performance.getEntriesByName('work-duration')[0];
console.log(`${measure.name}: ${measure.duration}ms`);

// Observer for monitoring
const observer = new PerformanceObserver((items) => {
  for (const item of items.getEntries()) {
    console.log(`Entry: ${item.name}, Duration: ${item.duration}ms`);
  }
});
observer.observe({ entryTypes: ['measure', 'function'] });

// Event loop utilization
const elu = eventLoopUtilization();
console.log(`Active: ${elu.utilization.toFixed(4)}`);

// Monitor event loop delay
const monitor = performance.monitorEventLoopDelay({ resolution: 10 });
monitor.enable();
// ... run app ...
monitor.disable();
console.log(monitor.mean); // average delay in ms

// Histogram
import { createHistogram } from 'node:perf_hooks';
const histogram = createHistogram();
histogram.value(performance.now());
console.log(histogram.percentile(95)); // 95th percentile
```

---

## tty — Terminal

```javascript
import tty from 'node:tty';

// Check if running in a TTY
tty.isatty(0);  // stdin
tty.isatty(1);  // stdout
tty.isatty(2);  // stderr

// Get terminal size
process.stdout.columns;  // width
process.stdout.rows;     // height

// Raw mode for terminal input
process.stdin.setRawMode(true);
process.stdin.resume();
process.stdin.on('data', (key) => {
  if (key[0] === 3) process.exit(); // Ctrl+C
});
```

---

## repl — Read-Eval-Print Loop

```javascript
import repl from 'node:repl';

const server = repl.start({
  prompt: 'my-repl> ',
  eval: repl.defaultEval,
  useGlobal: true,
});

// Add custom commands
server.defineCommand('clear', {
  help: 'Clear the screen',
  action() {
    this.clearBufferedCommand();
    console.clear();
    this.displayPrompt();
  },
});

// Add context variables
server.context.db = myDatabase;
```

---

## report — Diagnostic Reports

```javascript
import { report } from 'node:report';

// Generate diagnostic report
report.writeReport('./reports'); // writes JSON to directory

// Configure report
import { register } from 'node:report';
register({
  directory: './crash-reports',
  filename: 'report-%YYYY%-%MM%-%DD%-%hour%-%min%-%sec%.diagnostics.json',
  signature: 'my-app',
});

// Trigger on signal
process.on('SIGUSR2', () => {
  report.writeReport();
});
```
