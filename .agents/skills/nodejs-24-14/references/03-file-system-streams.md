# File System and Streams Reference

This document covers Node.js 24.14 file system operations, stream processing, path utilities, and OS module.

## File System Module (fs)

### Async/Await API (fs/promises)

```javascript
import fs from 'node:fs/promises';

// Read file
const data = await fs.readFile('file.txt', 'utf8');
console.log(data);

// Write file
await fs.writeFile('output.txt', 'Hello World', 'utf8');

// Append to file
await fs.appendFile('log.txt', 'New entry\n', 'utf8');

// Check if file exists
try {
  await fs.access('file.txt', fs.constants.F_OK);
  console.log('File exists');
} catch {
  console.log('File does not exist');
}

// Read directory
const files = await fs.readdir('/path/to/dir');
console.log(files);

// Read directory with options
const entries = await fs.readdir('/path/to/dir', { 
  withFileTypes: true 
});
for (const entry of entries) {
  console.log(entry.name, entry.isDirectory() ? 'dir' : 'file');
}

// Create directory
await fs.mkdir('new-dir', { recursive: true });

// Copy file
await fs.copyFile('source.txt', 'dest.txt');

// Move/rename file
await fs.rename('old-name.txt', 'new-name.txt');

// Delete file/directory
await fs.unlink('file.txt');
await fs.rm('dir', { recursive: true, force: true });

// Get file stats
const stats = await fs.stat('file.txt');
console.log('Size:', stats.size);
console.log('Is file:', stats.isFile());
console.log('Is directory:', stats.isDirectory());
console.log('Modified:', stats.mtime);
```

### Callback API (fs)

```javascript
import fs from 'node:fs';

// Read file with callback
fs.readFile('file.txt', 'utf8', (err, data) => {
  if (err) throw err;
  console.log(data);
});

// Write file with callback
fs.writeFile('output.txt', 'Hello', 'utf8', (err) => {
  if (err) throw err;
  console.log('File written');
});

// Synchronous operations (use sparingly)
const data = fs.readFileSync('file.txt', 'utf8');
fs.writeFileSync('output.txt', 'Hello', 'utf8');
```

### File Reading Patterns

#### Read Entire File

```javascript
import fs from 'node:fs/promises';

// As text
const text = await fs.readFile('file.txt', 'utf8');

// As JSON
const json = JSON.parse(await fs.readFile('config.json', 'utf8'));

// As buffer (binary)
const buffer = await fs.readFile('image.png');
```

#### Read Large File in Chunks

```javascript
import fs from 'node:fs/promises';

async function readLargeFileInChunks(filepath, chunkSize = 1024 * 1024) {
  const stat = await fs.stat(filepath);
  const fd = await fs.open(filepath, 'r');
  
  try {
    let offset = 0;
    const chunks = [];
    
    while (offset < stat.size) {
      const buffer = Buffer.alloc(Math.min(chunkSize, stat.size - offset));
      const { bytesRead } = await fd.read(buffer, 0, buffer.length, offset);
      
      if (bytesRead === 0) break;
      
      chunks.push(buffer);
      offset += bytesRead;
    }
    
    return Buffer.concat(chunks);
  } finally {
    await fd.close();
  }
}
```

#### Read Line by Line

```javascript
import fs from 'node:fs';

function* readLines(filepath) {
  const readline = require('node:readline');
  const fileStream = fs.createReadStream(filepath);
  
  const rl = readline.createInterface({
    input: fileStream,
    crlfDelay: Infinity
  });
  
  for await (const line of rl) {
    yield line;
  }
}

// Usage
for await (const line of readLines('large-file.txt')) {
  console.log(line);
}
```

### File Writing Patterns

#### Write with Atomic Operation

