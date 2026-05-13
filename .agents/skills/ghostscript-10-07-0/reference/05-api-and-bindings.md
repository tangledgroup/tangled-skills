# API and Language Bindings

## Contents
- gsapi C API Lifecycle
- Core Functions
- Parameter Management
- Standard I/O Redirection
- Path Control (SAFER mode)
- Custom Filing Systems
- Language Bindings Overview
  - Python
  - C#
  - Java

## gsapi C API Lifecycle

The Ghostscript interpreter API (`gsapi`) is declared in `iapi.h`. The standard lifecycle:

```
gsapi_revision()        → Verify library version
gsapi_new_instance()    → Create interpreter instance
gsapi_set_stdio()       → (optional) Redirect stdio
gsapi_init_with_args()  → Initialize with command-line-style arguments
gsapi_run_string()      → Execute PostScript code
gsapi_run_file()        → Process input file
gsapi_exit()            → Shutdown interpreter
gsapi_delete_instance() → Free instance
```

Only one Ghostscript instance is supported per process on most platforms.

### Example: Basic Conversion

```c
#include "iapi.h"
#include <stdio.h>

int main(int argc, char *argv[]) {
    void *instance;
    gsapi_revision_t r;

    /* Verify library version */
    if (gsapi_revision(&r, sizeof(r)) != 0) {
        fprintf(stderr, "revision structure size mismatch\n");
        return 1;
    }
    if (r.revision < 1000700) {
        fprintf(stderr, "Need Ghostscript >= 10.07.0\n");
        return 1;
    }

    /* Create instance */
    if (gsapi_new_instance(&instance, NULL) != 0) {
        fprintf(stderr, "Failed to create instance\n");
        return 1;
    }

    /* Build argument list (same as command-line switches) */
    char *args[] = {
        "-dSAFER", "-dBATCH", "-dNOPAUSE",
        "-sDEVICE=png16m", "-r300",
        "-sOutputFile=output.png",
        "input.pdf"
    };
    int arg_count = sizeof(args) / sizeof(args[0]);

    /* Initialize */
    int code = gsapi_init_with_args(instance, arg_count, args);
    if (code < 0) {
        fprintf(stderr, "Init failed with code %d\n", code);
    }

    /* Exit and cleanup */
    gsapi_exit(instance);
    gsapi_delete_instance(instance);
    return (code < 0) ? 1 : 0;
}
```

## Core Functions

### `gsapi_revision()`

Returns library version information. Call before any other API function.

```c
typedef struct {
    const char *product;
    const char *copyright;
    long revision;        /* e.g. 1000700 for 10.07.0 */
    long revisiondate;
} gsapi_revision_t;

int gsapi_revision(gsapi_revision_t *pr, int len);
```

### `gsapi_new_instance()` / `gsapi_delete_instance()`

Create and destroy interpreter instances. Initialize the opaque pointer to NULL before calling `new_instance`.

```c
int gsapi_new_instance(void **pinstance, void *caller_handle);
void gsapi_delete_instance(void *instance);
```

### `gsapi_init_with_args()`

Initialize with command-line-style arguments. Arguments are the same as `argv[1]` through `argv[n]` (first element is ignored).

```c
int gsapi_init_with_args(void *instance, int argc, char **argv);
```

### `gsapi_run_*()`

Execute PostScript code or process files:

```c
/* Execute a PostScript string */
int gsapi_run_string(void *instance, const char *str,
                     int user_errors, int *pexit_code);

/* Execute with explicit length (avoids null-termination issues) */
int gsapi_run_string_with_length(void *instance, const char *str,
                                 unsigned int length,
                                 int user_errors, int *pexit_code);

/* Process a file */
int gsapi_run_file(void *instance, const char *file_name,
                   int user_errors, int *pexit_code);

/* Streaming: begin → continue → end */
int gsapi_run_string_begin(void *instance, int user_errors, int *pexit_code);
int gsapi_run_string_continue(void *instance, const char *str,
                              unsigned int length,
                              int user_errors, int *pexit_code);
int gsapi_run_string_end(void *instance, int user_errors, int *pexit_code);
```

The 64 KB limit applies to any single `run_string` buffer. Split larger inputs using `begin`/`continue`/`end`.

Return codes ≤ -100 indicate quit or fatal error — call `gsapi_exit()` next. The `user_errors` parameter:
- `0` (default): Errors handled by interpreted code
- Negative: Return error code directly to caller, bypassing language error handler
- Positive: Treated same as 0

### `gsapi_exit()`

Must be called before `gsapi_delete_instance()` if `init_with_args` was called.

```c
int gsapi_exit(void *instance);
```

## Parameter Management

### `gsapi_set_param()` / `gsapi_get_param()`

Set and query parameters equivalent to `-d`, `-s`, or `-p` command-line switches:

```c
typedef enum {
    gs_spt_invalid = -1,
    gs_spt_null    = 0,
    gs_spt_bool    = 1,   /* int: 0=false, non-zero=true */
    gs_spt_int     = 2,
    gs_spt_float   = 3,
    gs_spt_name    = 4,   /* char * */
    gs_spt_string  = 5,   /* char * */
    gs_spt_long    = 6,
    gs_spt_i64     = 7,
    gs_spt_size_t  = 8,
    gs_spt_parsed  = 9,   /* PostScript code to parse */
    gs_spt_more_to_come = 1<<31  /* Queue without sending to device */
} gs_set_param_type;

int gsapi_set_param(void *instance, const char *param,
                    const void *value, gs_set_param_type type);
int gsapi_get_param(void *instance, const char *param,
                    void *value, gs_set_param_type type);
```

**Batch parameter setting with `gs_spt_more_to_come`:**

