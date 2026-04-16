# QuickJS C API Reference

## Runtime and Contexts

```c
// Create a runtime (object heap)
JSRuntime *JS_NewRuntime(void);

// Create with custom memory allocator
JSRuntime *JS_NewRuntime2(const JSClassAllocator *allocator);

// Set memory limit
void JS_SetMemoryLimit(JSRuntime *rt, size_t limit);

// Set max stack size
void JS_SetMaxStackSize(JSRuntime *rt, size_t stack_size);

// Create a context (realm) within a runtime
JSContext *JS_NewContext(JSRuntime *rt);

// Get/set runtime opaque pointer
void *JS_GetRuntimeOpaque(JSRuntime *rt);
void  JS_SetRuntimeOpaque(JSRuntime *rt, void *opaque);
```

**Key concepts:**
- `JSRuntime` = object heap. Multiple runtimes can coexist but cannot exchange objects
- `JSContext` = realm with its own global/system objects. Multiple contexts per runtime can share objects
- No multi-threading support within a given runtime

## JSValue

A JavaScript value (primitive or object). Uses reference counting — always balance `JS_DupValue()` / `JS_FreeValue()`.

```c
// Value type checks
int JS_IsUndefined(JSValue val);
int JS_IsNull(JSValue val);
int JS_IsBool(JSValue val);
int JS_IsNumber(JSValue val);
int JS_IsString(JSValue val);
int JS_IsObject(JSValue val);
int JS_IsBigInt(JSContext *ctx, JSValue val);

// Conversion to C
int   JS_ToInt32(JSContext *ctx, int32_t *pres, JSValue val);
int64_t JS_ToInt64(JSContext *ctx, int64_t *pres, JSValue val);
double JS_ToFloat64(JSContext *ctx, double *pres, JSValue val);
char *JS_ToCStringLen(JSContext *ctx, size_t *plen, JSValue val);
void  JS_FreeCString(JSContext *ctx, char *str);

// Conversion from C
JSValue JS_NewBool(JSContext *ctx, int val);
JSValue JS_NewInt32(JSContext *ctx, int32_t val);
JSValue JS_NewFloat64(JSContext *ctx, double val);
JSValue JS_NewStringLen(JSContext *ctx, const char *str, size_t len);
JSValue JS_NewString(JSContext *ctx, const char *str16);
JSValue JS_NewBigInt64(JSContext *ctx, int64_t v);
JSValue JS_NewUint32(JSContext *ctx, uint32_t v);

// Dup/Free
JSValue JS_DupValue(JSContext *ctx, JSValue val);
void    JS_FreeValue(JSContext *ctx, JSValue val);
void    JS_FreeValue2(JSRuntime *rt, JSValue val, int ref);
```

**Note:** In 64-bit code, JSValue is 128-bit (fits two CPU registers). In 32-bit, NaN boxing stores 64-bit floats.

## C Functions

```c
// Declare a C function
JSValue js_my_function(JSContext *ctx, JSValue this_val,
                       int argc, JSValue *argv);

// Register as property on an object
void JS_SetPropertyFunctionList(JSContext *ctx, JSValue obj,
                                 const JSCFunctionListEntry *cproto,
                                 int size);

// Function types
typedef enum {
    JS_CFUNC_generic,
    JS_CFUNC_generic_index,
    JS_CFUNC_constructor,
    JS_CFUNC_constructor_or_func,
    JS_CFUNC_magic,
    JS_CFUNC_getter,
    JS_CFUNC_setter,
    JS_CFUNC_getsetter,
} JSCFunctionEnum;

// Macro for creating function entries
JS_CFUNC_DEF("name", nargs, func)
JS_CGETSET_DEF("name", getter, setter)
JS_PROP_STRING_DEF("name", "str", flags)
JS_PROP_INTDEF("name", intval, flags)
JS_PROP_DOUBLEDEF("name", floatval, flags)
```

