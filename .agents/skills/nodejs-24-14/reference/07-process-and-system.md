# Process and System APIs

## process — The Current Process

### Properties

```javascript
process.pid;              // current process ID
process.ppid;             // parent process ID
process.platform;         // 'linux', 'darwin', 'win32'
process.arch;             // 'x64', 'arm64'
process.version;          // 'v24.14.0'
process.argv;             // command-line arguments array
process.execPath;         // path to node executable
process.cwd();            // current working directory (string)
process.chdir('/path');   // change working directory
process.env;              // environment variables object
process.stdin;            // readable stream for standard input
process.stdout;           // writable stream for standard output
process.stderr;           // writable stream for standard error
process.exitCode;         // exit code (set before process exits)
process.mainModule;       // the main module (CommonJS)
process.execArgv;         // Node.js-specific CLI args
process.memoryUsage();    // { rss, heapTotal, heapUsed, external, arrayBuffers }
process.cpuUsage();       // { user, system } in microseconds
process.hrtime.bigint();  // high-resolution time in nanoseconds
process.loadEnvFile();    // load .env file (Node 20+)
```

### Process Events

```javascript
// Uncaught exception
process.on('uncaughtException', (err, origin) => {
  console.error('Uncaught Exception:', err);
  process.exit(1);
});

// Unhandled promise rejection
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

// Signal handlers
process.on('SIGINT', () => {
  console.log('Received SIGINT (Ctrl+C)');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('Received SIGTERM, shutting down gracefully...');
  server.close(() => process.exit(0));
});

// Warning
process.on('warning', (warning) => {
  console.warn(warning.name, warning.message, warning.code);
});

// Before exit (runs before 'exit')
process.on('beforeExit', (code) => {
  console.log('Process about to exit with code:', code);
});

// Exit (synchronous only — async calls won't fire)
process.on('exit', (code) => {
  fs.writeFileSync('log.txt', `Exited with code ${code}`);
});
```

### process.nextTick and Microtasks

```javascript
// nextTick fires before any other async callback
process.nextTick(() => {
  console.log('nextTick');
});

// queueMicrotask is the standard equivalent
queueMicrotask(() => {
  console.log('microtask');
});

// Both run after current operation, before event loop continues
```

### Memory and Resource Usage

```javascript
const mem = process.memoryUsage();
console.log(`RSS: ${(mem.rss / 1024 / 1024).toFixed(2)} MB`);
console.log(`Heap total: ${(mem.heapTotal / 1024 / 1024).toFixed(2)} MB`);
console.log(`Heap used: ${(mem.heapUsed / 1024 / 1024).toFixed(2)} MB`);
console.log(`External: ${(mem.external / 1024).toFixed(2)} KB`);

// Available memory (system-wide)
process.availableMemory();
process.constrainedMemory();
process.totalmem();

// CPU usage since last call
const start = process.cpuUsage();
doWork();
const end = process.cpuUsage(start);
console.log(`User: ${end.user}μs, System: ${end.system}μs`);

// High-resolution time
const time1 = process.hrtime.bigint();
doWork();
const time2 = process.hrtime.bigint();
console.log(`Elapsed: ${(Number(time2 - time1) / 1e6).toFixed(2)}ms`);
```

### Permission Model (Node 21+)

```javascript
import { permission } from 'node:process';

// Check if fs access is allowed
if (permission.has('fs')) {
  // safe to use fs
}

// Deny specific resources
permission.deny('fs', '/etc/shadow');

// Hook into permission checks
permission.hook.add((request, callback) => {
  if (request.resourceType === 'fs' && request.path.startsWith('/secret')) {
    callback(new Error('Access denied'));
  } else {
    callback();
  }
});
```

## child_process — Spawning Processes

### execFile — Run External Commands (Preferred)

```javascript
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

const execFileAsync = promisify(execFile);

// Safe — doesn't use shell, args are properly escaped
const { stdout, stderr } = await execFileAsync('python3', ['--version'], {
  encoding: 'utf-8',
  timeout: 5000,
  maxBuffer: 10 * 1024 * 1024, // 10MB
});
console.log(stdout);
```

### spawn — Stream-Based Process Execution

```javascript
import { spawn } from 'node:child_process';

const child = spawn('find', ['.', '-name', '*.js'], {
  stdio: ['inherit', 'pipe', 'inherit'],
});

child.stdout.on('data', (data) => {
  console.log(`Output: ${data}`);
});

child.stderr.on('data', (data) => {
  console.error(`Error: ${data}`);
});

child.on('close', (code) => {
  console.log(`Child process exited with code ${code}`);
});

child.on('error', (err) => {
  console.error('Failed to start child:', err);
});

// Write to child stdin
child.stdin.write('input data\n');
child.stdin.end();
```

