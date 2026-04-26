# C API Reference

## Runtime and Context Management

Create a runtime and context pair to begin executing JavaScript:

```c
#include "quickjs.h"

/* Create runtime */
JSRuntime *rt = JS_NewRuntime();

/* Optionally configure the runtime */
JS_SetMemoryLimit(rt, 64 * 1024 * 1024);    /* 64 MB limit */
JS_SetMaxStackSize(rt, 1024 * 1024);         /* 1 MB stack (default) */
JS_SetGCThreshold(rt, 32 * 1024 * 1024);     /* GC at 32 MB */

/* Create context — can have multiple per runtime */
JSContext *ctx = JS_NewContext(rt);

/* When done */
JS_FreeContext(ctx);
JS_FreeRuntime(rt);
```

For custom memory allocators, use `JS_NewRuntime2()` with a `JSMallocFunctions` struct. Use `JS_SetRuntimeOpaque()` / `JS_GetRuntimeOpaque()` to attach user data to the runtime, and `JS_SetContextOpaque()` / `JS_GetContextOpaque()` for context-level data.

## JSValue Handling

JSValue is the core type representing any JavaScript value. Reference counting applies to objects, strings, symbols, and BigInts (all negative tags).

```c
/* Creating values */
JSValue v_int = JS_NewInt32(ctx, 42);
JSValue v_str = JS_NewString(ctx, "hello");
JSValue v_float = JS_NewFloat64(ctx, 3.14);
JSValue v_bigint = JS_NewBigInt64(ctx, 1234567890123456789LL);

/* Special values */
JSValue v_null = JS_NULL;
JSValue v_undefined = JS_UNDEFINED;
JSValue v_true = JS_TRUE;
JSValue v_false = JS_FALSE;

/* Type checking */
JS_BOOL is_num = JS_IsNumber(v);
JS_BOOL is_str = JS_IsString(v);
JS_BOOL is_obj = JS_IsObject(v);
JS_BOOL is_bigint = JS_IsBigInt(ctx, v);
JS_BOOL is_func = JS_IsFunction(ctx, v);

/* Converting to C types */
int32_t i;
JS_ToInt32(ctx, &i, v_int);

double d;
JS_ToFloat64(ctx, &d, v_float);

const char *s = JS_ToCString(ctx, v_str);
/* use s ... */
JS_FreeCString(ctx, s);

/* Reference counting — critical for correctness */
JSValue dup = JS_DupValue(ctx, v_str);   /* increment refcount */
JS_FreeValue(ctx, v_str);                /* decrement refcount */
JS_FreeValue(ctx, dup);                  /* free when done */
```

