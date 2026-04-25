# CFFI Thread Safety - Complete Guide

## Overview

CFFI 2.0.0 provides comprehensive thread safety support, including automatic GIL release when calling C code and full compatibility with Python's free-threaded build (3.14+). Understanding thread safety is crucial for building reliable multithreaded applications.

## GIL Handling in CFFI

### Automatic GIL Release (GIL-Enabled Python)

In standard Python builds with the GIL, CFFI automatically releases the GIL before calling into C libraries:

```python
from cffi import FFI
import threading

ffi = FFI()
ffi.cdef("int compute_heavy(int iterations);")

lib = ffi.dlopen("mylib.so")

# Multiple threads can call C code in parallel
results = []
locks = threading.Lock()

def worker(thread_id):
    # GIL is released during lib.compute_heavy()
    result = lib.compute_heavy(1000000)
    
    # GIL is reacquired to store result
    with locks:
        results.append((thread_id, result))

threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(f"Results from {len(results)} threads")
```

**Key Points:**
- GIL released automatically before C function calls
- GIL reacquired when returning to Python
- Multiple threads can execute C code in parallel
- Python objects accessed after C call are thread-safe (GIL held)

### Free-Threaded Python 3.14+ Support

CFFI 2.0.0 fully supports Python's free-threaded build:

```python
import sys

# Check if running in free-threaded mode
if hasattr(sys, 'total_threads'):
    print("Running in free-threaded mode")

from cffi import FFI
ffi = FFI()
ffi.cdef("int add(int x, int y);")

lib = ffi.dlopen("mylib.so")

# In free-threaded Python:
# - CFFI still manages thread safety
# - Python callbacks acquire GIL automatically
# - No changes needed to your code
result = lib.add(5, 3)
```

**Compatibility:**
- CFFI 2.0.0+ required for free-threaded Python 3.14+
- Free-threaded Python 3.13 is NOT supported (use 3.14+)
- Same code works on both GIL-enabled and free-threaded builds

## Thread Safety Patterns

### Protecting Non-Thread-Safe C Libraries

Many C libraries are not thread-safe. Use Python locks to serialize access:

```python
from cffi import FFI
import threading

ffi = FFI()
ffi.cdef("""
    int get_counter(void);
    void increment_counter(void);
    void reset_counter(void);
""")

lib = ffi.dlopen("mylib.so")

# C library uses global state, not thread-safe
counter_lock = threading.Lock()

def safe_increment():
    with counter_lock:
        lib.increment_counter()

def safe_get():
    with counter_lock:
        return lib.get_counter()

# Now multiple threads can safely use the library
threads = []
for i in range(10):
    t = threading.Thread(target=lambda: [safe_increment() for _ in range(100)])
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print(f"Final counter value: {safe_get()}")  # Should be 1000
```

### Per-Object Locking

For libraries that are thread-safe except for per-object operations:

```python
from cffi import FFI
import threading

ffi = FFI()
ffi.cdef("""
    typedef struct handle Handle;
    Handle* create_handle(void);
    void free_handle(Handle* h);
    int read_value(Handle* h);
    void write_value(Handle* h, int val);
""")

lib = ffi.dlopen("mylib.so")

class ThreadSafeHandle:
    def __init__(self):
        self._handle = lib.create_handle()
        self._lock = threading.Lock()
    
    def __del__(self):
        if hasattr(self, '_handle'):
            lib.free_handle(self._handle)
    
    def read(self):
        with self._lock:
            return lib.read_value(self._handle)
    
    def write(self, value):
        with self._lock:
            lib.write_value(self._handle, value)

# Each handle has its own lock
handles = [ThreadSafeHandle() for _ in range(10)]

def worker(h, value):
    h.write(value)
    result = h.read()
    assert result == value

threads = []
for i, h in enumerate(handles):
    t = threading.Thread(target=worker, args=(h, i))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

### Read-Write Locks for Read-Heavy Workloads

```python
from cffi import FFI
import threading

# Use asyncio locks or third-party rwlock
try:
    from aio_rwlock import RWLock
except ImportError:
    # Fallback to simple lock
    RWLock = None

ffi = FFI()
ffi.cdef("""
    const char* get_config(const char* key);
    void set_config(const char* key, const char* value);
""")

lib = ffi.dlopen("mylib.so")

class ThreadSafeConfig:
    def __init__(self):
        self._lock = threading.RLock()  # Reentrant lock
    
    def get(self, key):
        with self._lock:
            c_key = ffi.new("char[]", key.encode('utf-8'))
            c_value = lib.get_config(c_key)
            if c_value:
                return ffi.string(c_value).decode('utf-8')
            return None
    
    def set(self, key, value):
        with self._lock:
            c_key = ffi.new("char[]", key.encode('utf-8'))
            c_value = ffi.new("char[]", value.encode('utf-8'))
            lib.set_config(c_key, c_value)

