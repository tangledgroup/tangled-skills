# C Language Support

## ANSI C

TCC implements the full ANSI C standard, including structure bit fields and floating point numbers (`long double`, `double`, `float` fully supported).

## ISO C99 Extensions

Missing items: complex and imaginary numbers.

Implemented features:

**Variable length arrays:**

```c
void func(int n) {
    int arr[n];  // VLA
}
```

**64-bit `long long` types:** Fully supported.

**Boolean type `_Bool`:** Supported as a native type.

**`__func__`:** A string variable containing the current function name.

**Variadic macros with `__VA_ARGS__`:**

```c
#define dprintf(level, __VA_ARGS__) printf(__VA_ARGS__)
dprintf(1, "value = %d\n", x);
```

**Declarations anywhere in a block (C++ style):**

```c
void func() {
    int a = 1;
    int b = 2;  // declaration after code
}
```

**Designated initializers:**

```c
struct { int x, y; } st[10] = { [0].x = 1, [0].y = 2 };
int tab[10] = { 1, 2, [5] = 5, [9] = 9 };
```

**Compound initializers:**

```c
int *p = (int []){ 1, 2, 3 };
```

**Hexadecimal floating point constants:**

```c
double d = 0x1234p10;  // same as 4771840.0
```

**`inline` and `restrict` keywords:** Ignored (no effect).

**`_Generic`:** Supported (0.9.27).

## GNU C Extensions

**Array designators without `=`:**

```c
int a[10] = { [0] 1, [5] 2, 3, 4 };
```

**Structure field designators as labels:**

```c
struct { int x, y; } st = { x: 1, y: 1 };
// instead of: { .x = 1, .y = 1 }
```

**`\e` escape:** ASCII character 27.

**Case ranges:**

```c
switch(a) {
    case 1 ... 9:
        printf("range 1 to 9\n");
        break;
}
```

**`__attribute__`:**

- `aligned(n)` — Align variable or struct field to n bytes (power of two).
- `packed` — Force alignment to 1.
- `section(name)` — Generate function or data in named section.
- `unused` — Suppress unused variable/function warnings.
- `cdecl` — Standard C calling convention (default).
- `stdcall` — Pascal-like calling convention.
- `regparm(n)` — Fast i386 calling convention, n (1-3) parameters in `%eax`, `%edx`, `%ecx`.
- `dllexport` — Export function from DLL/executable (win32 only).

```c
int a __attribute__((aligned(8), section(".mysection")));

int my_add(int a, int b) __attribute__((section(".mycodesection"))) {
    return a + b;
}
```

**GNU-style variadic macros:**

```c
#define dprintf(fmt, args...) printf(fmt, ## args)
dprintf("no arg\n");
dprintf("one arg %d\n", 1);
```

**`__FUNCTION__`:** Interpreted as C99 `__func__`.

**`__alignof__`:** Returns alignment of a type or expression (like `sizeof`).

**`typeof(x)`:** Returns the type of expression or type `x`.

**Computed gotos:**

```c
void **label_ptr = &&my_label;
goto *label_ptr;
// ...
my_label: printf("here\n");
```

**Inline assembly (`asm` / `__asm__`):**

TCC includes its own x86 inline assembler with gas-like (GNU assembler) syntax. No intermediate files are generated. GCC 3.x named operands are supported.

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
        : "=&c"(d0), "=&D"(d1), "=&S"(d2)
        : "0"(n/4), "q"(n), "1"((long)to), "2"((long)from)
        : "memory");
    return to;
}
```

**`__builtin_types_compatible_p()` and `__builtin_constant_p()`:** Supported.

**`#pragma pack`:** Supported for win32 compatibility.

## TinyCC Extensions

**`__TINYC__`:** Predefined macro indicating TCC is the compiler.

**`#!` at line start:** Ignored to allow C scripting with shebangs.

**Binary literals:** `0b101` instead of `5`.

**`__BOUNDS_CHECKING_ON`:** Defined when bound checking is activated (`-b` flag).

## UTF-8 in String Literals

Supported since 0.9.27.
