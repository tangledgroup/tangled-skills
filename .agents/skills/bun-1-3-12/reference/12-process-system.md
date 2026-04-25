# Process & System Operations

Bun provides comprehensive APIs for process management, system operations, environment variables, shell commands, and scheduled tasks (cron jobs).

## Environment Variables

### Reading Environment Variables

```typescript
// Node.js style (compatible)
const nodeEnv = process.env.NODE_ENV;
const apiKey = process.env.API_KEY;

// Bun style (preferred for new code)
const nodeEnv2 = env.NODE_ENV;
const apiKey2 = env.API_KEY;

// Check if variable exists
if ("API_KEY" in env) {
  console.log("API key is set");
}
```

### Setting Environment Variables

```typescript
// Set at runtime (affects child processes only)
process.env.CUSTOM_VAR = "custom value";
env.ANOTHER_VAR = "another value";

// Note: This doesn't affect the parent process
```

### .env File Support

Bun automatically loads `.env` files in development:

```bash title=".env"
NODE_ENV=development
DATABASE_URL=postgres://localhost/dev
API_KEY=secret123
DEBUG=true
```

```typescript title="index.ts"
// Automatically available
console.log(env.DATABASE_URL);  // postgres://localhost/dev
```

Load specific env files:

```bash
# Load .env.production
bun run --env-file .env.production index.ts

# Multiple files (later overrides earlier)
bun run --env-file .env.base --env-file .env.local index.ts
```

### Environment Variable Best Practices

```typescript
// Validate required environment variables
function requireEnv(name: string): string {
  const value = env[name];
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

const databaseUrl = requireEnv("DATABASE_URL");
const apiKey = requireEnv("API_KEY");

// Type-safe environment access
interface Env {
  NODE_ENV: "development" | "production";
  PORT: number;
  DATABASE_URL: string;
}

const typedEnv = {
  NODE_ENV: env.NODE_ENV as "development" | "production",
  PORT: parseInt(env.PORT || "3000"),
  DATABASE_URL: env.DATABASE_URL!,
};
```

## Child Processes

### Spawning Processes

```typescript
// Spawn a child process
const process = Bun.spawn(["node", "--version"]);

// Read output
for await (const line of process.stdout) {
  console.log("Output:", line);
}

const exitCode = await process.exited;
console.log(`Exited with code: ${exitCode}`);
```

### Capturing Output

```typescript
// Capture stdout and stderr
const { stdout, stderr } = await Bun.spawn(["npm", "--version"]);

console.log("stdout:", new TextDecoder().decode(stdout));
console.log("stderr:", new TextDecoder().decode(stderr));
```

### Executing Commands

```typescript
// Execute command and get output (synchronous)
const output = Bun.execSync("git rev-parse --short HEAD");
const commitHash = output.toString().trim();
console.log(`Commit: ${commitHash}`);

// Async version
const process = Bun.spawn(["git", "rev-parse", "--short", "HEAD"]);
const [stdout] = await process;
const hash = new TextDecoder().decode(stdout).trim();
```

### Process with Input

```typescript
// Pipe input to process
const grep = Bun.spawn(["grep", "-n", "error"], {
  stdin: "inherit",
  stdout: "inherit",
  stderr: "inherit",
});

await grep.exited;
```

### Streaming Output

```typescript
// Stream command output in real-time
const ls = Bun.spawn(["ls", "-lah"]);

for await (const chunk of ls.stdout) {
  process.stdout.write(chunk);
}

await ls.exited;
```

### Process Options

```typescript
const process = Bun.spawn(["node", "script.js"], {
  // Working directory
  cwd: "./subdirectory",
  
  // Environment variables
  env: {
    ...env,
    CUSTOM_VAR: "custom value",
  },
  
  // Input data
  stdin: new TextEncoder().encode("input data"),
  
  // Capture output as array of chunks
  stdout: "piped",
  stderr: "piped",
  
  // Or inherit from parent
  // stdin: "inherit",
  // stdout: "inherit",
});

const exitCode = await process.exited;
```

### Process Management

```typescript
// Get process ID
console.log(Bun.pid);  // Current process PID
console.log(process.pid);  // Child process PID

// Kill process
process.kill();  // Default signal: SIGTERM
process.kill("SIGKILL");  // Force kill

// Check if process exited
if (process.exited !== null) {
  console.log(`Process exited with code: ${process.exited}`);
}
```

## Shell Commands

### Running Shell Commands

```typescript
// Execute shell command
const result = Bun.spawnShell("git status");
await result.exited;

// With arguments
const build = Bun.spawnShell("npm run build --if-present");
await build.exited;
```

### Command Chaining

```typescript
// Chain commands with pipes (using shell)
const count = Bun.spawnShell("cat file.txt | grep error | wc -l");
const [stdout] = await count;
console.log(`Error count: ${new TextDecoder().decode(stdout).trim()}`);
```

### Background Processes

```typescript
// Run process in background
const longRunning = Bun.spawn(["node", "long-task.js"], {
  detached: true,
  stdio: "ignore",
});

// Don't wait for it to complete
longRunning.kill("SIGTERM");
```

