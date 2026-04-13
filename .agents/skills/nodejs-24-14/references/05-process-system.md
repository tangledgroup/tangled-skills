# Process and System Reference

This document covers Node.js 24.14 process management, child processes, clustering, V8 tuning, and OS utilities.

## Process Module

### Process Events

```javascript
import process from 'node:process';

// Uncaught exceptions
process.on('uncaughtException', (err) => {
  console.error('Uncaught exception:', err);
  // Clean up and exit
  process.exit(1);
});

// Unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled rejection:', reason);
});

// Warning events
process.on('warning', (warning) => {
  console.warn(warning.name, warning.message);
});

// Before exit (synchronous only!)
process.on('beforeExit', (code) => {
  console.log('Before exit with code:', code);
  // Starting async work will restart the event loop
});

// Exit event (cannot be listened to)
// process.on('exit', ...) // This won't work!
```

### Process Signals

```javascript
import process from 'node:process';

// Graceful shutdown on SIGTERM
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully...');
  
  // Close servers, databases, etc.
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});

// Handle SIGINT (Ctrl+C)
process.on('SIGINT', () => {
  console.log('SIGINT received');
  process.exit(130); // 128 + 2 (SIGINT)
});

// Handle SIGHUP (terminal closed)
process.on('SIGHUP', () => {
  console.log('SIGHUP received, reloading configuration...');
  reloadConfig();
});

// Ignore SIGUSR1 for custom handling
process.on('SIGUSR1', () => {
  console.log('SIGUSR1 - Dumping heap snapshot');
  process._rawDebug('Heap dump requested');
});

// Send signal to self (for testing)
process.kill(process.pid, 'SIGUSR1');
```

### Environment Variables

```javascript
import process from 'node:process';

// Read environment variable
const port = process.env.PORT || 3000;
const env = process.env.NODE_ENV;

// Check if variable exists
if (process.env.API_KEY) {
  console.log('API key is set');
}

// Modify environment variable
process.env.DEBUG = 'true';

// Delete environment variable
delete process.env.TEMP_VAR;

// Get all environment variables
console.log(Object.keys(process.env));

// Common environment variables
console.log('NODE_ENV:', process.env.NODE_ENV);      // development, production, test
console.log('PATH:', process.env.PATH);              // System PATH
console.log('HOME:', process.env.HOME);              // User home directory
console.log('PWD:', process.env.PWD);                // Current working directory
```

### Process Arguments

```javascript
import process from 'node:process';

// All arguments
console.log(process.argv);
// [ '/usr/bin/node', '/path/to/script.js', 'arg1', 'arg2' ]

// Script path
console.log(process.argv[1]); // /path/to/script.js

// Arguments after script
console.log(process.argv.slice(2)); // ['arg1', 'arg2']

// Check for specific flag
if (process.argv.includes('--verbose')) {
  console.log('Verbose mode enabled');
}

// Get value of flag
const index = process.argv.indexOf('--port');
if (index !== -1 && index + 1 < process.argv.length) {
  const port = parseInt(process.argv[index + 1], 10);
  console.log('Port:', port);
}
```

### Process Exit Codes

```javascript
import process from 'node:process';

// Standard exit codes
process.exit(0);   // Success
process.exit(1);   // General error
process.exit(2);   // Misuse of shell builtins (POSIX)
process.exit(126); // Command invoked cannot execute
process.exit(127); // Command not found
process.exit(128); // Invalid exit argument
process.exit(130); // Terminated by SIGINT (Ctrl+C)
process.exit(137); // Terminated by SIGKILL

// Set exit code without exiting
process.exitCode = 1;
```

### Process Information

