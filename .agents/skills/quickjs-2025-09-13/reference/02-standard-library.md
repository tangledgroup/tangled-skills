# Standard Library

QuickJS includes a small built-in standard library with two modules (`std` and `os`) plus a few global objects. The standard library is included by default in the command line interpreter.

## Global Objects

**`scriptArgs`** — Command line arguments array. First element is the script name.

**`print(...args)`** — Print arguments separated by spaces with trailing newline.

**`console.log(...args)`** — Same as `print()`. As of 2025-09-13, objects are pretty-printed.

## std Module

The `std` module wraps libc `stdlib.h` and `stdio.h`:

### Process Control

- `exit(n)` — Exit the process
- `getenv(name)` — Get environment variable value or `undefined`
- `setenv(name, value)` — Set environment variable
- `unsetenv(name)` — Delete environment variable
- `getenviron()` — Return all environment variables as key-value object

### Script Evaluation

- `evalScript(str, options?)` — Evaluate string as script (global eval). Options: `backtrace_barrier` (boolean), `async` (boolean — returns promise with `{value}`)
- `loadScript(filename)` — Evaluate file as script
- `loadFile(filename)` — Load file as UTF-8 string, returns `null` on I/O error

### File I/O

- `open(filename, flags, errorObj?)` — Wrapper to `fopen()`. Returns FILE object or `null`
- `popen(command, flags, errorObj?)` — Wrapper to `popen()`
- `fdopen(fd, flags, errorObj?)` — Wrapper to `fdopen()`
- `tmpfile(errorObj?)` — Open temporary file
- `puts(str)` — Equivalent to `std.out.puts(str)`
- `printf(fmt, ...args)` — Equivalent to `std.out.printf(fmt, ...args)`
- `sprintf(fmt, ...args)` — Like libc `sprintf()`
- `in`, `out`, `err` — Wrappers to `stdin`, `stdout`, `stderr`
- `SEEK_SET`, `SEEK_CUR`, `SEEK_END` — Constants for seek

### HTTP

- `urlGet(url, options?)` — Download URL using `curl`. Options: `binary` (returns ArrayBuffer), `full` (returns `{response, responseHeaders, status}`)

### Utilities

- `gc()` — Manually invoke cycle removal algorithm
- `strerror(errno)` — Error code to string
- `Error` — Enumeration of common error codes (`EINVAL`, `EIO`, `EACCES`, `EEXIST`, `ENOSPC`, `ENOSYS`, `EBUSY`, `ENOENT`, `EPERM`, `EPIPE`)
- `parseExtJSON(str)` — Parse JSON5-like superset: comments, unquoted properties, trailing commas, single quotes, hex/octal/binary integers, `NaN`/`Infinity`

### FILE Prototype Methods

```javascript
const f = std.open("test.txt", "r");
if (f) {
    const line = f.getline();           // Read next line (UTF-8)
    const content = f.readAsString();   // Read entire file as string
    const bytes = f.read(buffer, pos, len);  // Binary read
    f.puts("hello");                    // Write string
    f.printf("%d items", 42);           // Formatted write
    f.seek(0, std.SEEK_SET);            // Seek
    const pos = f.tell();               // Current position
    const posBig = f.tello();           // Position as bigint
    f.flush();                          // Flush buffer
    f.close();                          // Close file
}
```

Additional FILE methods: `eof()`, `fileno()`, `error()`, `clearerr()`, `write(buffer, pos, len)`, `getByte()`, `putByte(c)`.

## os Module

The `os` module provides operating system specific functions: low-level file access, signals, timers, asynchronous I/O, and workers (threads).

### File Operations