config = ThreadSafeConfig()

# Multiple readers or single writer
def reader(key):
    value = config.get(key)
    print(f"Read {key}: {value}")

def writer(key, value):
    config.set(key, value)
    print(f"Wrote {key}: {value}")
```

## Callbacks and Thread Safety

### Callbacks from C Threads

When C code calls back into Python from different threads:

```python
from cffi import FFI
import threading

ffi = FFI()
ffi.cdef("""
    typedef void (*callback_fn)(int value);
    void start_async_operation(callback_fn cb);
""")

lib = ffi.dlopen("mylib.so")

# Thread-safe results collection
results = []
results_lock = threading.Lock()

@ffi.callback("callback_fn")
def async_callback(value):
    # CFFI automatically acquires GIL before calling Python
    # But shared data still needs protection
    
    with results_lock:
        results.append(value)
    
    print(f"Callback received: {value} (thread: {threading.current_thread().name})")

# Start multiple async operations
for i in range(5):
    lib.start_async_operation(async_callback)

# Wait for callbacks (in real code, use proper synchronization)
import time
time.sleep(2)

print(f"Received {len(results)} callbacks")
```

### Free-Threaded Callback Behavior

In free-threaded Python 3.14+:
- CFFI still acquires GIL before calling Python callbacks
- Your callback code runs with proper thread safety
- No code changes needed for free-threaded compatibility

## Testing Thread Safety

### Using ThreadPoolExecutor

```python
from cffi import FFI
from concurrent.futures import ThreadPoolExecutor, wait
import threading

ffi = FFI()
ffi.cdef("int unsafe_operation(int id);")

lib = ffi.dlopen("mylib.so")

# Test if C library is thread-safe
lock = threading.Lock()
errors = []

def worker(worker_id):
    try:
        for i in range(1000):
            result = lib.unsafe_operation(worker_id)
            if result < 0:
                with lock:
                    errors.append((worker_id, i, result))
    except Exception as e:
        with lock:
            errors.append((worker_id, i, str(e)))

# Run with many threads
with ThreadPoolExecutor(max_workers=16) as executor:
    futures = [executor.submit(worker, i) for i in range(16)]
    wait(futures)

if errors:
    print(f"Found {len(errors)} thread safety issues")
    for err in errors[:10]:
        print(f"  Error: {err}")
else:
    print("No thread safety issues detected")
```

### Using Thread Sanitizer

Build Python with Thread Sanitizer and test CFFI code:

```bash
# Build Python with TSan (simplified)
./configure --with-pydebug --with-address-sanitizer --with-thread-sanitizer
make

# Run tests
TSAN_OPTIONS=second_deadlock_stack=1 python3 test_thread_safety.py
```

Example output when race detected:
```
WARNING: ThreadSanitizer: data race (pid=12345)
  Read of size 4 at 0x7fff52040a8c by thread T2:
    #0 lib.unsafe_operation()

  Previous write of size 4 at 0x7fff52040a8c by thread T1:
    #0 lib.unsafe_operation()
```

### Stress Testing Pattern

```python
from cffi import FFI
from concurrent.futures import ThreadPoolExecutor
import sys

ffi = FFI()
ffi.cdef("""
    void* create_object(void);
    void modify_object(void* obj, int value);
    int read_object(void* obj);
    void free_object(void* obj);
""")

lib = ffi.dlopen("mylib.so")

