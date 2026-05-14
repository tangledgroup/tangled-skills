# Process & System

## Shell Scripting (`$`)

Bun Shell provides a cross-platform bash-like shell with seamless JavaScript interop. Written in Zig with its own lexer, parser, and interpreter.

```ts
import { $ } from "bun";

// Basic command
await $`echo "Hello World!"`;

// Quiet mode (no stdout)
await $`echo "Hello!"`.quiet();

// Capture output as text
const output = await $`ls -la`.text();

// Capture as JSON
const json = await $`cat config.json`.json();

// Access raw buffers
const { stdout, stderr } = await $`command`.quiet();

// Interpolation (auto-escaped for safety)
const name = "world";
await $`echo "Hello ${name}!"`;

// Pipes
await $`cat file.txt | wc -l`;

// Use Response as stdin
const response = await fetch("https://example.com");
await $`cat < ${response} | wc -c`;
```

### Error Handling

Non-zero exit codes throw `ShellError` by default:

```ts
try {
  const output = await $`command-that-fails`.text();
} catch (err) {
  console.log(`Exit code: ${err.exitCode}`);
  console.log(err.stdout.toString());
  console.log(err.stderr.toString());
}

// Disable throwing
const result = await $`may-fail`.nothrow().quiet();
if (result.exitCode !== 0) {
  // handle manually
}
```

### Features

- Cross-platform (works on Windows, Linux, macOS without `rimraf` or `cross-env`)
- Glob patterns: `**`, `*`, `{expansion}`
- Template literal interpolation with automatic escaping
- JavaScript interop: `Response`, `ArrayBuffer`, `Blob`, `Bun.file()` as stdin/stdout/stderr
- Shell scripts via `.bun.sh` files

## Child Processes (`Bun.spawn`)

### Async Spawn

```ts
const proc = Bun.spawn(["bun", "--version"]);
console.log(await proc.exited); // exit code

// With options
const proc2 = Bun.spawn(["cat"], {
  cwd: "./subdir",
  env: { ...process.env, FOO: "bar" },
  stdin: "pipe",       // return FileSink for writing
  stdout: "pipe",      // ReadableStream (default)
  stderr: "pipe",
  onExit(proc, exitCode, signal, error) {
    // callback
  },
});

// Write to stdin
proc2.stdin.write("hello");
proc2.stdin.flush();
proc2.stdin.end();

// Read stdout
const output = await proc2.stdout.text();
```

### stdin Options

- `null` — no input (default)
- `"pipe"` — return `FileSink` for incremental writing
- `"inherit"` — inherit parent stdin
- `Bun.file()` — read from file
- `TypedArray` / `DataView` — binary buffer
- `Response` / `Request` — use body as input
- `ReadableStream` — pipe stream to subprocess
- `Blob` — blob data
- `number` — file descriptor

### Sync Spawn

```ts
const result = Bun.spawnSync(["echo", "hello"], {
  stdin: null,
  stdout: "pipe",
  stderr: "pipe",
});

result.exitCode;    // number
result.stdout;      // Buffer
result.stderr;      // Buffer
```

## Workers

Bun implements the Web Workers API for multi-threading. Note: experimental, particularly for termination.

### Main Thread

```ts
const worker = new Worker("./worker.ts");

worker.postMessage("hello");
worker.onmessage = event => {
  console.log(event.data); // "world"
};
```

### Worker Thread

```ts
// worker.ts
declare var self: Worker;

self.onmessage = (event: MessageEvent) => {
  console.log(event.data); // "hello"
  postMessage("world");
};
```

### Worker Options

```ts
const worker = new Worker("./worker.ts", {
  preload: ["./load-sentry.js"],  // load modules before worker starts
});
```

### blob: URLs

Create workers from dynamic content:

```ts
const blob = new Blob([`self.onmessage = (e) => postMessage(e.data)`], {
  type: "application/typescript",
});
const url = URL.createObjectURL(blob);
const worker = new Worker(url);
```

Workers from `blob:` URLs support TypeScript, JSX, and other file types.

## Environment Variables

Bun automatically loads `.env` files. Access via `process.env`:

```ts
console.log(process.env.NODE_ENV);
```

Override with CLI:

```bash
NODE_ENV=production bun run server.ts
```

Or explicitly load:

```bash
bun --env-file=.env.production run server.ts
```

## Cron Jobs

Bun provides a built-in cron scheduler:

```ts
Bun.serve({
  port: 3000,
  fetch(req) {
    return new Response("Hello");
  },
  cron: [
    {
      name: "cleanup",
      pattern: "0 0 * * *",  // every day at midnight
      run(async (cronJob) => {
        console.log("Running cleanup...");
        // cleanup logic
      }),
    },
  ],
});
```
