# Bytecode and VM Internals

## Instruction Set

TinyPy uses a compact 4-byte instruction format. Each instruction has an opcode byte plus three parameter bytes (a, b, c):

```c
typedef union tp_code {
    unsigned char i;
    struct { unsigned char i, a, b, c; } regs;
    struct { char val[4]; } string;
    struct { float val; } number;
} tp_code;
```

### Opcodes

| Opcode | Name | Description |
|--------|------|-------------|
| 0 | TP_IEOF | End of code — return None |
| 1 | TP_IADD | RA = RB + RC |
| 2 | TP_ISUB | RA = RB - RC |
| 3 | TP_IMUL | RA = RB * RC |
| 4 | TP_IDIV | RA = RB / RC |
| 5 | TP_IPOW | RA = RB ** RC |
| 6 | TP_IAND | RA = RB & RC (bitwise) |
| 7 | TP_IOR | RA = RB \| RC (bitwise) |
| 8 | TP_ICMP | RA = compare(RB, RC) |
| 9 | TP_IGET | RA = RB[RC] |
| 10 | TP_ISET | RA[RB] = RC |
| 11 | TP_INUMBER | Load double from following bytes |
| 12 | TP_ISTRING | Load string (length in b,c as 16-bit) |
| 13 | TP_IGGET | Global get with builtin fallback |
| 14 | TP_IGSET | Global set |
| 15 | TP_IMOVE | RA = RB |
| 16 | TP_IDEF | Define function (pointer to code) |
| 17 | TP_IPASS | No-op |
| 18 | TP_IJUMP | Relative jump (signed 16-bit in b,c) |
| 19 | TP_ICALL | RA = call(RB, RC) |
| 20 | TP_IRETURN | Return RA from current frame |
| 21 | TP_IIF | Conditional: if RA truthy, skip next instruction |
| 22 | TP_IDEBUG | Debug print |
| 23 | TP_IEQ | RA = (RB == RC) |
| 24 | TP_ILE | RA = (RB <= RC) |
| 25 | TP_ILT | RA = (RB < RC) |
| 26 | TP_IDICT | Create dict from pairs |
| 27 | TP_ILIST | Create list from items |
| 28 | TP_INONE | RA = None |
| 29 | TP_ILEN | RA = len(RB) |
| 30 | TP_IPOS | Position info (line number + source text) |
| 31 | TP_IPARAMS | Create parameter list |
| 32 | TP_IIGET | Failsafe get (no exception on miss) |
| 33 | TP_IFILE | Set filename for traceback |
| 34 | TP_INAME | Set function name for traceback |
| 35 | TP_INE | RA = (RB != RC) |
| 36 | TP_IHAS | RA = has(RB, RC) |
| 37 | TP_IRAISE | Raise exception in RA |
| 38 | TP_ISETJMP | Set jump target for exception handling |
| 39 | TP_IMOD | RA = RB % RC |
| 40 | TP_ILSH | RA = RB << RC |
| 41 | TP_IRSH | RA = RB >> RC |
| 42 | TP_IITER | Iterate (list/string by index, dict keys) |
| 43 | TP_IDEL | Delete RA[RB] |
| 44 | TP_IREGS | Set register count for frame |

## Execution Model

### tp_step

The main execution loop in `tp_step()` fetches the current instruction and dispatches via a switch statement. Each iteration processes one bytecode instruction:

```c
int tp_step(TP) {
    tp_frame_ *f = &tp->frames[tp->cur];
    tp_obj *regs = f->regs;
    tp_code *cur = f->cur;
    while(1) {
        tp_code e = *cur;
        switch (e.i) {
            case TP_IADD: RA = tp_add(tp, RB, RC); break;
            case TP_ICALL: _tp_call(tp, &RA, RB, RC); cur++; SR(0); break;
            /* ... all other opcodes ... */
        }
        cur += 1;
    }
}
```

The `SR(0)` macro saves the current position and returns, used after calls that may modify control flow.

### Frames

Each call frame (`tp_frame_`) contains:

- `codes` — pointer to bytecode
- `cur` — current instruction pointer
- `jmp` — exception jump target (for try/except)
- `regs` — register array for local variables
- `ret_dest` — destination for return value
- `fname`, `name`, `line` — traceback information
- `globals` — global symbol dictionary
- `lineno` — current line number
- `cregs` — count of registers used

Maximum frames: 256 (`TP_FRAMES`). Maximum registers: 16384 (`TP_REGS`). Stack overflow is detected and raises an exception.

### tp_run

```c
void tp_run(TP, int cur) {
    if (tp->jmp) { tp_raise(,"tp_run(%d) called recursively",cur); }
    tp->jmp = 1;
    if (setjmp(tp->buf)) { tp_handle(tp); }
    while (tp->cur >= cur && tp_step(tp) != -1);
    tp->cur = cur-1;
    tp->jmp = 0;
}
```

Uses `setjmp`/`longjmp` for exception handling. When `tp_raise` is called, it does `longjmp` back to the set point, then `tp_handle` walks frames to find a try/except handler.

### Exception Handling

When an exception is raised:

1. `_tp_raise` stores the exception message and calls `longjmp(tp->buf, 1)`
2. `tp_run` catches the jump and calls `tp_handle`
3. `tp_handle` walks frames backward looking for a set jump target (`f->jmp`)
4. If found, execution resumes at that point
5. If not found, `tp_print_stack` prints the full traceback and exits

Traceback includes filename, line number, function name, and source line text for each frame.

## Function Calls

### C Functions

C functions are registered with `tp_fnc(tp, func_ptr)`. When called from tinypy code, `_tp_tcall` invokes them directly. Parameters are accessed via `TP_OBJ()` macro which pops from the parameter list.

### Tinypy Functions

Tinypy functions store a pointer to their compiled bytecode and a globals dictionary. When called, a new frame is created with the function's bytecode and globals, then execution continues in `tp_step`.

Function types (`ftype`):
- 0 — C function
- 1 — Tinypy function
- 2 (bitwise OR) — Bound method (self prepended to params)

## Register Allocation

The encoder uses a simple register allocator:

- Registers are allocated from a pool of up to 256 per frame
- `alloc(n)` finds the first gap of `n` free registers
- Temporary registers are named `$0`, `$1`, etc.
- Named variables map to specific registers
- An assertion after each frame verifies no temp registers were leaked