```javascript
import fs from 'node:fs/promises';

async function atomicWrite(filepath, content) {
  const tmpPath = filepath + '.tmp.' + process.pid;
  
  try {
    await fs.writeFile(tmpPath, content, { flag: 'wx' }); // 'wx' = create exclusively
    await fs.rename(tmpPath, filepath); // Atomic on most filesystems
  } catch (err) {
    // Clean up temp file on error
    try {
      await fs.unlink(tmpPath);
    } catch {}
    throw err;
  }
}
```

#### Write with Encoding Options

```javascript
import fs from 'node:fs/promises';

// UTF-8 (default for text)
await fs.writeFile('file.txt', 'Hello', 'utf8');

// UTF-16 LE
await fs.writeFile('file.txt', 'Hello', 'utf16le');

// Base64 encoded
await fs.writeFile('file.b64', Buffer.from('Hello').toString('base64'));

// Binary data
await fs.writeFile('binary.bin', Buffer.from([0x00, 0x01, 0x02]));
```

### Directory Operations

#### Recursive Directory Traversal

```javascript
import fs from 'node:fs/promises';
import path from 'node:path';

async function* traverseDir(dirPath) {
  const entries = await fs.readdir(dirPath, { withFileTypes: true });
  
  for (const entry of entries) {
    const fullPath = path.join(dirPath, entry.name);
    
    if (entry.isDirectory()) {
      yield* traverseDir(fullPath);
    } else {
      yield fullPath;
    }
  }
}

// Usage
for await (const filepath of traverseDir('./src')) {
  console.log('File:', filepath);
}
```

#### Copy Directory Recursively

```javascript
import fs from 'node:fs/promises';
import path from 'node:path';

async function copyDir(src, dest) {
  // Create destination directory
  await fs.mkdir(dest, { recursive: true });
  
  // Get source directory entries
  const entries = await fs.readdir(src, { withFileTypes: true });
  
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    
    if (entry.isDirectory()) {
      await copyDir(srcPath, destPath);
    } else {
      await fs.copyFile(srcPath, destPath);
    }
  }
}

// Usage
await copyDir('./source', './backup');
```

#### Watch Directory for Changes

```javascript
import fs from 'node:fs';

// Watch single file
fs.watchFile('file.txt', { interval: 1000 }, (curr, prev) => {
  if (curr.mtime !== prev.mtime) {
    console.log('File was modified');
  }
});

// Watch directory (FSEvents on macOS, inotify on Linux)
fs.watch('/path/to/dir', { recursive: true }, (eventType, filename) => {
  console.log(`Event: ${eventType}, File: ${filename}`);
});

// Using fs/promises for more control
import { createReadStream } from 'node:fs';
import { createInterface } from 'node:readline';

const watcher = fs.watch('/path/to/dir', async (eventType, filename) => {
  if (eventType === 'change' && filename) {
    const filepath = path.join('/path/to/dir', filename);
    console.log(`Processing changed file: ${filepath}`);
  }
});

// Stop watching
// watcher.close();
```

## Stream Module

### Stream Types

Node.js has four types of streams:

1. **Readable**: Can read data (e.g., `fs.createReadStream`)
2. **Writable**: Can write data (e.g., `fs.createWriteStream`)
3. **Duplex**: Both readable and writable (e.g., `net.Socket`)
4. **Transform**: Modifies data as it passes through (e.g., `zlib.Gzip`)

### Readable Streams

#### Creating from Array

```javascript
import { Readable } from 'node:stream';

// Create readable stream from array
const readable = Readable.from(['a', 'b', 'c']);

// Consume with for-await
for await (const chunk of readable) {
  console.log(chunk);
}

// Or with events
readable.on('data', (chunk) => {
  console.log('Data:', chunk);
});

readable.on('end', () => {
  console.log('No more data');
});
```

#### Creating from Generator

```javascript
import { Readable } from 'node:stream';

function* generateNumbers() {
  for (let i = 0; i < 100; i++) {
    yield i;
  }
}

const readable = Readable.from(generateNumbers());

readable.on('data', (num) => {
  console.log('Number:', num);
});
```

#### File Read Stream