def stress_test(num_threads, operations_per_thread):
    objects = []
    lock = threading.Lock()
    
    def create_phase():
        obj = lib.create_object()
        with lock:
            objects.append(obj)
    
    def modify_phase():
        with lock:
            if not objects:
                return
            obj = objects[0]
        
        for i in range(operations_per_thread):
            lib.modify_object(obj, i)
            value = lib.read_object(obj)
            
            # Check for corruption
            if value < -10000 or value > 10000:
                print(f"Possible corruption: {value}")
    
    def cleanup_phase():
        with lock:
            to_clean = objects.copy()
            objects.clear()
        
        for obj in to_clean:
            lib.free_object(obj)
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Create phase
        futures = [executor.submit(create_phase) for _ in range(num_threads // 2)]
        wait(futures)
        
        # Modify phase (race condition territory)
        futures = [executor.submit(modify_phase) for _ in range(num_threads)]
        wait(futures)
        
        # Cleanup phase
        futures = [executor.submit(cleanup_phase) for _ in range(num_threads // 2)]
        wait(futures)
    
    print(f"Stress test completed: {num_threads} threads, {operations_per_thread} ops each")

# Run stress test
stress_test(16, 1000)
```

## Free-Threading Migration Guide

### Checking Python Build Type

```python
import sysconfig

free_threaded = bool(sysconfig.get_config_var('Py_GIL_DISABLED'))

if free_threaded:
    print("Running in free-threaded mode")
    # CFFI 2.0.0+ required
else:
    print("Running in GIL-enabled mode")
```

### Code Compatibility Checklist

Most CFFI code works unchanged in free-threaded Python. Verify:

1. **C library thread safety**: Does the C library need additional locking?
2. **Callback handling**: Callbacks work the same (GIL acquired automatically)
3. **Shared state protection**: Python-level locks still needed for shared data
4. **Extension compatibility**: Other extensions used with CFFI must support free-threading

### Performance Considerations

```python
import time
from concurrent.futures import ThreadPoolExecutor
from cffi import FFI

ffi = FFI()
ffi.cdef("int compute(int n);")
lib = ffi.dlopen("mylib.so")

def benchmark(num_threads, iterations):
    def worker():
        total = 0
        for _ in range(iterations):
            total += lib.compute(1000)
        return total
    
    start = time.time()
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = list(executor.map(lambda _: worker(), range(num_threads)))
    
    elapsed = time.time() - start
    print(f"{num_threads} threads: {elapsed:.3f}s for {num_threads * iterations} calls")
    
    return elapsed

# Benchmark with different thread counts
for n in [1, 2, 4, 8, 16]:
    benchmark(n, 1000)
```

Expected behavior:
- **GIL-enabled Python**: C code runs in parallel, limited by CPU cores
- **Free-threaded Python**: Same parallelism, potentially better for CPU-bound work

## Troubleshooting Thread Issues

### Deadlock Detection

```python
import threading
import sys

class DeadlockDetector:
    def __init__(self):
        self.locks_held = {}
    
    def acquire(self, lock, thread_id):
        if thread_id in self.locks_held:
            print(f"WARNING: Thread {thread_id} already holds locks: {self.locks_held[thread_id]}")
        
        if thread_id not in self.locks_held:
            self.locks_held[thread_id] = []
        self.locks_held[thread_id].append(lock)
        
        return lock.acquire()
    
    def release(self, lock, thread_id):
        if thread_id in self.locks_held and lock in self.locks_held[thread_id]:
            self.locks_held[thread_id].remove(lock)
        lock.release()

# Use with caution - adds overhead
detector = DeadlockDetector()

class TrackedLock:
    def __init__(self):
        self._lock = threading.Lock()
    
    def __enter__(self):
        tid = threading.current_thread().ident
        detector.acquire(self._lock, tid)
        return self
    
    def __exit__(self, *args):
        tid = threading.current_thread().ident
        detector.release(self._lock, tid)
```

### Race Condition Debugging

```python
import threading
from cffi import FFI

ffi = FFI()
ffi.cdef("int shared_counter(void);")

lib = ffi.dlopen("mylib.so")

# Add logging to detect races
access_log = []
log_lock = threading.Lock()

def logged_access(thread_id):
    value = lib.shared_counter()
    
    with log_lock:
        access_log.append((thread_id, value))
    
    # Check for unexpected values
    if value < 0 or value > 1000000:
        print(f"SUSPICIOUS: Thread {thread_id} got value {value}")
    
    return value

threads = []
for i in range(10):
    t = threading.Thread(target=logged_access, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# Analyze access patterns
print(f"Total accesses: {len(access_log)}")
```

## Best Practices

1. **Assume C libraries are NOT thread-safe** unless documented otherwise
2. **Use Python locks** to serialize access to non-thread-safe C code
3. **Prefer per-object locking** over global locks when possible
4. **Test with Thread Sanitizer** during development
5. **Document thread safety guarantees** clearly for your wrapper
6. **Keep critical sections small** to maximize parallelism
7. **Use context managers** for lock management
8. **Test with high thread counts** to expose race conditions
9. **Consider free-threaded Python** for future compatibility
10. **Profile before optimizing** - locking overhead can be significant

## References

- [CFFI Documentation - Thread Safety](https://cffi.readthedocs.io/en/stable/overview.html#thread-safety)
- [Python Free-Threading Guide](https://py-free-threading.github.io/)
- [Python Threading Documentation](https://docs.python.org/3/library/threading.html)
- [Thread Sanitizer Documentation](https://clang.llvm.org/docs/ThreadSanitizer.html)
