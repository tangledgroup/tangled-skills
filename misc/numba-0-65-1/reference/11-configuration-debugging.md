# Configuration and Debugging

## Environment Variables

Numba behavior is controlled through environment variables (integer values, default 0 unless noted). Configuration can also be persisted in `.numba_config.yaml` in the working directory (requires `pyyaml`). Environment variables override config file settings.

Config file format:
```yaml
developer_mode: 1
dump_cfg: 1
color_scheme: dark_bg
```

## JIT Flags

- **NUMBA_BOUNDSCHECK** — Globally enable (1) or disable (0) bounds checking
- **NUMBA_DISABLE_PERFORMANCE_WARNINGS** — Disable performance warnings (set to 1)

## Debugging Variables

- **NUMBA_DEVELOPER_MODE** — Full tracebacks, disables help instructions (default: 0)
- **NUMBA_FULL_TRACEBACKS** — Enable full tracebacks on exceptions (defaults to NUMBA_DEVELOPER_MODE value)
- **NUMBA_SHOW_HELP** — Show resources for getting help (default: 0)
- **NUMBA_DISABLE_ERROR_MESSAGE_HIGHLIGHTING** — Disable error message highlighting (useful for CI)
- **NUMBA_COLOR_SCHEME** — Color scheme for error reporting: `no_color`, `dark_bg`, `light_bg`, `blue_bg`, `jupyter_nb` (requires `colorama`)
- **NUMBA_HIGHLIGHT_DUMPS** — Syntax highlighting on IR dumps if `pygments` installed (default: 0)

### Compiler Debug Output

- **NUMBA_DEBUG** — Print all debugging information during compilation
- **NUMBA_DEBUG_FRONTEND** — Debug info up to Numba IR generation
- **NUMBA_DEBUG_TYPEINFER** — Debug info about type inference
- **NUMBA_DISABLE_TYPEINFER_FAIL_CACHE** — Disable cache of failed function resolutions (debugging only)
- **NUMBA_DUMP_CFG** — Dump control flow graphs
- **NUMBA_DUMP_llvm** — Dump LLVM IR
- **NUMBA_DUMP_ASSEMBLY** — Dump generated assembly

### Runtime Debug

- **NUMBA_DEBUGINFO** — Enable debug info for full application (increases memory usage significantly)
- **NUMBA_EXTEND_VARIABLE_LIFETIMES** — Extend variable lifetimes to end of block (useful with NUMBA_DEBUGINFO)
- **NUMBA_DEBUG_NRT** — Debug Numba runtime reference counting; fills allocated memory with marker patterns (`0xCB` on alloc, `0xDE` on dealloc)
- **NUMBA_NRT_STATS** — Enable Numba runtime statistics counters

### Profiling

- **NUMBA_ENABLE_PROFILING** — Enable JIT events of LLVM for profiling jitted functions
- **NUMBA_TRACE** — Trace function entry/exit events with arguments and return values
- **NUMBA_ENABLE_SYS_MONITORING** — Support Python's `sys.monitoring` (Python 3.12+, disabled by default). **Disabled on Python 3.14.4+**: CPython internal changes broke the JIT `sys.monitoring` integration ([#10538](https://github.com/numba/numba/issues/10538)). On 3.14.4+, this variable has no effect and emits a `UserWarning` if set to a non-zero value.

### GDB Integration

- **NUMBA_GDB_BINARY** — Path to GDB binary for Numba's GDB support (default: `gdb`)

Use `debug=True` in the decorator for per-function debug info:

```python
@njit(debug=True)
def my_function(x):
    return x * 2
```

Combined with `NUMBA_DEBUGINFO=1`, enables variable inspection in GDB.

## Command Line Interface

Numba provides a CLI tool:

```bash
numba --help           # Show help
numba env              # System information
numba dump-bytecode    # Dump bytecode of a function
numba debug            # Debugging utilities
```

## Disabling JIT Compilation

For testing, disable all JIT compilation:

```python
import numba
numba.config.DISABLE_JIT = 1
```

Or via environment variable: `NUMBA_DISABLE_JIT=1`.