OR the type with `gs_spt_more_to_come` to queue parameters without sending to device. This avoids multiple device reinitializations:

```c
gsapi_set_param(instance, "HWResolution", "[300 300]",
                gs_spt_parsed | gs_spt_more_to_come);
int first = 1;
gsapi_set_param(instance, "FirstPage", &first,
                gs_spt_int | gs_spt_more_to_come);
int factor = 3;
gsapi_set_param(instance, "DownScaleFactor", &factor, gs_spt_int);
/* Last call without more_to_come sends all queued params */
```

### `gsapi_enumerate_params()`

List current device parameters:

```c
void *iter = NULL;
const char *key;
gs_set_param_type type;

while (gsapi_enumerate_params(instance, &iter, &key, &type) == 0) {
    printf("Parameter: %s (type %d)\n", key, type);
}
```

## Standard I/O Redirection

### `gsapi_set_stdio()`

Redirect stdin/stdout/stderr callbacks:

```c
int stdin_callback(void *handle, char *buf, int len);
int stdout_callback(void *handle, const char *str, int len);
int stderr_callback(void *handle, const char *str, int len);

gsapi_set_stdio(instance, stdin_callback, stdout_callback, stderr_callback);
```

- stdin callback: return chars read, 0 for EOF, -1 for error
- stdout/stderr callbacks: return chars written

Note: These callbacks do not affect output device I/O when using `%stdout` as the output file. Device output still goes to process stdout file descriptor.

### `gsapi_set_poll()`

Set a polling callback for cooperative multitasking or user cancel checks. Called frequently during interpretation — must be fast:

```c
int poll_callback(void *handle) {
    /* Return 0 to continue, negative to abort */
    return check_user_cancel() ? -1 : 0;
}

gsapi_set_poll(instance, poll_callback);
```

## Path Control (SAFER mode)

When `-dSAFER` is used, file access is restricted. The API provides functions to manage permitted paths:

```c
/* Add a path to permitted list */
gsapi_add_control_path(instance, type, "/data/allowed");

/* Remove a path */
gsapi_remove_control_path(instance, type, "/data/allowed");

/* Clear all permitted paths */
gsapi_purge_control_paths(instance, type);

/* Enable/disable path checking */
gsapi_activate_path_control(instance, 1);

/* Query path control status */
int active = gsapi_is_path_control_active(instance);
```

The `type` parameter specifies which path list to modify (read, write, lib).

## Custom Filing Systems

Register custom filing systems to intercept file opens from the interpreter:

```c
typedef struct {
    int (*open_file)(const gs_memory_t *mem, void *secret,
                     const char *fname, const char *mode, ...);
    /* Additional function pointers for read, write, close, etc. */
} gsapi_fs_t;

gsapi_fs_t my_fs = { ... };
gsapi_add_fs(instance, &my_fs, &my_secret);

/* Later: */
gsapi_remove_fs(instance, &my_fs, &my_secret);
```

Filing systems are checked in reverse registration order (newest first). The default OS file system is always present as a fallback.

## Language Bindings Overview

Ghostscript provides language bindings for Python, C#, and Java that mirror the C API.

### Python

The `gsapi` Python module wraps the C API:

```python
import gs

# Create instance
gs_instance = gs.instance()

# Run with arguments (same as command line)
gs_instance.init([
    "-dSAFER", "-dBATCH", "-dNOPAUSE",
    "-sDEVICE=png16m", "-r300",
    "-sOutputFile=output.png",
    "input.pdf"
])

# Cleanup
gs_instance.exit()
```

Demo code is in the `demos` folder of the source distribution.

### C#

C# bindings provide two layers:

- **GhostAPI**: Direct mapping of `gsapi_*` functions via P/Invoke
- **GhostNET**: Higher-level .NET wrapper with helper methods, event-based progress reporting, and example viewers

```csharp
using Ghostscript;

using (var gs = new GSInstance(new string[] {
    "-dSAFER", "-dBATCH", "-dNOPAUSE",
    "-sDEVICE=png16m", "-r300",
    "-sOutputFile=output.png", "input.pdf"
}, null, null))
{
    // Processing happens during init
}
```

GhostNET provides delegates for progress callbacks, stdio callbacks, and page-rendered events.

### Java

Java bindings provide equivalent methods to the C API with additional helpers:

```java
import com.ghostgum.ghostscript.GSInstance;

String[] args = {
    "-dSAFER", "-dBATCH", "-dNOPAUSE",
    "-sDEVICE=png16m", "-r300",
    "-sOutputFile=output.png", "input.pdf"
};

try (GSInstance gs = new GSInstance(args, null, null)) {
    // Processing happens during init
}
```

## Display Device Callbacks

For applications that render to a display window, register callbacks:

```c
typedef struct {
    void *handle;
    int (*open)(void **device, void *handle);
    void (*close)(void *device);
    void (*presize)(void *device, int width, int height);
    void (*size)(void *device, int *px, int *py);
    void (*sync)(void *device);
    void (*page)(void *device, int copythis);
    void (*update)(void *device, int x, int y, int w, int h);
    /* Additional callbacks for memory, rectangles, etc. */
} display_callback;

gsapi_set_display_callback(instance, &callback);
```

Modern integrations should use `gsapi_register_callout()` instead of the deprecated `gsapi_set_display_callback()`.

## Return Codes

| Code Range | Meaning |
|------------|---------|
| `0` | Success |
| Positive | Informational (e.g., bytes needed for get_param) |
| `-1` to `-99` | Recoverable errors |
| `≤ -100` | Fatal error or quit — call `gsapi_exit()` next |

Common specific codes:
- `gs_error_undefined` (-21): Parameter not set or not recognized by device
- `gs_error_NeedInput`: More input needed (from `run_string_continue`)
