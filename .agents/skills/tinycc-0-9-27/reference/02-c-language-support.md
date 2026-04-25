# TinyCC C Language Support

## ANSI C (C89)

TCC implements all the ANSI C standard, including structure bit fields and floating point numbers (`long double`, `double`, and `float` fully supported).

## ISO C99 Extensions

### Implemented Features

| Feature | Description | Example |
|---------|-------------|---------|
| Variable-length arrays | VLA support | `int arr[n];` |
| `long long` | 64-bit integer types | `long long x = 0x123456789ABCDEFLL;` |
| `_Bool` | Boolean type | `_Bool flag = 1;` |
| `__func__` | Current function name string | `printf("%s\n", __func__);` |
| Variadic macros | `__VA_ARGS__` | `#define dprintf(l, ...) printf(__VA_ARGS__)` |
| Scoped declarations | Declarations anywhere in block | C++-style variable declarations |
| Designated initializers | Array/struct init in any order | `int tab[10] = { [5] = 5, [9] = 9 };` |
| Compound initializers | Anonymous arrays/structs | `int *p = (int[]){ 1, 2, 3 };` |
| Hex float constants | Hexadecimal floating point | `double d = 0x1234p10;` |
| `inline` keyword | Ignored (no-op) | — |
| `restrict` keyword | Ignored (no-op) | — |

**Missing C99 features**: Complex and imaginary numbers.

### Designated Initializers Examples

```c
// Array designators
int tab[10] = { 1, 2, [5] = 5, [9] = 9 };

// Struct designators
struct { int x, y; } st[10] = { [0].x = 1, [0].y = 2 };

// GNU-style label designators (without '=')
int a[10] = { [0] 1, [5] 2, 3, 4 };
struct { int x, y; } st = { x: 1, y: 1 };
```

### Compound Literals

```c
int *p = (int []){ 1, 2, 3 };   // pointer to initialized array
// Same works for structures and strings
```

### Hexadecimal Floating-Point

```c
double d = 0x1234p10;  // equivalent to 4771840.0
```

## GNU C Extensions

### `__attribute__` Support

| Attribute | Description | Example |
|-----------|-------------|---------|
| `aligned(n)` | Align to n bytes (power of two) | `int a __attribute__((aligned(8)));` |
| `packed` | Force 1-byte alignment | `int a __attribute__((packed));` |
| `section(name)` | Place in named section | `int a __attribute__((section(".mysec")));` |
| `unused` | Suppress unused warning | `int a __attribute__((unused));` |
| `cdecl` | Standard C calling convention (default) | — |
| `stdcall` | Pascal-like calling convention | `void f(void) __attribute__((stdcall));` |
| `regparm(n)` | Fast i386 calling, n=1..3 registers | `void f(int a,int b) __attribute__((regparm(2)));` |
| `dllexport` | Export from DLL (Windows only) | Function-level export |

```c
int a __attribute__((aligned(8), section(".mysection")));

int my_add(int a, int b) __attribute__((section(".mycodesection"))) {
    return a + b;
}
```

### Inline Assembly

TCC includes its own x86 inline assembler with gas-like syntax. GCC 3.x named operands are supported:

```c
static inline void *my_memcpy(void *to, const void *from, size_t n)
{
    int d0, d1, d2;
    __asm__ __volatile__(
        "rep ; movsl\n\t"
        "testb $2,%b4\n\t"
        "je 1f\n\t"
        "movsw\n"
        "1:\ttestb $1,%b4\n\t"
        "je 2f\n\t"
        "movsb\n"
        "2:"
        : "=&c" (d0), "=&D" (d1), "=&S" (d2)
        :"0" (n/4), "q" (n), "1" ((long)to), "2" ((long)from)
        : "memory");
    return to;
}
```

### Case Ranges

```c
switch(a) {
    case 1 ... 9:
        printf("range 1 to 9\n");
        break;
    default:
        printf("unexpected\n");
        break;
}
```

### GNU Variadic Macros

```c
#define dprintf(fmt, args...) printf(fmt, ## args)
dprintf("no arg\n");
dprintf("one arg %d\n", 1);
```

### Other GNU Extensions

| Extension | Description | Example |
|-----------|-------------|---------|
| `__FUNCTION__` | Same as `__func__` (string literal in TCC) | `printf("%s\n", __FUNCTION__);` |
| `__alignof__` | Get alignment of type/expression | `size_t a = __alignof__(int);` |
| `typeof(x)` | Return type of x | `typeof(x) y;` |
| Computed gotos | `&&label` returns pointer, `goto *expr` jumps | `void *p = &&my_label; goto *p;` |
| `__builtin_types_compatible_p()` | Type compatibility check | Compile-time type checking |
| `__builtin_constant_p()` | Constant expression check | `#if __builtin_constant_p(x)` |
| `#pragma pack` | Win32 compatibility | `#pragma pack(push, 1)` |

## TinyCC Extensions

| Extension | Description |
|-----------|-------------|
| `__TINYC__` | Predefined macro when compiling with TCC |
| `#!` at line start | Ignored (allows shebang scripts) |
| Binary literals | `0b101` instead of `5` |
| `__BOUNDS_CHECKING_ON__` | Defined when `-b` is active |

## Example: Self-Contained C Script

```c
#!/usr/local/bin/tcc -run
#include <tcclib.h>

/* This program computes Fibonacci numbers */
int fib(int n)
{
    if (n <= 2)
        return 1;
    else
        return fib(n-1) + fib(n-2);
}

int main(int argc, char **argv)
{
    int n;
    if (argc < 2) {
        printf("usage: fib n\nCompute nth Fibonacci number\n");
        return 1;
    }
    n = atoi(argv[1]);
    printf("fib(%d) = %d\n", n, fib(n));
    return 0;
}
```

Make executable and run: `chmod +x fib.c && ./fib.c 10` → `fib(10) = 89`

## tcclib.h — Minimal libc for TCC

TCC ships with a minimal header `tcclib.h` for environments where full glibc headers are too large:

```c
#include <tcclib.h>
/* Provides: malloc, free, printf, sprintf, strlen, strcpy, strcat,
   memcpy, memset, atoi, strtol, fopen, fclose, fgets, putchar,
   dlopen, dlsym, dlclose, and more */
```

This is particularly useful for rescue disks and minimal environments where standard headers would be too large to include.