## Cron Jobs

### Scheduled Tasks

Bun supports cron-like scheduling for background tasks:

```typescript
// Simple interval (every 5 minutes)
setInterval(async () => {
  console.log("Running scheduled task...");
  await cleanupDatabase();
}, 5 * 60 * 1000);
```

### Cron Expression Support

Use a cron library or implement with cron-schedule:

```typescript
// Using crontab-like syntax (requires external package)
import { Cron } from "cron";

const cron = new Cron("* * * * *", () => {
  console.log("Runs every minute");
});

cron.start();
```

### Built-in Scheduling Pattern

```typescript
function scheduleTask(cronExpression: string, callback: () => void) {
  const nextRun = parseCronExpression(cronExpression); // Implement or use library
  
  const runTask = () => {
    callback();
    
    const next = parseCronExpression(cronExpression);
    const delay = next.getTime() - Date.now();
    
    setTimeout(runTask, delay);
  };
  
  const firstDelay = nextRun.getTime() - Date.now();
  setTimeout(runTask, Math.max(firstDelay, 0));
}

// Usage
scheduleTask("0 * * * *", () => {
  console.log("Runs every hour at minute 0");
});

scheduleTask("0 0 * * *", () => {
  console.log("Runs daily at midnight");
});

scheduleTask("0 0 * * 0", () => {
  console.log("Runs weekly on Sunday at midnight");
});
```

### Common Cron Patterns

```typescript
// Every minute
"* * * * *"

// Every hour
"0 * * * *"

// Every day at midnight
"0 0 * * *"

// Every day at 9:30 AM
"30 9 * * *"

// Every weekday (Mon-Fri) at 8 AM
"0 8 * * 1-5"

// First day of every month
"0 0 1 * *"

// Every 15 minutes
"*/15 * * * *"

// Every 6 hours
"0 */6 * * *"
```

### Background Job Pattern

```typescript
class JobScheduler {
  private jobs: Map<string, NodeJS.Timeout> = new Map();
  
  schedule(id: string, cronExpression: string, callback: () => Promise<void>) {
    // Clear existing job
    if (this.jobs.has(id)) {
      clearTimeout(this.jobs.get(id)!);
    }
    
    const runJob = async () => {
      try {
        await callback();
      } catch (error) {
        console.error(`Job ${id} failed:`, error);
      }
      
      // Schedule next run
      const nextDelay = this.calculateNextDelay(cronExpression);
      this.jobs.set(id, setTimeout(runJob, nextDelay) as unknown as NodeJS.Timeout);
    };
    
    // Start job
    const firstDelay = this.calculateNextDelay(cronExpression);
    this.jobs.set(id, setTimeout(runJob, firstDelay) as unknown as NodeJS.Timeout);
  }
  
  cancel(id: string) {
    const job = this.jobs.get(id);
    if (job) {
      clearTimeout(job);
      this.jobs.delete(id);
    }
  }
  
  private calculateNextDelay(cronExpression: string): number {
    // Simplified implementation - use a proper cron library in production
    const parts = cronExpression.split(" ");
    const minute = parts[0];
    
    if (minute === "*") return 60 * 1000;  // Every minute
    if (minute === "*/15") return 15 * 60 * 1000;  // Every 15 minutes
    
    return 60 * 60 * 1000;  // Default: every hour
  }
}

// Usage
const scheduler = new JobScheduler();

scheduler.schedule("cleanup", "0 * * * *", async () => {
  console.log("Running cleanup job...");
  await cleanupTemporaryFiles();
});

scheduler.schedule("backup", "0 2 * * *", async () => {
  console.log("Running backup job...");
  await backupDatabase();
});

// Graceful shutdown
process.on("SIGINT", () => {
  scheduler.jobs.forEach((job) => clearTimeout(job));
  process.exit(0);
});
```

## System Information

### Operating System Info

```typescript
// Platform information
console.log(process.platform);  // "linux", "darwin", "win32"
console.log(process.arch);      // "x64", "arm64", etc.
console.log(process.version);   // Node.js version compatibility
console.log(Bun.version);       // Bun version

// CPU information
console.log(os.cpus());  // Array of CPU info

// Memory information
console.log(os.totalmem());    // Total system memory
console.log(os.freemem());     // Free system memory

// Uptime
console.log(os.uptime());      // System uptime in seconds
console.log(process.uptime()); // Process uptime in seconds
```

### Network Information

```typescript
// Network interfaces
const networkInterfaces = os.networkInterfaces();
for (const [name, interfaces] of Object.entries(networkInterfaces)) {
  for (const config of interfaces) {
    console.log(`${name}: ${config.address} (${config.family})`);
  }
}

// Hostname
console.log(os.hostname());
```

### File System Information

```typescript
// Free disk space
const fs = require("fs");

function getDiskSpace(path: string = "/") {
  const stats = os.freemem();  // Note: Bun doesn't have direct disk space API yet
  return stats;
}

// Use child process for detailed info
const df = Bun.spawnShell("df -h /");
const [stdout] = await df;
console.log(stdout.toString());
```

## Process Signals

### Handling Signals