```javascript
import * as os from "os";

const fd = os.open("file.txt", os.O_RDONLY);
const buf = new ArrayBuffer(1024);
const n = os.read(fd, buf, 0, 1024);
os.close(fd);

// Directory operations
const [entries, err] = os.readdir("/path");
const [stat, err2] = os.stat("/path/file");
os.mkdir("/new/dir", 0o755);
os.remove("/path/file");
os.rename("old.txt", "new.txt");
const [realPath, err3] = os.realpath("./file");
const [cwd, err4] = os.getcwd();
os.chdir("/some/dir");

// Symlinks
os.symlink("target", "linkpath");
const [linkTarget, err5] = os.readlink("linkpath");
```

POSIX open flags: `O_RDONLY`, `O_WRONLY`, `O_RDWR`, `O_APPEND`, `O_CREAT`, `O_EXCL`, `O_TRUNC`. Windows-specific: `O_TEXT` (text mode).

### stat Mode Constants

`S_IFMT`, `S_IFIFO`, `S_IFCHR`, `S_IFDIR`, `S_IFBLK`, `S_IFREG`, `S_IFSOCK`, `S_IFLNK`, `S_ISGID`, `S_ISUID` — Same values as `<sys/stat.h>`.

### TTY Operations

- `isatty(fd)` — Check if fd is a terminal
- `ttyGetWinSize(fd)` — Return `[width, height]` or `null`
- `ttySetRaw(fd)` — Set TTY to raw mode

### Signals

```javascript
os.signal(os.SIGINT, () => {
    print("Caught SIGINT");
});
os.kill(pid, os.SIGTERM);
```

Signal constants: `SIGINT`, `SIGABRT`, `SIGFPE`, `SIGILL`, `SIGSEGV`, `SIGTERM`.

Signal handlers can only be defined in the main thread. Use `null` to restore default handler, `undefined` to ignore.

### Process Execution

```javascript
const exitCode = os.exec(["ls", "-la"], {
    block: true,       // Wait for completion (default)
    usePath: true,     // Search in PATH
    file: "ls",        // Override executable
    cwd: "/tmp",       // Working directory
    stdin: fd,         // Redirect stdin
    stdout: fd2,       // Redirect stdout
    stderr: fd3,       // Redirect stderr
    env: { PATH: "/usr/bin" },  // Environment
    uid: 1000,         // Set UID
    gid: 1000,         // Set GID
});
```

When `block` is false, returns the child process PID.

### Unix System Calls

- `waitpid(pid, options)` — Return `[ret, status]`
- `WNOHANG` — Non-blocking waitpid flag
- `dup(fd)` — Duplicate file descriptor
- `dup2(oldfd, newfd)` — Duplicate to specific fd
- `pipe()` — Create pipe, returns `[read_fd, write_fd]` or `null`

### Timers

```javascript
os.sleep(1000);                    // Block for 1000ms
await os.sleepAsync(500);          // Async sleep (returns promise)

const handle = os.setTimeout(() => {
    print("timeout!");
}, 1000);
os.clearTimeout(handle);           // Cancel timer

const timestamp = os.now();        // High-precision timestamp (ms)
```

### Platform Detection

`os.platform` — Returns `"linux"`, `"darwin"`, `"win32"`, or `"js"`.

### Workers (Threads)

```javascript
// Main script
import * as os from "os";
const worker = new os.Worker("worker.mjs");
worker.onmessage = (e) => {
    print("Received:", e.data);
};
worker.postMessage({ task: "compute" });

// worker.mjs
import { Worker } from "os";
Worker.parent.onmessage = (e) => {
    const result = doWork(e.data.task);
    Worker.parent.postMessage(result);
};
```

Workers use an API close to Web Workers. Messages are cloned using structured clone algorithm. `SharedArrayBuffer` is shared between workers. Current limitations: `Map` and `Set` are not supported in messages. Nested workers are not supported.

### Asynchronous I/O Handlers

```javascript
os.setReadHandler(fd, () => {
    // Called when data is available on fd
    const buf = new ArrayBuffer(4096);
    const n = os.read(fd, buf, 0, 4096);
});

os.setWriteHandler(fd, () => {
    // Called when fd can accept writes
});
```

Single handler per file handle. Use `func = null` to remove.