Key rule: C functions receive constant JSValues (don't free them) and return newly allocated (=live) JSValues that the caller must free.

## Defining C Functions

Expose C functions to JavaScript using `JS_NewCFunction()`:

```c
/* Function signature: takes ctx, this_val, argc, argv */
static JSValue my_add(JSContext *ctx, JSValueConst this_val,
                      int argc, JSValueConst *argv) {
    double a, b;
    if (JS_ToFloat64(ctx, &a, argv[0]) < 0) return JS_EXCEPTION;
    if (JS_ToFloat64(ctx, &b, argv[1]) < 0) return JS_EXCEPTION;
    return JS_NewFloat64(ctx, a + b);
}

/* Register the function */
JSValue fn = JS_NewCFunction(ctx, my_add, "add", 2);
JSValue global = JS_GetGlobalObject(ctx);
JS_SetPropertyStr(ctx, global, "add", fn);
JS_FreeValue(ctx, fn);
JS_FreeValue(ctx, global);
```

For bulk property registration, use `JS_SetPropertyFunctionList()` with `JSCFunctionListEntry` arrays:

```c
static const JSCFunctionListEntry my_funcs[] = {
    JS_CFUNC_DEF("add", 2, my_add),
    JS_CFUNC_DEF("multiply", 2, my_multiply),
    JS_PROP_INT32_DEF("VERSION", 1, JS_PROP_CONFIGURABLE | JS_PROP_ENUMERABLE),
};

JS_SetPropertyFunctionList(ctx, global_obj, my_funcs,
                           sizeof(my_funcs) / sizeof(my_funcs[0]));
```

Function types available:

- `JS_CFUNC_DEF` — regular function
- `JS_CFUNC_MAGIC_DEF` — function with magic value
- `JS_CFUNC_SPECIAL_DEF` — constructor, getter/setter, iterator
- `JS_CGETSET_DEF` — getter/setter pair
- `JS_PROP_STRING_DEF`, `JS_PROP_INT32_DEF`, `JS_PROP_INT64_DEF`, `JS_PROP_DOUBLE_DEF` — constant properties

## Exception Handling

Most C API functions can return `JS_EXCEPTION`. Check explicitly:

```c
JSValue result = JS_Eval(ctx, source, strlen(source), "main.js",
                         JS_EVAL_TYPE_GLOBAL);
if (JS_IsException(result)) {
    JSValue exc = JS_GetException(ctx);
    const char *msg = JS_ToCString(ctx, exc);
    fprintf(stderr, "Error: %s\n", msg);
    JS_FreeCString(ctx, msg);
    JS_FreeValue(ctx, exc);
} else {
    /* use result */
    JS_FreeValue(ctx, result);
}
```

Throw exceptions from C functions:

```c
JSValue JS_ThrowTypeError(JSContext *ctx, const char *fmt, ...);
JSValue JS_ThrowSyntaxError(JSContext *ctx, const char *fmt, ...);
JSValue JS_ThrowReferenceError(JSContext *ctx, const char *fmt, ...);
JSValue JS_ThrowRangeError(JSContext *ctx, const char *fmt, ...);
JSValue JS_ThrowInternalError(JSContext *ctx, const char *fmt, ...);
JSValue JS_ThrowOutOfMemory(JSContext *ctx);
```

## Script Evaluation

Evaluate JavaScript source code:

```c
/* Flags for JS_Eval() */
#define JS_EVAL_TYPE_GLOBAL   (0 << 0)   /* global code (default) */
#define JS_EVAL_TYPE_MODULE   (1 << 0)   /* module code */
#define JS_EVAL_FLAG_STRICT   (1 << 3)   /* force strict mode */
#define JS_EVAL_FLAG_COMPILE_ONLY (1 << 5) /* compile but don't run */
#define JS_EVAL_FLAG_BACKTRACE_BARRIER (1 << 6)
#define JS_EVAL_FLAG_ASYNC    (1 << 7)   /* allow top-level await */

/* Evaluate a script */
JSValue result = JS_Eval(ctx, "1 + 2", 5, "expr.js", JS_EVAL_TYPE_GLOBAL);

/* Evaluate as module */
JSValue mod = JS_Eval(ctx, source, len, "mod.mjs",
                      JS_EVAL_TYPE_MODULE | JS_EVAL_FLAG_COMPILE_ONLY);

/* Evaluate compiled bytecode (from qjsc output) */
JSValue result = js_std_eval_binary(ctx, bytecode, bytecode_size, 0);
```

Detect whether source is a module: `JS_DetectModule(input, input_len)` returns non-zero if the source contains ES6 module syntax.

## JS Classes

Attach C opaque data to JavaScript objects via class IDs:

```c
/* Step 1: Register class ID (global, across all runtimes) */
static JSClassID my_class_id;
JS_NewClassID(&my_class_id);

/* Step 2: Define class (per runtime) */
static void my_finalizer(JSRuntime *rt, JSValue val) {
    void *data = JS_GetOpaque(val, my_class_id);
    if (data) free(data);
}

static const JSClassDef my_class_def = {
    "MyClass",
    .finalizer = my_finalizer,
};

JS_NewClass(rt, my_class_id, &my_class_def);

/* Step 3: Set prototype (per context) */
JSValue proto = JS_NewObject(ctx);
/* ... define methods on proto ... */
JS_SetClassProto(ctx, my_class_id, proto);
JS_FreeValue(ctx, proto);

/* Step 4: Create instances */
JSValue obj = JS_NewObjectClass(ctx, my_class_id);
MyData *data = malloc(sizeof(MyData));
JS_SetOpaque(obj, data);
```

Use `JS_GetOpaque()` to retrieve the C pointer, `JS_GetOpaque2()` for cross-context safety, and `JS_GetAnyOpaque()` to get opaque data with its class ID. Define a `gc_mark` callback in the class def so the cycle removal algorithm can find referenced objects.

## C Modules

Native ES6 modules written in C:

```c
static int my_module_init(JSContext *ctx, JSModuleDef *m) {
    JSValue ns = JS_GetModuleNamespace(ctx, m);

    const JSCFunctionListEntry exports[] = {
        JS_CFUNC_DEF("doSomething", 0, c_do_something),
    };

    JS_SetModuleExportList(ctx, m, exports,
                           sizeof(exports) / sizeof(exports[0]));
    JS_FreeValue(ctx, ns);
    return 0;
}

/* Register the module */
JS_NewCModule(ctx, "my_module", my_module_init);
```

Modules with `.so` extension are loaded as native modules using the C API. The standard library (`quickjs-libc.c`) itself is implemented as a native module.

## Memory Handling

```c
/* Set memory limit */
JS_SetMemoryLimit(rt, 64 * 1024 * 1024);

/* Custom allocators */
JSMallocFunctions mf = {
    .js_malloc = my_malloc,
    .js_free = my_free,
    .js_realloc = my_realloc,
    .js_malloc_usable_size = my_usable_size,
};
JSRuntime *rt = JS_NewRuntime2(&mf, opaque);

/* Query memory usage */
JSMemoryUsage usage;
JS_ComputeMemoryUsage(rt, &usage);
JS_DumpMemoryUsage(stdout, &usage, rt);

/* Force garbage collection */
JS_RunGC(rt);
```

## Execution Timeout and Interrupts

Set a callback invoked regularly during JavaScript execution:

```c
static int interrupt_cb(JSRuntime *rt, void *opaque) {
    /* Return non-zero to interrupt execution */
    return *(int *)opaque;
}

JS_SetInterruptHandler(rt, interrupt_cb, &interrupt_flag);
```

This is used by the `qjs` interpreter for Ctrl-C handling. The callback receives the runtime and opaque pointer.

## Module Loader

For dynamic module loading:

```c
typedef char *JSModuleNormalizeFunc(JSContext *ctx,
    const char *module_base_name,
    const char *module_name, void *opaque);

typedef JSModuleDef *JSModuleLoaderFunc(JSContext *ctx,
    const char *module_name, void *opaque);

JS_SetModuleLoaderFunc(rt, NULL, my_module_loader, NULL);
```

The newer `JS_SetModuleLoaderFunc2()` supports import attributes for JSON modules. Use `JS_GetImportMeta()` to access `import.meta` of a module.

## Jobs (Microtask Queue)

Pending jobs from async operations:

```c
/* Check if any jobs pending */
JS_BOOL pending = JS_IsJobPending(rt);

/* Execute one pending job */
JSContext *pctx;
JS_ExecutePendingJob(rt, &pctx);
```

## Object Writer/Reader

Serialize and deserialize JavaScript objects (used for precompiled bytecode):

```c
/* Write object to binary */
size_t size;
uint8_t *buf = JS_WriteObject(ctx, &size, obj,
                               JS_WRITE_OBJ_BYTECODE);

/* Read object from binary */
JSValue read_obj = JS_ReadObject(ctx, buf, size,
                                  JS_READ_OBJ_BYTECODE);

/* Evaluate bytecode function */
JSValue result = JS_EvalFunction(ctx, read_obj);
```

Flags: `JS_WRITE_OBJ_BSWAP` (byte-swapped output), `JS_WRITE_OBJ_SAB` (SharedArrayBuffer), `JS_WRITE_OBJ_REFERENCE` (arbitrary object graphs).

## PrintValue API

Pretty-print JavaScript values (added 2025-09-13):

```c
void JS_PrintValue(JSContext *ctx, JSPrintValueWrite *write_func,
                   void *opaque, JSValueConst val,
                   const JSPrintValueOptions *options);

/* Options: max_depth, max_string_length, max_item_count, show_hidden, raw_dump */
JSPrintValueOptions opts;
JS_PrintValueSetDefaultOptions(&opts);
opts.max_depth = 5;
```
