# QuickJS Standard Library Reference

## Global Objects

### `scriptArgs`

Array of command-line arguments. First element is the script name.

```javascript
print(scriptArgs);  // ["qjs", "my_script.js", "arg1", "arg2"]
```

### `print(...args)`

Print arguments separated by spaces with trailing newline.

```javascript
print("Hello", "World");  // "Hello World\n"
```

### `console.log(...args)`

Same as `print()`.

## std Module

The `std` module wraps libc `stdlib.h` and `stdio.h` functions plus utilities.

### Process Control

| Function | Description |
|----------|-------------|
| `exit(n)` | Exit the process with code `n` |

### Script Evaluation

```javascript
// Evaluate a string as global script
std.evalScript("1 + 2");

// With options for async and backtrace control
std.evalScript(code, {
    async: true,           // Allow await, returns Promise
    backtrace_barrier: true // Exclude from error backtraces
});
```

### File Operations

```javascript
// Load a file as UTF-8 string
const content = std.loadFile("data.txt");

// Open a FILE object (wrapper to fopen)
const f = std.open("file.txt", "r");   // Returns FILE or null
if (f) {
    const line = f.getLine();          // Read next line (no newline)
    const byte = f.getByte();          // Read single byte (-1 on EOF)
    f.putByte(65);                     // Write a byte
    f.puts("text\n");                  // Write string with newline
    f.printf("Value: %d\n", 42);       // Formatted output
    f.flush();                         // Flush buffer
    f.seek(0, std.SEEK_SET);           // Seek to position
    const pos = f.tell();              // Current position (number)
    const bigpos = f.tello();          // Current position (bigint)
    f.close();                         // Close file
}

// Open a process pipe (wrapper to popen)
const p = std.popen("ls -la", "r");
if (p) {
    const output = p.readAsString();
    p.close();
}

// Temporary file
const tmp = std.tmpfile();
```

### FILE Object Methods

| Method | Description |
|--------|-------------|
| `close()` | Close file. Returns 0 or `-errno` |
| `puts(str)` | Output string with UTF-8 encoding |
| `printf(fmt, ...args)` | Formatted printf (C format specifiers) |
| `flush()` | Flush buffered output |
| `seek(offset, whence)` | Seek (`std.SEEK_SET`, `SEEK_CUR`, `SEEK_END`) |
| `tell()` | Current position as number |
| `tello()` | Current position as bigint |
| `eof()` | Return true if end of file |
| `fileno()` | OS file descriptor |
| `error()` | True if error occurred |
| `clearerr()` | Clear error indication |
| `read(buffer, position, length)` | Read bytes to ArrayBuffer |
| `write(buffer, position, length)` | Write bytes from ArrayBuffer |
| `getline()` | Next line without trailing newline |
| `readAsString(max_size?)` | Read up to max_size bytes as string |
| `getByte()` | Next byte (-1 on EOF) |
| `putByte(c)` | Write one byte |

### I/O Streams

```javascript
std.in   // stdin (FILE)
std.out  // stdout (FILE)
std.err  // stderr (FILE)
```

### String Formatting

```javascript
std.puts("text");                     // Equivalent to std.out.puts()
std.printf("%d %s\n", 42, "hello");   // Equivalent to std.out.printf()
const s = std.sprintf("Value: %f", 3.14);
```

### Error Codes

```javascript
std.EINVAL    // Invalid argument
std.EIO       // I/O error
std.EACCES    // Permission denied
std.EEXIST    // File exists
std.ENOSPC    // No space left
std.ENOSYS    // Function not implemented
std.EBUSY     // Resource busy
std.ENOENT    // No such file or directory
std.EPERM     // Operation not permitted
std.EPIPE     // Broken pipe

// Get error description string
std.strerror(std.EACCES);  // "Permission denied"
```

### Memory Management

```javascript
// Manually trigger cycle removal (normally automatic)
std.gc();
```

### Environment Variables

```javascript
const val = std.getenv("HOME");
std.setenv("MY_VAR", "value");
std.unsetenv("MY_VAR");
const all = std.getenviron();  // { HOME: "/home/user", ... }
```

### URL Fetching

```javascript
// Simple GET request (uses curl internally)
const text = std.urlGet("https://example.com/data.json");

// With options
const result = std.urlGet("https://api.example.com/data", {
    binary: true,              // Return ArrayBuffer instead of string
    full: true                 // Return { response, responseHeaders, status }
});
if (result.status === 200) {
    console.log(result.response);
}

// Binary data
const img = std.urlGet("https://example.com/image.png", { binary: true });
```

### Extended JSON Parsing (JSON5-like)

```javascript
// Accepts: comments, unquoted keys, trailing commas, single quotes,
// hex/octal/binary numbers, NaN/Infinity, leading plus signs
const data = std.parseExtJSON(`{
  // comment
  name: 'QuickJS',       // unquoted key, single-quoted string
  value: 0x1F,           // hexadecimal
  trailing: [1, 2,],     // trailing comma
}`);
```