```typescript
// Graceful shutdown
let shuttingDown = false;

const gracefulShutdown = async (signal: string) => {
  if (shuttingDown) return;
  shuttingDown = true;
  
  console.log(`Received ${signal}, shutting down gracefully...`);
  
  try {
    // Close database connections
    await db.close();
    
    // Finish ongoing requests
    await server.waitForIdle();
    
    // Cleanup
    console.log("Cleanup complete");
  } catch (error) {
    console.error("Error during shutdown:", error);
  } finally {
    process.exit(0);
  }
};

process.on("SIGTERM", () => gracefulShutdown("SIGTERM"));
process.on("SIGINT", () => gracefulShutdown("SIGINT"));

// Ignore SIGTERM for worker processes (handled by parent)
process.on("SIGTERM", () => {
  console.log("Worker received SIGTERM, cleaning up...");
  // Cleanup and exit
  process.exit(0);
});
```

### Sending Signals

```typescript
// Send signal to process
const child = Bun.spawn(["node", "app.js"]);

// Send SIGTERM after 10 seconds
setTimeout(() => {
  child.kill("SIGTERM");
}, 10000);

// Force kill if still running
setTimeout(() => {
  child.kill("SIGKILL");
}, 15000);
```

## Performance Monitoring

### Memory Usage

```typescript
// Get memory usage
const memUsage = process.memoryUsage();
console.log(`Heap used: ${Math.round(memUsage.heapUsed / 1024 / 1024)}MB`);
console.log(`Heap total: ${Math.round(memUsage.heapTotal / 1024 / 1024)}MB`);
console.log(`RSS: ${Math.round(memUsage.rss / 1024 / 1024)}MB`);

// Monitor memory over time
setInterval(() => {
  const usage = process.memoryUsage();
  console.log(`Memory: ${(usage.heapUsed / 1024 / 1024).toFixed(2)}MB`);
}, 5000);
```

### CPU Usage

```typescript
// Get CPU usage (requires tracking over time)
let lastCpuUsage = process.cpuUsage();

setInterval(() => {
  const cpuUsage = process.cpuUsage(lastCpuUsage);
  lastCpuUsage = process.cpuUsage();
  
  console.log(`CPU user: ${cpuUsage.user.toFixed(0)}ms`);
  console.log(`CPU system: ${cpuUsage.system.toFixed(0)}ms`);
}, 1000);
```

### Event Loop Lag

```typescript
// Measure event loop lag
function measureEventLoopLag(): number {
  const start = Date.now();
  return Date.now() - start;
}

// More accurate measurement using process.hrtime
function measureEventLoopLagPrecise(): number {
  const start = process.hrtime.bigint();
  return Number(process.hrtime.bigint() - start) / 1000000; // Convert to ms
}

setInterval(() => {
  const lag = measureEventLoopLag();
  if (lag > 10) {
    console.warn(`Event loop lag: ${lag.toFixed(2)}ms`);
  }
}, 1000);
```

## Resource Limits

### Ulimit Configuration

```typescript
// Check file descriptor limit
const ulimit = Bun.spawnShell("ulimit -n");
const [stdout] = await ulimit;
console.log(`Max open files: ${stdout.toString().trim()}`);

// Set limits (requires appropriate permissions)
Bun.spawnShell("ulimit -n 65536");  // Set max open files to 65536
```

### Memory Limits

```typescript
// Get heap size limit
const heapLimit = process.env.NODE_OPTIONS || "";
console.log(`Node options: ${heapLimit}`);

// Set memory limit (use when starting Bun)
// bun run --max-old-space-size=4096 index.ts
```

## Best Practices

1. **Always handle signals** for graceful shutdown
2. **Use environment variables** for configuration, not hardcoded values
3. **Validate environment variables** at startup
4. **Log process information** in production for debugging
5. **Monitor resource usage** to detect leaks
6. **Use child processes** for CPU-intensive tasks
7. **Implement retry logic** for scheduled jobs
8. **Keep cron jobs idempotent** to handle retries safely

## Troubleshooting

### Process Won't Exit

```typescript
// Check for open handles
console.log("Open handles:", process.openHandles);

// Force exit if needed
process.exit(1);
```

### Environment Variables Not Loading

```bash
# Ensure .env file is in project root
ls -la .env

# Load manually if needed
export $(cat .env | grep -v '^#' | xargs)
bun run index.ts
```

### Child Process Hanging

```typescript
const child = Bun.spawn(["command"], {
  timeout: 30000,  // 30 second timeout
});

try {
  await Promise.race([
    child.exited,
    new Promise((_, reject) => 
      setTimeout(() => reject(new Error("Timeout")), 30000)
    ),
  ]);
} catch (error) {
  child.kill("SIGKILL");
  throw error;
}
```

## Related Documentation

- [Runtime Basics](references/01-runtime-basics.md) - Environment variables overview
- [HTTP Server](references/06-http-server.md) - Graceful shutdown examples
- [Data Storage](references/07-data-storage.md) - Database connection management
- [CI/CD & Deployment](references/10-ci-cd-deployment.md) - Production deployment patterns
