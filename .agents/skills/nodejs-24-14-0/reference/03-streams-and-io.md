# Streams and I/O

## Stream Types

Node.js streams handle data incrementally rather than loading everything into memory.

| Type | Description | Example |
|------|-------------|---------|
| Readable | Data source | `fs.createReadStream()` |
| Writable | Data destination | `fs.createWriteStream()` |
| Duplex | Both readable and writable | `net.Socket` |
| Transform | Modifies data as it passes through | `zlib.createGzip()` |

## Reading Streams

```javascript
import fs from 'node:fs';

// Method 1: Event-based
const readStream = fs.createReadStream('large-file.txt', { encoding: 'utf-8' });
readStream.on('data', (chunk) => {
  console.log(`Received ${chunk.length} bytes`);
});
readStream.on('end', () => {
  console.log('Finished reading');
});
readStream.on('error', (err) => {
  console.error('Read error:', err);
});

// Method 2: Async iteration (preferred for modern code)
import fs from 'node:fs/promises';
const file = await fs.open('large-file.txt', 'r');
const stream = file.createReadStream();
for await (const chunk of stream) {
  console.log(chunk.toString());
}
await file.close();

// Method 3: pipe to another stream
fs.createReadStream('input.txt')
  .pipe(fs.createWriteStream('output.txt'));
```

## Writing Streams

```javascript
import fs from 'node:fs';

const writeStream = fs.createWriteStream('output.txt');

writeStream.write('First chunk\n');
writeStream.write('Second chunk\n');
writeStream.end('Final chunk\n');

// Backpressure handling
writeStream.on('drain', () => {
  console.log('Ready to write more');
});

// Check if write was accepted
if (!writeStream.write('data')) {
  // Buffer is full, wait for 'drain'
  writeStream.once('drain', () => {
    writeStream.write('more data');
  });
}

// Promise-based write (Node 20+)
await writeStream.write('data\n');
await writeStream.end();
```

## Piping Streams

```javascript
import fs from 'node:fs';
import zlib from 'node:zlib';

// Chain streams with pipe
fs.createReadStream('large-file.json')
  .pipe(zlib.createGzip())
  .pipe(fs.createWriteStream('large-file.json.gz'));

// Pipe with error handling
const source = fs.createReadStream('input.txt');
const dest = fs.createWriteStream('output.txt');

source.on('error', (err) => {
  console.error('Source error:', err);
  dest.destroy();
});

dest.on('error', (err) => {
  console.error('Dest error:', err);
  source.destroy();
});

dest.on('finish', () => {
  console.log('Write complete');
});

source.pipe(dest);

// Node 16+: pipe returns destination for chaining
source.pipe(dest).on('finish', () => console.log('done'));
```

## Transform Streams

Transform streams modify data as it flows through:

```javascript
import { Transform } from 'node:stream';
import fs from 'node:fs';

// Custom transform — uppercase text
const upperCase = new Transform({
  transform(chunk, encoding, callback) {
    this.push(chunk.toString().toUpperCase());
    callback();
  },
});

fs.createReadStream('input.txt')
  .pipe(upperCase)
  .pipe(fs.createWriteStream('output.txt'));

// Async transform (modern style)
const jsonlToJson = new Transform({
  async transform(chunk, _, callback) {
    const lines = chunk.toString().trim().split('\n');
    const objects = lines.map(line => JSON.parse(line));
    this.push(JSON.stringify(objects));
    callback();
  },
  flush(callback) {
    callback();
  },
});
```

## Object Mode Streams

Streams that handle JavaScript objects instead of Buffers:

```javascript
import { Readable } from 'node:stream';

// Object mode readable
const objStream = Readable.from([
  { id: 1, name: 'Alice' },
  { id: 2, name: 'Bob' },
  { id: 3, name: 'Charlie' },
], { objectMode: true });

for await (const obj of objStream) {
  console.log(obj.name);
}

// Object mode transform
import { Transform } from 'node:stream';

const filterTransform = new Transform({
  readableObjectMode: true,
  writableObjectMode: true,
  transform(chunk, _, callback) {
    if (chunk.active) this.push(chunk); // pass through only active
    callback();
  },
});
```