```javascript
import fs from 'node:fs';

const readStream = fs.createReadStream('large-file.txt', {
  highWaterMark: 64 * 1024, // Chunk size: 64KB
  encoding: 'utf8'           // Return strings instead of buffers
});

readStream.on('data', (chunk) => {
  console.log('Received chunk:', chunk.length, 'bytes');
});

readStream.on('end', () => {
  console.log('File read complete');
});

readStream.on('error', (err) => {
  console.error('Read error:', err);
});
```

### Writable Streams

#### File Write Stream

```javascript
import fs from 'node:fs';

const writeStream = fs.createWriteStream('output.txt', {
  flags: 'a',    // Append mode ('w' for overwrite)
  encoding: 'utf8'
});

writeStream.on('open', () => {
  writeStream.write('Line 1\n');
  writeStream.write('Line 2\n');
  writeStream.end('Line 3\n');
});

writeStream.on('finish', () => {
  console.log('All data written');
});

writeStream.on('error', (err) => {
  console.error('Write error:', err);
});
```

#### Custom Writable Stream

```javascript
import { Writable } from 'node:stream';

class WriteToDatabase extends Writable {
  async _write(chunk, encoding, callback) {
    try {
      // Simulate database insert
      await this.insertIntoDatabase(chunk.toString());
      callback();
    } catch (err) {
      callback(err);
    }
  }
  
  async insertIntoDatabase(data) {
    console.log('Inserting:', data);
    // Actual database logic here
  }
}

const dbStream = new WriteToDatabase();

dbStream.write('Record 1\n');
dbStream.write('Record 2\n');
dbStream.end('Record 3\n');
```

### Transform Streams

#### Built-in Transform: Compression

```javascript
import fs from 'node:fs';
import zlib from 'node:zlib';

// Compress file
fs.createReadStream('file.txt')
  .pipe(zlib.createGzip())
  .pipe(fs.createWriteStream('file.txt.gz'));

// Decompress file
fs.createReadStream('file.txt.gz')
  .pipe(zlib.createGunzip())
  .pipe(fs.createWriteStream('file.txt'));
```

#### Custom Transform: Line Numbering

```javascript
import { Transform } from 'node:stream';

class LineNumberer extends Transform {
  constructor() {
    super({ encoding: 'utf8' });
    this.lineNum = 1;
  }
  
  _transform(chunk, encoding, callback) {
    const lines = chunk.toString().split('\n');
    
    for (const line of lines) {
      this.push(`${this.lineNum++}: ${line}\n`);
    }
    
    callback();
  }
}

// Usage
import fs from 'node:fs';

fs.createReadStream('input.txt')
  .pipe(new LineNumberer())
  .pipe(fs.createWriteStream('numbered.txt'));
```

#### Custom Transform: JSON Lines Parser

```javascript
import { Transform } from 'node:stream';

class JsonLinesParser extends Transform {
  constructor() {
    super({ objectMode: true });
    this.buffer = '';
  }
  
  _transform(chunk, encoding, callback) {
    this.buffer += chunk.toString();
    
    const lines = this.buffer.split('\n');
    this.buffer = lines.pop(); // Keep incomplete line in buffer
    
    for (const line of lines) {
      if (line.trim()) {
        try {
          this.push(JSON.parse(line));
        } catch (err) {
          this.emit('error', new Error(`Invalid JSON: ${line}`));
          return;
        }
      }
    }
    
    callback();
  }
  
  _flush(callback) {
    // Process remaining buffer
    if (this.buffer.trim()) {
      try {
        this.push(JSON.parse(this.buffer));
      } catch (err) {
        this.emit('error', err);
        return;
      }
    }
    callback();
  }
}

// Usage
import fs from 'node:fs';

fs.createReadStream('data.jsonl')
  .pipe(new JsonLinesParser())
  .on('data', (obj) => {
    console.log('Parsed object:', obj);
  });
```

### Piping Streams

#### Basic Pipe