```javascript
import process from 'node:process';

console.log('PID:', process.pid);           // Current process ID
console.log('PPID:', process.ppid);         // Parent process ID
console.log('UID:', process.getuid());      // User ID (Unix)
console.log('GID:', process.getgid());      // Group ID (Unix)
console.log('Platform:', process.platform); // 'linux', 'darwin', 'win32'
console.log('Arch:', process.arch);         // 'x64', 'arm64', etc.
console.log('Version:', process.version);   // 'v24.14.0'
console.log('Versions:', process.versions); // All dependency versions
console.log('Uptime:', process.uptime());   // Seconds since start
console.log('CWD:', process.cwd());         // Current working directory

// Memory usage
const mem = process.memoryUsage();
console.log('Heap used:', mem.heapUsed / 1024 / 1024, 'MB');
console.log('Heap total:', mem.heapTotal / 1024 / 1024, 'MB');
console.log('RSS:', mem.rss / 1024 / 1024, 'MB');

// CPU usage
const startUsage = process.cpuUsage();
// ... do some work ...
const endUsage = process.cpuUsage(startUsage);
console.log('User CPU time:', endUsage.user, 'ms');
console.log('System CPU time:', endUsage.system, 'ms');
```

### Working Directory

```javascript
import process from 'node:process';

// Get current working directory
const cwd = process.cwd();

// Change working directory
process.chdir('/tmp');
console.log(process.cwd()); // /tmp

// Check if path exists before changing
import fs from 'node:fs/promises';

async function safeChdir(path) {
  try {
    await fs.access(path);
    process.chdir(path);
  } catch (err) {
    console.error('Cannot change to', path, ':', err.message);
  }
}
```

## Child Process Module

### Spawn - Low-Level Process Creation

```javascript
import { spawn } from 'node:child_process';

// Spawn a process
const ls = spawn('ls', ['-lh', '/usr']);

ls.stdout.on('data', (data) => {
  console.log(`stdout: ${data}`);
});

ls.stderr.on('data', (data) => {
  console.error(`stderr: ${data}`);
});

ls.on('close', (code) => {
  console.log(`Child process exited with code ${code}`);
});

// Spawn with options
const grep = spawn('grep', ['ssh'], {
  stdio: ['pipe', 'pipe', 'pipe'],
  env: { ...process.env, LANG: 'en_US.UTF-8' }
});
```

### Spawn with Stdin Input

```javascript
import { spawn } from 'node:child_process';

const cat = spawn('cat');

cat.stdin.write('Hello\n');
cat.stdin.write('World\n');
cat.stdin.end();

cat.stdout.on('data', (data) => {
  console.log(data.toString());
});
```

### Exec - Capturing Output

```javascript
import { exec, execFile } from 'node:child_process';
import { promisify } from 'node:util';

const execAsync = promisify(exec);
const execFileAsync = promisify(execFile);

// Using async/await
async function runCommand() {
  try {
    const { stdout, stderr } = await execAsync('ls -lh /usr');
    console.log(stdout);
  } catch (err) {
    console.error('Execution failed:', err.message);
    console.error('Stderr:', err.stderr);
    console.error('Exit code:', err.code);
  }
}

// With timeout and maxBuffer
async function runWithLimits() {
  const { stdout } = await execAsync('slow-command', {
    timeout: 5000,      // Kill after 5 seconds
    maxBuffer: 1024 * 1024 // 1MB buffer limit
  });
}

// Using execFile (safer, no shell)
async function runExecutable() {
  const { stdout } = await execFileAsync('node', ['script.js', 'arg1', 'arg2']);
  console.log(stdout);
}
```

### Fork - Node.js Process with IPC

```javascript
import { fork } from 'node:child_process';

// Fork a worker process
const worker = fork('./worker.js');

// Send message to worker
worker.send({ msg: 'Hello worker', data: 123 });

// Receive message from worker
worker.on('message', (msg) => {
  console.log('Received from worker:', msg);
});

// Handle worker exit
worker.on('exit', (code, signal) => {
  console.log(`Worker exited with code ${code}, signal ${signal}`);
});

// Send data back to parent (in worker.js)
process.on('message', (msg) => {
  console.log('Worker received:', msg);
  
  // Send response
  process.parentPort?.postMessage({ result: 'Done' });
  // Or for older Node.js:
  // process.send({ result: 'Done' });
});
```

### Worker Thread Example (worker.js)

```javascript
// worker.js
import { parentPort } from 'node:worker_threads';

parentPort?.on('message', (msg) => {
  if (msg.type === 'compute') {
    const result = heavyComputation(msg.data);
    parentPort.postMessage({ type: 'result', data: result });
  }
  
  if (msg.type === 'exit') {
    parentPort.close();
  }
});

function heavyComputation(data) {
  // CPU-intensive work
  let sum = 0;
  for (let i = 0; i < data * 1e6; i++) {
    sum += Math.sqrt(i) * Math.sin(i);
  }
  return sum;
}
```