### spawn with Promise (Node 22+)

```javascript
import { spawn } from 'node:child_process';

const child = spawn('ls', ['-la'], { stdio: 'pipe', encoding: 'utf-8' });

// Wait for exit with result
const { stdout, stderr, status, signal } = await child;
console.log(`Exit code: ${status}`);
console.log(stdout);
```

### exec — Shell Commands (Use Carefully)

```javascript
import { exec } from 'node:child_process';
import { promisify } from 'node:util';

const execAsync = promisify(exec);

// WARNING: shell injection risk with user input!
const { stdout } = await execAsync('ls -la | grep ".js"');
console.log(stdout);

// NEVER do this with unsanitized input:
// exec(`ls ${userInput}`); // VULNERABLE
```

### fork — Node.js Child Process with IPC

```javascript
import { fork } from 'node:child_process';

const worker = fork('./worker.js', ['arg1', 'arg2'], {
  env: { NODE_ENV: 'production' },
  stdio: 'inherit',
});

worker.on('message', (msg) => {
  console.log('Message from worker:', msg);
});

worker.on('error', (err) => {
  console.error('Worker error:', err);
});

worker.on('exit', (code) => {
  console.log(`Worker exited with code ${code}`);
});

// Send messages to worker
worker.send({ command: 'process', data: { id: 123 } });

// worker.js
process.on('message', (msg) => {
  if (msg.command === 'process') {
    const result = doWork(msg.data);
    process.send({ result });
  }
});
```

### Subprocess Options

```javascript
const child = spawn('command', ['arg'], {
  cwd: '/path/to/working/dir',
  env: { ...process.env, CUSTOM_VAR: 'value' },
  stdio: ['inherit', 'pipe', 'inherit'], // stdin, stdout, stderr
  // stdio options: 'pipe', 'inherit', 'ignore', or array of 3
  timeout: 10000,        // kill after N ms
  killSignal: 'SIGTERM', // signal to send on kill()
  shell: false,          // don't use shell (safer)
  windowsHide: true,     // hide console window on Windows
});
```

## worker_threads — Parallelism

### Basic Worker

```javascript
import { Worker, isMainThread, parentPort, workerData } from 'node:worker_threads';

if (isMainThread) {
  // Main thread
  const worker = new Worker(import.meta.url, {
    workerData: { start: 0, end: 1000000 },
    resourceLimits: { maxOldGenerationSizeMb: 128 },
  });

  worker.on('message', (result) => {
    console.log('Result from worker:', result);
  });

  worker.on('error', (err) => {
    console.error('Worker error:', err);
    process.exit(1);
  });

  worker.on('exit', (code) => {
    if (code !== 0) {
      console.error(`Worker stopped with exit code ${code}`);
    }
  });
} else {
  // Worker thread
  const { start, end } = workerData;
  let sum = 0;
  for (let i = start; i < end; i++) {
    sum += i;
  }
  parentPort.postMessage({ sum, range: `${start}-${end}` });
}
```

### Pool of Workers

```javascript
import { Worker } from 'node:worker_threads';

class WorkerPool {
  constructor(size, workerScript) {
    this.workers = [];
    this.queue = [];
    this.size = size;

    for (let i = 0; i < size; i++) {
      this.workers.push(this._createWorker(workerScript));
    }
  }

  _createWorker(script) {
    const worker = new Worker(script);
    worker.on('message', (result) => {
      const { resolve } = this.queue.shift() || {};
      resolve?.(result);
      this._dispatch();
    });
    worker.on('error', (err) => {
      const { reject } = this.queue.shift() || {};
      reject?.(err);
      this._dispatch();
    });
    return worker;
  }

  _dispatch() {
    if (this.queue.length > 0) {
      const task = this.queue[0]; // peek
      // assign to available worker
    }
  }

  async execute(data) {
    return new Promise((resolve, reject) => {
      this.queue.push({ data, resolve, reject });
      this._dispatch();
    });
  }
}
```

### MessageChannel and BroadcastChannel

```javascript
import { MessageChannel, MessagePort, BroadcastChannel } from 'node:worker_threads';

// MessageChannel — two-way communication between ports
const { port1, port2 } = new MessageChannel();

port1.on('message', (msg) => {
  console.log('Port1 received:', msg);
});

port2.postMessage({ hello: 'from port2' });

// BroadcastChannel — pub/sub between threads
const bc = new BroadcastChannel('my-channel');
bc.postMessage({ type: 'update', data: 'new value' });
bc.onmessage = (event) => {
  console.log('Broadcast:', event.data);
};
bc.close(); // stop listening
```

### SharedArrayBuffer and Atomics