```javascript
import fs from 'node:fs';

// Copy file using streams
fs.createReadStream('source.txt')
  .pipe(fs.createWriteStream('dest.txt'));
```

#### Pipe with Error Handling

```javascript
import fs from 'node:fs';

const pipeline = require('node:stream/promises').pipeline;

async function copyFile(src, dest) {
  await pipeline(
    fs.createReadStream(src),
    fs.createWriteStream(dest)
  );
  
  console.log('Copy complete');
}

// Pipeline automatically handles errors and cleanup
try {
  await copyFile('source.txt', 'dest.txt');
} catch (err) {
  console.error('Copy failed:', err.message);
}
```

#### Multiple Transform Stages

```javascript
import fs from 'node:fs';
import zlib from 'node:zlib';
import crypto from 'node:crypto';
import { pipeline } from 'node:stream/promises';

async function compressAndHash(inputPath, outputPath) {
  const sha256 = crypto.createHash('sha256');
  
  // Tee the stream: one path for compression, one for hashing
  const readStream = fs.createReadStream(inputPath);
  const writeStream = fs.createWriteStream(outputPath + '.gz');
  
  let hash = null;
  
  await pipeline(
    readStream,
    zlib.createGzip(),
    writeStream
  );
  
  // Hash separately
  const hashStream = fs.createReadStream(inputPath);
  hashStream.pipe(sha256);
  
  hashStream.on('end', () => {
    hash = sha256.digest('hex');
    console.log('SHA256:', hash);
  });
}
```

### Backpressure Handling

```javascript
import fs from 'node:fs';

const readStream = fs.createReadStream('large-file.txt');
const writeStream = fs.createWriteStream('output.txt');

// Monitor backpressure
readStream.on('drain', () => {
  console.log('Write stream drained, can write more');
});

// Pause on high water mark
readStream.on('pause', () => {
  console.log('Read stream paused due to backpressure');
});

readStream.on('resume', () => {
  console.log('Read stream resumed');
});

readStream.pipe(writeStream);
```

### Stream Duplex Examples

#### Net Socket (Duplex)

```javascript
import net from 'node:net';

const server = net.createServer((socket) => {
  // Socket is a Duplex stream
  
  // Read incoming data
  socket.on('data', (data) => {
    console.log('Received:', data.toString());
  });
  
  // Write response
  socket.write('Hello from server\n');
  
  // Can also pipe
  socket.pipe(socket); // Echo server
});

server.listen(3000);
```

## Path Module

### Cross-Platform Path Handling

```javascript
import path from 'node:path';

// Join path segments
const joined = path.join('usr', 'local', 'bin');
// Linux: usr/local/bin
// Windows: usr\local\bin

// Normalize path
const normalized = path.normalize('/usr/../var/./log');
// Result: /var/log

// Get absolute path
const absolute = path.resolve('relative/path');
// Result: /current/working/dir/relative/path

// Get directory name
const dir = path.dirname('/usr/local/bin/node');
// Result: /usr/local/bin

// Get base name
const base = path.basename('/usr/local/bin/node');
// Result: node

// Get base name without extension
const name = path.basename('/usr/local/bin/node', '.exe');
// Result: node

// Get extension
const ext = path.extname('file.tar.gz');
// Result: .gz

// Parse path into object
const parsed = path.parse('/usr/local/bin/node.js');
// {
//   root: '/',
//   dir: '/usr/local/bin',
//   base: 'node.js',
//   ext: '.js',
//   name: 'node'
// }

// Format path object
const formatted = path.format({
  root: '/',
  dir: '/usr/local',
  base: 'bin/node.js'
});
// Result: /usr/local/bin/node.js
```

### Platform-Specific Separators

```javascript
import path from 'node:path';

console.log(path.sep);      // '/' on Linux, '\\' on Windows
console.log(path.delimiter); // ':' on Linux, ';' on Windows (for PATH)

// Use path.join instead of string concatenation
const correct = path.join('folder', 'file.txt');
const wrong = 'folder' + '/' + 'file.txt'; // Breaks on Windows
```