### Exec with Streaming Output

```javascript
import { exec } from 'node:child_process';

const ps = exec('ps aux');

ps.stdout.on('data', (data) => {
  // Process output line by line as it comes
  const lines = data.toString().split('\n');
  for (const line of lines) {
    if (line.trim()) {
      console.log('Process:', line);
    }
  }
});

ps.stderr.on('data', (data) => {
  console.error('Error:', data);
});
```

## Cluster Module

### Master-Worker Pattern

```javascript
// server.js (master process)
import cluster from 'node:cluster';
import http from 'node:http';
import os from 'node:os';

if (cluster.isPrimary) {
  console.log(`Primary ${process.pid} is running`);
  
  // Fork workers based on CPU count
  const numCPUs = os.cpus().length;
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }
  
  // Handle worker exit
  cluster.on('exit', (worker, code, signal) => {
    console.log(`Worker ${worker.process.pid} died`);
    
    // Restart worker
    console.log('Starting new worker...');
    cluster.fork();
  });
  
  // Handle online events
  cluster.on('online', (worker) => {
    console.log(`Worker ${worker.process.pid} is online`);
  });
  
} else {
  // Worker code
  const server = http.createServer((req, res) => {
    res.writeHead(200);
    res.end(`Handled by worker ${process.pid}\n`);
  });
  
  server.listen(8080, () => {
    console.log(`Worker ${process.pid} listening on port 8080`);
  });
}
```

### Custom Fork Settings

```javascript
import cluster from 'node:cluster';
import os from 'node:os';

if (cluster.isPrimary) {
  // Fork with custom environment
  cluster.fork({
    env: {
      ...process.env,
      WORKER_ID: '1',
      LOG_LEVEL: 'debug'
    }
  });
  
  // Fork with resource constraints (Node.js 12+)
  cluster.fork({
    execArgv: ['--max-old-space-size=512']
  });
}
```

### Load Balancing Strategies

```javascript
import cluster from 'node:cluster';

// Default: round-robin (all platforms)
cluster.setupMaster({});

// For older Node.js versions on Windows: polling
// cluster.setupMaster({ scheduling: 'polling' });

// Get worker statistics
function getWorkerStats() {
  const stats = {};
  for (const [id, worker] of Object.entries(cluster.workers)) {
    stats[id] = {
      pid: worker.process.pid,
      sending: worker.sendingMessage,
      suicide: worker.suicide
    };
  }
  return stats;
}

console.log(getWorkerStats());
```

### Graceful Shutdown with Cluster

```javascript
import cluster from 'node:cluster';
import http from 'node:http';

let servers = [];

if (cluster.isPrimary) {
  cluster.fork();
  cluster.fork();
  
  process.on('SIGTERM', async () => {
    console.log('Shutting down gracefully...');
    
    // Disconnect to stop receiving new connections
    cluster.disconnect((err) => {
      if (err) {
        console.error('Error during disconnect:', err);
        process.exit(1);
      }
      
      console.log('All workers stopped');
      process.exit(0);
    });
    
    // Force exit after timeout
    setTimeout(() => {
      console.error('Timeout, forcing exit');
      process.exit(1);
    }, 30000);
  });
  
} else {
  const server = http.createServer((req, res) => {
    res.end(`Worker ${process.pid}`);
  });
  
  server.listen(8080);
  servers.push(server);
  
  // Worker handles SIGTERM by closing its server
  process.on('SIGTERM', () => {
    console.log(`Worker ${process.pid} shutting down`);
    
    server.close(() => {
      console.log(`Worker ${process.pid} closed`);
      process.exit(0);
    });
    
    // Force close after timeout
    setTimeout(() => {
      console.error(`Worker ${process.pid} forcing exit`);
      process.exit(1);
    }, 5000);
  });
}
```

## V8 Module

### Memory Management