## os Module

The `os` module provides operating system specific functions. Returns 0 on success or negative error code on failure.

### Low-Level File I/O

```javascript
const fd = os.open("file.bin", os.O_RDWR | os.O_CREAT, 0o644);
os.seek(fd, 0, std.SEEK_SET);
const buf = new Uint8Array(1024);
const nread = os.read(fd, buf, 0, 1024);
os.write(fd, buf, 0, nread);
os.close(fd);

// Open flags: O_RDONLY, O_WRONLY, O_RDWR, O_APPEND, O_CREAT, O_EXCL, O_TRUNC
// Windows only: O_TEXT (text mode vs default binary)
```

### TTY Operations

```javascript
if (os.isatty(0)) { print("stdin is a terminal"); }

const [w, h] = os.ttyGetWinSize(0);  // [width, height] or null
os.ttySetRaw(0);                      // Raw terminal mode
```

### File/Directory Operations

```javascript
os.remove("file.txt");                        // Remove file
os.rename("old.txt", "new.txt");              // Rename
const [path, err] = os.realpath("dir/../f");  // Canonical path
const [cwd, err] = os.getcwd();               // Current directory
os.chdir("/tmp");                             // Change directory
os.mkdir("/tmp/newdir", 0o755);               // Create directory
const [files, err] = os.readdir("/path");     // List directory entries

// stat/lstat return [obj, errno]
const [info, err] = os.stat("file.txt");
if (!err) {
    print(info.dev, info.ino, info.mode, info.nlink,
          info.uid, info.gid, info.rdev, info.size,
          info.blocks, info.atime, info.mtime, info.ctime);
}

// Symbolic links
os.symlink("target", "link");
const [target, err] = os.readlink("link");

// Time manipulation (milliseconds since 1970)
os.utimes("file.txt", Date.now(), Date.now());

// File type constants: S_IFIFO, S_IFCHR, S_IFDIR, S_IFBLK, S_IFREG, S_IFSOCK, S_IFLNK, S_ISGID, S_ISUID
```

### Process Management

```javascript
// Execute a command
const code = os.exec(["ls", "-la"], {
    block: true,       // Wait for completion (default)
    usePath: true,     // Search PATH (default)
    file: "ls",        // Override executable name
    cwd: "/tmp",       // Working directory
    stdin: fd,         // Redirect stdin
    stdout: fd,        // Redirect stdout
    stderr: fd,        // Redirect stderr
    env: { HOME: "/home" },  // Environment variables
    uid: 1000,         // Set user ID
    gid: 1000,         // Set group ID
});

const pid = os.exec(["sleep", "1"], { block: false });  // Non-blocking

os.getpid();                    // Current process ID

// Wait for child process
const [ret, status] = os.waitpid(pid, os.WNOHANG);
```

### Pipes and File Descriptors

```javascript
const [rd, wr] = os.pipe();     // Create pipe: [read_fd, write_fd] or null
os.dup(0);                      // Duplicate fd
os.dup2(oldfd, newfd);          // Duplicate to specific fd
```

### Signals

```javascript
// Set signal handler (main thread only)
os.signal(os.SIGINT, () => print("interrupted"));
os.signal(os.SIGTERM, null);    // Default handler
os.signal(os.SIGSEGV, undefined);  // Ignore

// Signal constants: SIGINT, SIGABRT, SIGFPE, SIGILL, SIGSEGV, SIGTERM

// Send signal to process
os.kill(pid, os.SIGTERM);
```

### Timers and Sleep

```javascript
// Async sleep (returns Promise)
await os.sleepAsync(500);

// Blocking sleep
os.sleep(1000);

// Timer functions
const handle = os.setTimeout(() => print("done"), 1000);
os.clearTimeout(handle);
```

### I/O Event Handlers

```javascript
// Asynchronous read/write handlers
os.setReadHandler(fd, (fd) => {
    // Called when data is available on fd
});

os.setWriteHandler(fd, (fd) => {
    // Called when fd is ready for writing
});

// Remove handler
os.setReadHandler(fd, null);
```

### Timestamps and Platform

```javascript
const precise = os.now();           // High-precision timestamp (ms)
const platform = os.platform;       // "linux", "darwin", "win32", or "js"
```

### Workers

```javascript
// Create a worker thread
const worker = new os.Worker("worker_module.js");

// Send message (structured clone)
worker.postMessage({ data: "hello" });

// Receive messages
worker.onmessage = (event) => {
    print(event.data);  // Received message
};

// In the worker, access parent
os.Worker.parent.postMessage({ result: 42 });

// Limitations:
// - No nested workers
// - Map and Set not supported in postMessage yet
// - SharedArrayBuffer is shared between workers
```
