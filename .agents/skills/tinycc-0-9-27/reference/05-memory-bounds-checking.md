# Memory and Bounds Checking

## Overview

TCC's bounds checking feature is activated with the `-b` flag (which implies `-g`). It inserts runtime checks for memory safety while allowing all standard C pointer operations. Pointer size is unchanged, and bound-checked code is fully compatible with unchecked code — when a pointer comes from unchecked code, it is assumed valid.

The `-b` flag is only available on i386 when using libtcc.

## What Is Checked

**Buffer overflows in standard string functions:**

```c
{
    char tab[10];
    memset(tab, 0, 11);  // ERROR: writes 11 bytes into 10-byte buffer
}
```

**Out-of-bounds access in local arrays:**

```c
{
    int tab[10];
    for (i = 0; i < 11; i++) {
        sum += tab[i];  // ERROR: tab[10] is out of bounds
    }
}
```

**Out-of-bounds access in global arrays:**

```c
int global_tab[10];
void func() {
    global_tab[10] = 42;  // ERROR: out of bounds
}
```

**Out-of-bounds access in malloc'd data:**

```c
{
    int *tab = malloc(20 * sizeof(int));
    for (i = 0; i < 21; i++) {
        sum += tab[i];  // ERROR: tab[20] is out of bounds
    }
    free(tab);
}
```

**Use-after-free:**

```c
{
    int *tab = malloc(20 * sizeof(int));
    free(tab);
    for (i = 0; i < 20; i++) {
        sum += tab[i];  // ERROR: accessing freed memory
    }
}
```

**Double-free:**

```c
{
    int *tab = malloc(20 * sizeof(int));
    free(tab);
    free(tab);  // ERROR: double free
}
```

## Usage

Compile with `-b` to enable bounds checking:

```bash
tcc -b -run test.c
```

Combine with `-g` for detailed error messages (though `-b` implies `-g`):

```bash
tcc -b -g -o test test.c
./test
```

Use `-bt N` to display N callers in stack traces:

```bash
tcc -b -bt 5 -run test.c
```

## Mixing Checked and Unchecked Code

Bound-checked code can be mixed freely with standard (unchecked) code. When a pointer originates from unchecked code, it is assumed valid. Even obscure C code with casts should work correctly.

The `__BOUNDS_CHECKING_ON` macro is defined when bounds checking is active, allowing conditional compilation:

```c
#ifdef __BOUNDS_CHECKING_ON
// bounds checking is enabled
#endif
```

## Performance Impact

Code generated with `-b` is slower and produces larger binaries. Use it during development and debugging, not in production builds.