```javascript
import v8 from 'node:v8';

// Get heap statistics
const stats = v8.getHeapStatistics();
console.log('Heap size:', stats.heap_size / 1024 / 1024, 'MB');
console.log('Heap used:', stats.used_heap_size / 1024 / 1024, 'MB');
console.log('Available:', stats.heap_size_limit / 1024 / 1024, 'MB');

// Get space statistics (detailed breakdown)
const spaces = v8.getHeapSpaceStatistics();
for (const space of spaces) {
  console.log(`${space.space_name}:`);
  console.log(`  Size: ${space.space_size_used / 1024 / 1024} MB`);
  console.log(`  Capacity: ${space.space_capacity / 1024 / 1024} MB`);
}

// Force garbage collection (use with --expose-gc flag)
if (global.gc) {
  console.log('Before GC:', v8.getHeapStatistics().used_heap_size);
  global.gc();
  console.log('After GC:', v8.getHeapStatistics().used_heap_size);
}

// Set heap limits
v8.setFlagsFromString('--max_old_space_size=512');
```

### CPU Profiling

```javascript
import v8 from 'node:v8';

// Start profiling
v8.startProfiling('my-profile');

// Run your code...
for (let i = 0; i < 1e6; i++) {
  Math.sqrt(i);
}

// Stop and get profile
const profile = v8.stopProfiling('my-profile');

// Process profile data
function processProfile(profile, indent = '') {
  console.log(`${indent}${profile.functionName} (${profile.hits} hits)`);
  
  for (const child of profile.children || []) {
    processProfile(child, indent + '  ');
  }
}

processProfile(profile);

// Get all profiles
const allProfiles = v8.getProfilingData();
```

### Code Cache

```javascript
import v8 from 'node:v8';

// Serialize function to buffer
function myFunction() {
  return 42;
}

const buffer = v8.serialize(myFunction);
console.log('Serialized size:', buffer.length, 'bytes');

// Deserialize and execute
const deserialized = v8.deserialize(buffer);
console.log(deserialized()); // 42

// Get serialization statistics
const stats = v8.getHeapSnapshot();
```

### Heap Snapshot

```javascript
import v8 from 'node:v8';
import fs from 'node:fs/promises';

// Create heap snapshot
async function takeHeapSnapshot(filepath = 'heap-snapshot.heapsnapshot') {
  const snapshot = v8.getHeapSnapshot();
  
  // Save to file (for Chrome DevTools)
  await fs.writeFile(filepath, JSON.stringify(snapshot));
  console.log('Heap snapshot saved to', filepath);
}

// Usage
await takeHeapSnapshot();

// Load and analyze in Chrome DevTools:
// chrome://devtools > Memory > Load
```

### Serializer/Deserializer

```javascript
import v8 from 'node:v8';

// Custom serializer with external data
class CustomSerializer extends v8.Serializer {
  writeNumber(num) {
    this.writeHostObject({ type: 'number', value: num });
  }
}

// Custom deserializer
class CustomDeserializer extends v8.Deserializer {
  readHostObject() {
    const { type, value } = this.readHostObject();
    if (type === 'number') return value;
    return super.readHostObject();
  }
}

const serializer = new CustomSerializer();
serializer.writeNumber(42);
const buffer = serializer.release();

const deserializer = new CustomDeserializer(buffer);
console.log(deserializer.deserialize()); // 42
```

## OS Module Extended

### CPU Information

```javascript
import os from 'node:os';

// Get CPU details
const cpus = os.cpus();
console.log('CPU Model:', cpus[0].model);
console.log('Speed:', cpus[0].speed, 'MHz');
console.log('Cores:', cpus.length);

// CPU usage by core
function getCpuUsage() {
  const startUsage = os.cpus().map(cpu => cpu.times);
  
  // Wait a bit
  const start = Date.now();
  while (Date.now() - start < 1000);
  
  const endUsage = os.cpus().map(cpu => cpu.times);
  
  for (let i = 0; i < startUsage.length; i++) {
    const start = startUsage[i];
    const end = endUsage[i];
    
    const startTotal = Object.values(start).reduce((a, b) => a + b, 0);
    const endTotal = Object.values(end).reduce((a, b) => a + b, 0);
    
    const idleStart = start.idle;
    const idleEnd = end.idle;
    
    const usage = 1 - (idleEnd - idleStart) / (endTotal - startTotal);
    
    console.log(`CPU ${i}: ${(usage * 100).toFixed(2)}%`);
  }
}

getCpuUsage();
```