**C function conventions:**
- Parameters are normal C parameters (no implicit stack)
- Take `const JSValue *` for input (don't need to free)
- Return a newly allocated (=live) JSValue
- Check for exceptions: `if (JS_IsException(retval)) { ... }`

## Exceptions

```c
// Most C functions can return an exception
JSValue retval = some_js_function(ctx, ...);

if (JS_IsException(retval)) {
    JSValue exc = JS_GetException(ctx);
    // Handle exception...
    JS_FreeValue(ctx, exc);
    return retval;  // Propagate the exception
}
```

- `JS_EXCEPTION` is a special JSValue indicating an error occurred
- The actual exception object is stored in the JSContext and retrieved via `JS_GetException()`

## Script Evaluation

```c
// Evaluate JavaScript source
JSValue JS_Eval(JSContext *ctx, const char *input, size_t input_len,
                int flags);

// Flags: JS_EVAL_TYPE_GLOBAL, JS_EVAL_TYPE_MODULE, JS_EVAL_TYPE_MASK,
//        JS_EVAL_FLAG_STRICT, JS_EVAL_FLAG_COMPILE_ONLY,
//        JS_EVAL_FLAG_STRIP

// Compile-only mode (returns bytecode)
JSValue JS_CompileValue(JSContext *ctx, JSValue val);

// Evaluate compiled bytecode
void js_std_eval_binary(JSContext *ctx, const uint8_t *bc_buf,
                        size_t bc_buf_len, int flags);

// Evaluate this in a module context
JSValue JS_EvalThis(JSContext *ctx, JSValue val);
```

## JS Classes (C Classes)

```c
// Register a new class ID (globally allocated)
int JS_NewClassID(JSClassID *pclass_id);

// Define a class (per runtime)
int JS_NewClass(JSRuntime *rt, JSClassID class_id,
                const JSClassDef *class_def);

// Create an object of the class
JSValue JS_NewObjectClass(JSContext *ctx, JSClassID class_id);

// Set prototype for a class in a context
int JS_SetClassProto(JSContext *ctx, JSClassID class_id,
                     JSValue proto);

// Get/set opaque C data attached to an object
void *JS_GetOpaque(JSContext *ctx, JSValue obj, JSClassID class_id);
int  JS_SetOpaque(JSValue obj, void *opaque);

// Get any opaque (without class check)
void *JS_GetAnyOpaque(JSValue val, const char *name);
```

**JSClassDef:**
```c
typedef struct {
    const char *class_name;
    JSCFunctionType finalizer;      // Called when object is destroyed
    JSCFunctionType gc_mark;        // For cycle removal algorithm
    JSClassExoticMethods exotic;    // Exotic object behaviors
} JSClassDef;
```

## C Modules

Native ES6 modules can be dynamically or statically linked:

```c
// Module initialization function signature
typedef int (*JSModuleInitFunc)(JSContext *ctx,
                                 JSModuleDef *m);

// Load a module from file
JSModuleDef *js_module_loader(JSContext *ctx,
                               const char *module_name,
                               void *opaque);
```

## Memory Handling

```c
// Set memory allocation limit
void JS_SetMemoryLimit(JSRuntime *rt, size_t limit);

// Custom allocator (use with JS_NewRuntime2)
typedef struct {
    void *(*js_malloc)(void *opaque, size_t size);
    void (*js_free)(void *opaque, void *ptr);
    void *(*js_realloc)(void *opaque, void *ptr, size_t size);
    uint64_t (*js_malloc_usable_size)(const void *ptr);
} JSClassAllocator;

// Get/set runtime opaque data
void *JS_GetRuntimeOpaque(JSRuntime *rt);
void  JS_SetRuntimeOpaque(JSRuntime *rt, void *opaque);
```

## Execution Timeout and Interrupts

```c
// Set callback for execution timeout / Ctrl-C handler
void JS_SetInterruptHandler(JSRuntime *rt,
                             void (*callback)(JSRuntime *rt, void *opaque),
                             void *opaque);

// Update stack top (for embedded use)
void JS_UpdateStackTop(JSContext *ctx);
```

## Additional API Functions

```c
// Atom operations
JSAtom JS_NewAtomStringLen(JSContext *ctx, const char *str, size_t len);
JSAtom JS_AtomFromCStringLen(const char *str, size_t len);
char  *JS_AtomToCStringLen(JSContext *ctx, size_t *plen, JSAtom atom);
void   JS_FreeAtom(JSContext *ctx, JSAtom atom);

// Property enumeration
int JS_Enumerate(JSContext *ctx, JSValue obj);
int JS_GetPropertyEnum(JSContext *ctx, JSValue obj, JSAtom prop_name);
void JS_FreePropertyEnum(JSContext *ctx, JSAtom *tab, int len);

// Promise handling
JSValue JS_NewPromiseCapability(JSContext *ctx, JSValue *promises);

// Value to string
char *JS_ValueToCString(JSContext *ctx, JSValue val);

// Error handling
int JS_SetHostPromiseRejectionTracker(JSRuntime *rt,
                                       void (*callback)(JSContext *ctx,
                                                        JSValue promise,
                                                        JSValue reason,
                                                        int is_handled,
                                                        void *opaque),
                                       void *opaque);
```

## Example: Creating a C Class

See `quickjs-libc.c` for full examples. Basic pattern:

```c
// 1. Register class ID
static JSClassID my_class_id;

// 2. Define class with finalizer and methods
static const JSClassDef my_class_def = {
    .class_name = "MyClass",
    .finalizer = my_finalizer,
    .gc_mark = my_gc_mark,
};

// Initialize once at startup:
JS_NewClassID(&my_class_id);
JS_NewClass(rt, my_class_id, &my_class_def);

// 3. Create instances and attach opaque data
JSValue obj = JS_NewObjectClass(ctx, my_class_id);
MyStruct *data = malloc(sizeof(MyStruct));
JS_SetOpaque(obj, data);

// 4. Set prototype
JSValue proto = JS_NewObject(ctx);
JS_SetPropertyFunctionList(ctx, proto, my_funcs, count);
JS_SetClassProto(ctx, my_class_id, proto);
```
