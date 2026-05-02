# VM Embedding

## Contents
- Running the VM
- Libraries
- Exports
- Loaders
- Custom Loaders
- Embedding in C
- Multithreading

## Running the VM

The `neko` binary executes `.n` bytecode files:

```bash
neko program        # extension optional for .n files
neko -version       # check version
```

Bytecode files are searched in the current directory and paths listed in the `NEKOPATH` environment variable (colon-separated on Unix, semicolon on Windows). Each `.n` file is a **module**.

## Libraries

`.ndll` files are shared libraries (`.so`/`.dll`) linked against `libneko`. They expose C primitives callable from Neko. Libraries are searched the same way as modules — current directory + `NEKOPATH`.

A single `.ndll` can contain multiple primitives, each identified by name.

## Exports

Each module has a global `$exports` object. Set fields on it to make values available to other modules:

```neko
$exports.add = function(a, b) { return a + b; };
$exports.PI = 3.14159;
```

When another module loads this one via `loadmodule`, it receives the `$exports` table as the return value.

## Loaders

The `$loader` builtin provides module and primitive loading:

**Load a module:**
```neko
var m = $loader.loadmodule("mathlib", $loader);
// Returns mathlib's $exports object, or throws if not found
m.add(3, 4);
```

First argument is the module name (searched via NEKOPATH). Second argument is the loader to pass to the loaded module.

**Load a C primitive:**
```neko
var p = $loader.loadprim("std@test", 0);
// Format: "library_name@function_name"
// Last arg: number of arguments (-1 for variable arity)
p();
```

Returns a Neko function wrapping the C primitive, or throws on failure.

## Custom Loaders

Implement custom loaders by creating an object with `loadmodule` and `loadprim` methods. Use it as the second parameter to `loadmodule`:

```neko
var secure_loader = $new(null);
secure_loader.loadmodule = function(name, child_loader) {
    // Filter: only allow whitelisted modules
    if( name == "safe_lib" )
        return $loader.loadmodule(name, child_loader);
    $throw("Module " + name + " not allowed");
};
secure_loader.loadprim = function(name, nargs) {
    // Block all C primitives for sandboxing
    $throw("C primitives not allowed in sandbox");
};

var m = $loader.loadmodule("entry_point", secure_loader);
```

This enables security sandboxes, module filtering, and resource access control.

## Embedding in C

Embed NekoVM in a C application using `libneko.so` (Unix) or `neko.dll` (Windows), plus the Boehm GC library (`libgc`/`gc.dll`). Include `neko_vm.h` for VM API and `neko_mod.h` for low-level module access.

**Minimal embedding example:**

```c
#include <stdio.h>
#include <neko_vm.h>

value load_module( char *file ) {
    value loader = neko_default_loader(NULL, 0);
    value args[2];
    value exc = NULL;
    args[0] = alloc_string(file);
    args[1] = loader;
    value ret = val_callEx(loader,
        val_field(loader, val_id("loadmodule")),
        args, 2, &exc);
    if( exc != NULL ) {
        buffer b = alloc_buffer(NULL);
        val_buffer(b, exc);
        printf("Error: %s\n", val_string(buffer_to_string(b)));
        return NULL;
    }
    return ret;
}

int main( int argc, char *argv[] ) {
    neko_global_init(NULL);              // Initialize global state
    neko_vm *vm = neko_vm_alloc(NULL);   // Allocate VM instance
    neko_vm_select(vm);                  // Select for current thread

    value module = load_module("mymodule.n");
    if( module != NULL ) {
        value x = val_field(module, val_id("x"));
        printf("x = %d\n", val_int(x));
    }

    neko_global_free();  // Cleanup global state
    return 0;
}
```

The Neko program `mymodule.neko` would export values via `$exports`:

```neko
$exports.x = 33;
$exports.f = function(x) { return x * 2 + 1; };
```

## Multithreading

Neko supports multiple VM instances and multithreading with these rules:

- Allocate a VM per thread: `neko_vm *vm = neko_vm_alloc(NULL)`
- A thread can allocate several VMs
- Select the active VM: `neko_vm_select(vm)`
- Get current VM: `neko_vm_current()`
- **One VM must not execute on multiple threads simultaneously**
- Neko modules (`.n` files) can be shared across VMs/threads safely

**Thread safety constraints:** Non-basic data structures (loaders, hashtables, abstracts like file handles and regexps) are not thread-safe. Keep them in the thread that originally allocated them. Sharing across threads risks crashes.