### POSIX and Win32 Paths

```javascript
import { posix, win32 } from 'node:path';

// Force POSIX-style paths (for URLs, etc.)
const urlPath = posix.join('usr', 'local', 'bin');
// Result: usr/local/bin

// Force Windows-style paths
const windowsPath = win32.join('usr', 'local', 'bin');
// Result: usr\local\bin
```

## OS Module

### System Information

```javascript
import os from 'node:os';

// Platform
console.log('Platform:', os.platform()); // 'linux', 'darwin', 'win32'

// Architecture
console.log('Arch:', os.arch()); // 'x64', 'arm64', 'ia32'

// CPU model
console.log('CPU:', os.cpus()[0].model);

// Number of CPUs
console.log('Cores:', os.cpus().length);

// Total memory (bytes)
console.log('Total Mem:', os.totalmem());

// Free memory (bytes)
console.log('Free Mem:', os.freemem());

// System uptime (seconds)
console.log('Uptime:', os.uptime());

// Hostname
console.log('Hostname:', os.hostname());

// OS release
console.log('Release:', os.release());

// User home directory
console.log('Home:', os.homedir());

// Temp directory
console.log('Temp:', os.tmpdir());

// Network interfaces
console.log('Network:', os.networkInterfaces());

// UUID (macOS only)
console.log('UUID:', os.uuid());
```

### CPU Usage Monitoring

```javascript
import os from 'node:os';

const startCpu = os.cpus()[0].times;

// Do some work...
for (let i = 0; i < 1e8; i++) {}

const endCpu = os.cpus()[0].times;

const userTime = endCpu.user - startCpu.user;
const systemTime = endCpu.system - startCpu.system;

console.log(`CPU usage: ${userTime + systemTime}ms`);
```

### Environment Variables

```javascript
import os from 'node:os';

// Get all environment variables
console.log(os.env());

// Same as process.env
console.log(process.env.NODE_ENV);
```

## Best Practices

### Stream Memory Management

```javascript
import fs from 'node:fs';
import { pipeline } from 'node:stream/promises';

// Good: Use streams for large files
async function processLargeFile(input, output) {
  await pipeline(
    fs.createReadStream(input),
    // transform stream here
    fs.createWriteStream(output)
  );
}

// Bad: Load entire file into memory
async function badProcessLargeFile(input, output) {
  const data = await fs.readFile(input); // Memory issue!
  await fs.writeFile(output, data);
}
```

### Error Handling with Streams

```javascript
import { pipeline } from 'node:stream/promises';
import fs from 'node:fs';

// Good: Pipeline handles errors automatically
async function safeCopy(src, dest) {
  try {
    await pipeline(
      fs.createReadStream(src),
      fs.createWriteStream(dest)
    );
  } catch (err) {
    console.error('Copy failed:', err);
    // Streams are automatically destroyed
  }
}

// Bad: Manual pipe requires error handling on each stream
fs.createReadStream('src.txt')
  .on('error', handleError)
  .pipe(fs.createWriteStream('dest.txt'))
  .on('error', handleError);
```

### File Locking Pattern

```javascript
import fs from 'node:fs/promises';

async function withFileLock(filepath, operation) {
  const lockPath = filepath + '.lock';
  
  try {
    // Try to create exclusive lock file
    await fs.open(lockPath, 'wx'); // 'wx' = create exclusively
    
    // Lock acquired, perform operation
    return await operation();
  } catch (err) {
    if (err.code === 'EEXIST') {
      throw new Error('File is locked by another process');
    }
    throw err;
  } finally {
    // Release lock
    try {
      await fs.unlink(lockPath);
    } catch {}
  }
}

// Usage
await withFileLock('data.json', async () => {
  const data = JSON.parse(await fs.readFile('data.json'));
  data.count++;
  await fs.writeFile('data.json', JSON.stringify(data));
});
```