### Network Interfaces

```javascript
import os from 'node:os';

const interfaces = os.networkInterfaces();

for (const [name, config] of Object.entries(interfaces)) {
  console.log(`Interface: ${name}`);
  
  for (const cfg of config) {
    if (cfg.family === 'IPv4' && !cfg.internal) {
      console.log(`  IPv4: ${cfg.address}/${cfg.netmask}`);
    } else if (cfg.family === 'IPv6') {
      console.log(`  IPv6: ${cfg.address}`);
    }
  }
}

// Get default interface IP
function getDefaultIPv4() {
  const interfaces = os.networkInterfaces();
  
  for (const config of Object.values(interfaces)) {
    for (const cfg of config) {
      if (cfg.family === 'IPv4' && !cfg.internal) {
        return cfg.address;
      }
    }
  }
  
  return null;
}

console.log('Default IPv4:', getDefaultIPv4());
```

### Load Average

```javascript
import os from 'node:os';

// Get load average (Unix only, returns [0] on Windows)
const loadAvg = os.loadavg();
console.log('1 min:', loadAvg[0]);
console.log('5 min:', loadAvg[1]);
console.log('15 min:', loadAvg[2]);

// Calculate CPU load percentage
function getLoadPercentage() {
  const load = os.loadavg()[0];
  const cpus = os.cpus().length;
  
  return Math.round((load / cpus) * 100);
}

console.log('CPU Load:', getLoadPercentage(), '%');
```

### System Information

```javascript
import os from 'node:os';

// Comprehensive system info
function getSystemInfo() {
  return {
    platform: os.platform(),
    arch: os.arch(),
    release: os.release(),
    hostname: os.hostname(),
    uptime: Math.round(os.uptime() / 60 / 60) + ' hours',
    cpus: {
      model: os.cpus()[0].model,
      cores: os.cpus().length
    },
    memory: {
      total: (os.totalmem() / 1024 / 1024 / 1024).toFixed(2) + ' GB',
      free: (os.freemem() / 1024 / 1024 / 1024).toFixed(2) + ' GB',
      used: ((os.totalmem() - os.freemem()) / 1024 / 1024 / 1024).toFixed(2) + ' GB'
    },
    user: os.userInfo().username,
    cwd: process.cwd()
  };
}

console.log(JSON.stringify(getSystemInfo(), null, 2));
```

## Performance Monitoring

### Event Loop Lag

```javascript
import { performance } from 'node:perf_hooks';

function measureEventLoopLag(iterations = 10) {
  const lags = [];
  
  return new Promise((resolve) => {
    function measure() {
      if (lags.length >= iterations) {
        const avgLag = lags.reduce((a, b) => a + b, 0) / lags.length;
        resolve({
          average: avgLag,
          max: Math.max(...lags),
          min: Math.min(...lags),
          samples: lags
        });
        return;
      }
      
      const start = performance.now();
      setImmediate(() => {
        lags.push(performance.now() - start);
        measure();
      });
    }
    
    measure();
  });
}

// Usage
measureEventLoopLag(100).then(stats => {
  console.log('Event loop lag:', stats.average.toFixed(2), 'ms average');
});
```

### Memory Monitoring Over Time

```javascript
import v8 from 'node:v8';

function monitorMemory(interval = 1000, duration = 60000) {
  const samples = [];
  const end = Date.now() + duration;
  
  const timer = setInterval(() => {
    const stats = v8.getHeapStatistics();
    samples.push({
      time: Date.now(),
      heapUsed: stats.used_heap_size,
      heapTotal: stats.heap_size,
      external: stats.external_memory_size
    });
    
    if (Date.now() > end) {
      clearInterval(timer);
      console.log('Memory samples:', samples.length);
      console.log('Peak heap used:', Math.max(...samples.map(s => s.heapUsed)) / 1024 / 1024, 'MB');
    }
  }, interval);
}

// Usage
// monitorMemory(1000, 30000); // Monitor for 30 seconds
```