```javascript
import { Worker, isMainThread, shareMemory } from 'node:worker_threads';

if (isMainThread) {
  const sharedBuffer = new SharedArrayBuffer(BigInt(Int32Array.BYTES_PER_ELEMENT));
  const sharedArray = new Int32Array(sharedBuffer);
  sharedArray[0] = 42;

  const worker = new Worker(`
    import { workerData } from 'node:worker_threads';
    const sab = workerData.sab;
    const arr = new Int32Array(sab);
    arr[0] = arr[0] * 2; // modify shared memory
  `, { workerData: { sab: sharedBuffer } });

  worker.on('exit', () => {
    console.log(sharedArray[0]); // 84
  });
}
```

### Transferable Objects

```javascript
// Transfer Buffer without copying (zero-copy)
const buffer = Buffer.alloc(1024 * 1024);
parentPort.postMessage({ type: 'data', buffer }, [buffer]);
// buffer is now invalid in sender, valid in receiver

// Mark as untransferable (forces copy)
import { markAsUntransferable } from 'node:worker_threads';
markAsUntransferable(buffer);
parentPort.postMessage({ buffer }); // copied, original still valid
```

### Worker Locks (Node 22+)

```javascript
import { locks, Worker } from 'node:worker_threads';

const mutex = new locks.Mutex();

await mutex.acquire();
try {
  // critical section
} finally {
  mutex.release();
}

const rwlock = new locks.ReadWriteLock();
await rwlock.acquireRead();   // multiple readers allowed
// ... read shared data ...
rwlock.releaseRead();

await rwlock.acquireWrite();  // exclusive write access
// ... modify shared data ...
rwlock.releaseWrite();
```

## cluster — Multi-Process Load Balancing

```javascript
import cluster from 'node:cluster';
import http from 'node:http';
import { availableParallelism } from 'node:os';

if (cluster.isPrimary) {
  const numWorkers = availableParallelism();
  console.log(`Forking ${numWorkers} workers...`);

  for (let i = 0; i < numWorkers; i++) {
    cluster.fork();
  }

  cluster.on('exit', (worker, code, signal) => {
    console.log(`Worker ${worker.process.pid} died. Restarting...`);
    cluster.fork();
  });

  cluster.on('online', (worker) => {
    console.log(`Worker ${worker.process.pid} is online`);
  });

  // Graceful shutdown
  process.on('SIGTERM', () => {
    console.log('Primary received SIGTERM. Shutting down workers...');
    for (const worker of Object.values(cluster.workers)) {
      worker.process.kill('SIGTERM');
    }
    setTimeout(() => process.exit(0), 5000);
  });
} else {
  // Worker process
  const server = http.createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end(`Handled by worker ${process.pid}\n`);
  });

  server.listen(8000);
  console.log(`Worker ${process.pid} started`);
}
```

### Cluster Scheduling

```javascript
import cluster from 'node:cluster';
import net from 'net';

// Round-robin scheduling (default on non-Windows)
cluster.schedulingPolicy = cluster.SCHED_RR;

// Random scheduling (Windows default)
cluster.schedulingPolicy = cluster.SCHED_NONE;
```

## os — System Information

```javascript
import os from 'node:os';

os.platform();              // 'linux', 'darwin', 'win32'
os.arch();                  // 'x64', 'arm64'
os.hostname();              // machine hostname
os.homedir();               // user home directory
os.tmpdir();                // temp directory
os.type();                  // 'Linux', 'Darwin', 'Windows_NT'
os.release();               // OS kernel version
os.endianness();            // 'BE' or 'LE'
os.EOL;                     // '\n' or '\r\n'
os.devNull;                 // '/dev/null' or 'NUL'

// CPU info
os.cpus();                  // [{ model, speed, times: { user, nice, sys, idle, irq } }]
os.availableParallelism();  // number of available cores

// Memory
os.totalmem();              // total system memory in bytes
os.freemem();               // free memory in bytes

// Load average
os.loadavg();               // [1min, 5min, 15min]

// Network interfaces
os.networkInterfaces();     // { interfaceName: [{ address, netmask, family, mac, internal }]}

// User info
os.userInfo();              // { uid, gid, username, homedir, shell }

// Process priority
os.getPriority();           // get current process priority
os.setPriority(10);         // set priority (lower = higher priority)
```

## Environment Variables

```javascript
// Read
process.env.NODE_ENV;       // 'production', 'development'
process.env.HOME;           // home directory
process.env.PATH;           // system PATH

// Write (affects child processes only)
process.env.CUSTOM_VAR = 'value';

// Load .env file (Node 20+)
process.loadEnvFile();      // loads .env from cwd
process.loadEnvFile('.env.local'); // specific file

// Command-line flags
process.allowedNodeEnvironmentFlags; // Set of allowed --* flags
```