## Backpressure

Backpressure occurs when the writer is slower than the reader. Node.js handles it automatically with `pipe()`:

```javascript
// pipe() automatically pauses the source when dest buffer fills
source.pipe(dest); // handles backpressure internally

// Manual backpressure handling
function writeWithBackpressure(stream, data) {
  let chunk = data.shift();
  function write() {
    while (chunk !== undefined) {
      let ok = stream.write(chunk);
      if (!ok) {
        // Buffer full, wait for drain
        stream.once('drain', write);
        return;
      }
      chunk = data.shift();
    }
    stream.end();
  }
  write();
}
```

## Web Streams Interop

Node.js supports the WHATWG Web Streams API (`node:stream/web`):

```javascript
import { ReadableStream, WritableStream, TransformStream } from 'node:stream/web';

// Convert Node stream to web stream
const nodeStream = fs.createReadStream('file.txt');
const webReadable = new ReadableStream({
  start(controller) {
    nodeStream.on('data', (chunk) => controller.enqueue(chunk));
    nodeStream.on('end', () => controller.close());
    nodeStream.on('error', (err) => controller.error(err));
  },
});

// Use with fetch Response
const response = new Response(webReadable);
const text = await response.text();

// TransformStream for pipelining
const upperTransform = new TransformStream({
  transform(chunk, controller) {
    controller.enqueue(chunk.toString().toUpperCase());
  },
});

fetch('https://example.com/data')
  .then(r => r.body)
  .then(body => body.pipeThrough(upperTransform))
  .then(stream => new Response(stream))
  .then(r => r.text())
  .then(console.log);
```

## Compression Streams (Built-in)

Node.js provides native compression/decompression via Web Streams:

```javascript
import { CompressionStream, DecompressionStream } from 'node:stream/web';

// Compress
const compressed = await new Response(
  new TextStream('hello world').pipeThrough(new CompressionStream('gzip'))
).arrayBuffer();

// Decompress
const decompressed = await new Response(
  new Response(compressed).body.pipeThrough(new DecompressionStream('gzip'))
).text();
// 'hello world'

// Supported formats: 'gzip', 'deflate', 'deflate-raw', 'br' (brotli)
```

## readline — Line-by-Line Reading

```javascript
import readline from 'node:readline';
import fs from 'node:fs';

// Interactive prompt
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

const answer = await rl.question('Enter your name: ');
console.log(`Hello, ${answer}!`);
rl.close();

// Read file line by line (memory efficient)
const fileStream = fs.createReadStream('large-file.csv');
const fileRl = readline.createInterface({ input: fileStream });

let lineCount = 0;
for await (const line of fileRl) {
  lineCount++;
  const [name, email] = line.split(',');
  console.log(`Line ${lineCount}: ${name} <${email}>`);
}
```

## string_decoder — Character Encoding

Properly decode Buffers without splitting multi-byte characters:

```javascript
import { StringDecoder } from 'node:string_decoder';

const decoder = new StringDecoder('utf-8');

// Simulate receiving partial UTF-8 character
const part1 = Buffer.from([0xe2]);
const part2 = Buffer.from([0x82, 0xac]); // € sign

console.log(decoder.write(part1));  // '' (incomplete char buffered)
console.log(decoder.write(part2));  // '€' (completed)
console.log(decoder.end());          // '' (no remaining bytes)
```

## Stream Promises API

Node.js streams support promise-based methods:

```javascript
import fs from 'node:fs';
import { pipeline } from 'node:stream/promises';
import zlib from 'node:zlib';

// pipeline — handles errors and cleanup automatically
await pipeline(
  fs.createReadStream('input.txt'),
  zlib.createGzip(),
  fs.createWriteStream('output.txt.gz')
);
console.log('Pipeline complete');

// consume — collect all data from a readable stream
import { consume } from 'node:stream/promises';
const chunks = await consume(fs.createReadStream('file.txt'));
```
