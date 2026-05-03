# Evaluation Cycle & Continuations

## Contents
- Register Machine
- Dump Stack Implementations
- s_save and s_return
- Core Evaluation (OP_EVAL)
- Argument Evaluation Chain
- Closure Application
- Special Form Implementation Patterns
- Continuations (call/cc)
- Macro Expansion

## Register Machine

The interpreter uses four registers plus a value register:

```c
pointer args;    /* arguments for current function call */
pointer envir;   /* current environment chain */
pointer code;    /* expression currently being evaluated */
pointer dump;    /* dump stack (saved contexts) */
pointer value;   /* result of last evaluation */
```

These registers form a simple abstract machine. The evaluation cycle manipulates them through `s_save()` (push context), `_s_return()` (pop and restore), and `s_goto()` (jump to opcode).

## Dump Stack Implementations

Two implementations controlled by `USE_SCHEME_STACK`:

### C Heap Version (default when USE_SCHEME_STACK is undefined)

```c
struct dump_stack_frame {
  enum scheme_opcodes op;
  pointer args;
  pointer envir;
  pointer code;
};

static void s_save(scheme *sc, enum scheme_opcodes op, pointer args, pointer code) {
  if ((int)sc->dump >= sc->dump_size) {
    sc->dump_size += STACK_GROWTH;  /* 3 */
    sc->dump_base = realloc(sc->dump_base,
                            sizeof(struct dump_stack_frame) * sc->dump_size);
  }
  struct dump_stack_frame *next = (struct dump_stack_frame *)sc->dump_base + (int)sc->dump;
  next->op = op;
  next->args = args;
  next->envir = sc->envir;
  next->code = code;
  sc->dump = (pointer)((int)sc->dump + 1);
}
```

Faster but doesn't support proper continuations — the dump stack is a C array that can't be captured into a Scheme value.

### Scheme Cons Version (USE_SCHEME_STACK defined)

```c
static void s_save(scheme *sc, enum scheme_opcodes op, pointer args, pointer code) {
    sc->dump = cons(sc, sc->envir, cons(sc, code, sc->dump));
    sc->dump = cons(sc, args, sc->dump);
    sc->dump = cons(sc, mk_integer(sc, (long)op), sc->dump);
}
```

Stores each frame as `(op . (args . (envir . (code . rest))))` — a cons cell chain. Slower but the dump stack is itself a Scheme object that can be captured by continuations.

### Return from Both

```c
static pointer _s_return(scheme *sc, pointer a) {
    sc->value = a;
    if (dump_empty_p(sc)) return sc->NIL;  /* no more frames */

    /* Pop frame, restore registers */
    sc->op = frame->op;
    sc->args = frame->args;
    sc->envir = frame->envir;
    sc->code = frame->code;
    /* Adjust dump pointer */
    return sc->T;  /* Continue Eval_Cycle loop */
}
```

## s_save and s_return

The control flow pattern for special forms:

```c
case OP_IF0:        /* if */
    s_save(sc, OP_IF1, sc->NIL, cdr(sc->code));  /* Save: after evaluating condition, come here with <then> <else> */
    sc->code = car(sc->code);                      /* Evaluate condition */
    s_goto(sc, OP_EVAL);

case OP_IF1:        /* if — condition evaluated, pick branch */
    if (is_true(sc->value))
         sc->code = car(sc->code);   /* then-branch */
    else
         sc->code = cadr(sc->code);  /* else-branch (car(NIL) = NIL for (if #f 1)) */
    s_goto(sc, OP_EVAL);
```

Pattern: `s_save(next_opcode, args, extra_data)` pushes the current context and arranges for the next iteration to execute `next_opcode` with specified args. The handler then sets up `sc->code` and calls `s_goto(OP_EVAL)` to evaluate a sub-expression.

## Core Evaluation (OP_EVAL)

```c
case OP_EVAL:
    if (is_symbol(sc->code)) {
        /* Variable lookup */
        x = find_slot_in_env(sc, sc->envir, sc->code, 1);
        if (x != sc->NIL)
            s_return(sc, slot_value_in_env(x));
        else
            Error_1(sc, "eval: unbound variable:", sc->code);
    } else if (is_pair(sc->code)) {
        /* Function application */
        if (is_syntax(x = car(sc->code))) {
            /* Special form — dispatch directly */
            sc->code = cdr(sc->code);
            s_goto(sc, syntaxnum(x));
        } else {
            /* Procedure call — evaluate operator and operands */
            s_save(sc, OP_E0ARGS, sc->NIL, sc->code);
            sc->code = car(sc->code);
            s_goto(sc, OP_EVAL);
        }
    } else {
        /* Self-evaluating: numbers, strings, symbols not in env, etc. */
        s_return(sc, sc->code);
    }
```

Three cases:
1. **Symbol**: Look up in environment chain, return bound value
2. **Pair**: Check if car is syntax (special form) or procedure (normal call)
3. **Atom**: Return itself (self-evaluating)

## Argument Evaluation Chain

For procedure calls, arguments are evaluated left-to-right and collected into a list:

```c
case OP_E0ARGS:     /* Start evaluating arguments */
    if (is_macro(sc->value)) {    /* Macro expansion */
        s_save(sc, OP_DOMACRO, sc->NIL, sc->NIL);
        sc->args = cons(sc, sc->code, sc->NIL);
        sc->code = sc->value;
        s_goto(sc, OP_APPLY);
    } else {
        sc->code = cdr(sc->code);  /* Move to first argument */
        s_goto(sc, OP_E1ARGS);
    }

case OP_E1ARGS:     /* Collect evaluated arguments */
    sc->args = cons(sc, sc->value, sc->args);
    if (is_pair(sc->code)) {       /* More arguments */
        s_save(sc, OP_E1ARGS, sc->args, cdr(sc->code));
        sc->code = car(sc->code);
        sc->args = sc->NIL;
        s_goto(sc, OP_EVAL);
    } else {                        /* Done — apply */
        sc->args = reverse_in_place(sc, sc->NIL, sc->args);
        sc->code = car(sc->args);   /* The procedure */
        sc->args = cdr(sc->args);   /* The argument list */
        s_goto(sc, OP_APPLY);
    }
```

Arguments are collected in reverse order (each new arg consed to front), then reversed before application. This is the standard Scheme left-to-right evaluation order.

## Closure Application

```c
case OP_APPLY:
    if (is_proc(sc->code)) {
        s_goto(sc, procnum(sc->code));   /* Built-in procedure */
    } else if (is_foreign(sc->code)) {
        push_recent_alloc(sc, sc->args, sc->NIL);
        x = sc->code->_object._ff(sc, sc->args);
        s_return(sc, x);
    } else if (is_closure(sc->code) || is_macro(sc->code) || is_promise(sc->code)) {
        /* Create new environment frame */
        new_frame_in_env(sc, closure_env(sc->code));

        /* Bind parameters to arguments */
        for (x = car(closure_code(sc->code)), y = sc->args;
             is_pair(x); x = cdr(x), y = cdr(y)) {
            if (y == sc->NIL) Error_0(sc, "not enough arguments");
            new_slot_in_env(sc, car(x), car(y));
        }

        /* Dotted tail: (lambda (a . rest) ...) binds rest to remaining args */
        if (x == sc->NIL) {
            /* exact match — extra args silently accepted (non-R5RS) */
        } else if (is_symbol(x)) {
            new_slot_in_env(sc, x, y);  /* Bind dotted symbol to remaining args */
        } else {
            Error_1(sc, "syntax error in closure: not a symbol:", x);
        }

        /* Execute body */
        sc->code = cdr(closure_code(sc->code));
        sc->args = sc->NIL;
        s_goto(sc, OP_BEGIN);
    } else if (is_continuation(sc->code)) {
        sc->dump = cont_dump(sc->code);
        s_return(sc, sc->args != sc->NIL ? car(sc->args) : sc->NIL);
    } else {
        Error_0(sc, "illegal function");
    }
```

Closure structure: `(parameter-list . body)` paired with captured environment. The parameter list is a list of symbols (or dotted for rest args). Body is a sequence of expressions executed via OP_BEGIN.

## Special Form Implementation Patterns

### begin — Sequential evaluation

```c
case OP_BEGIN:
    if (!is_pair(sc->code)) s_return(sc, sc->code);
    if (cdr(sc->code) != sc->NIL)
        s_save(sc, OP_BEGIN, sc->NIL, cdr(sc->code));  /* Save rest */
    sc->code = car(sc->code);
    s_goto(sc, OP_EVAL);                               /* Eval first */
```

### cond — Conditional with => support

```c
case OP_COND0:
    s_save(sc, OP_COND1, sc->NIL, sc->code);
    sc->code = caar(sc->code);   /* First clause's test */
    s_goto(sc, OP_EVAL);

case OP_COND1:
    if (is_true(sc->value)) {
        if ((sc->code = cdar(sc->code)) == sc->NIL)
            s_return(sc, sc->value);
        if (car(sc->code) == sc->FEED_TO) {  /* => syntax */
            /* Call the procedure with the test value */
            x = cons(sc, sc->QUOTE, cons(sc, sc->value, sc->NIL));
            sc->code = cons(sc, cadr(sc->code), cons(sc, x, sc->NIL));
            s_goto(sc, OP_EVAL);
        }
        s_goto(sc, OP_BEGIN);  /* Evaluate clause body */
    } else {
        /* Try next clause or return () */
    }
```

### let — Create new environment

```c
case OP_LET0:       /* Parse bindings */
    sc->args = sc->NIL;
    sc->value = sc->code;
    sc->code = car(sc->code);  /* Binding list */
    s_goto(sc, OP_LET1);

case OP_LET1:       /* Evaluate init expressions */
    sc->args = cons(sc, sc->value, sc->args);
    if (is_pair(sc->code)) {
        s_save(sc, OP_LET1, sc->args, cdr(sc->code));
        sc->code = cadar(sc->code);  /* Init expression */
        s_goto(sc, OP_EVAL);
    } else {
        /* All inits evaluated — create frame */
        sc->args = reverse_in_place(sc, sc->NIL, sc->args);
        s_goto(sc, OP_LET2);
    }

case OP_LET2:       /* Bind and execute body */
    new_frame_in_env(sc, sc->envir);
    for (x = car(sc->code), y = sc->args; y != sc->NIL; x = cdr(x), y = cdr(y))
        new_slot_in_env(sc, caar(x), car(y));
    /* Named let: create recursive closure and bind it */
    sc->code = cdr(sc->code);  /* Body */
    s_goto(sc, OP_BEGIN);
```

### and/or — Short-circuit

```c
case OP_AND0:
    if (sc->code == sc->NIL) s_return(sc, sc->T);  /* (and) => #t */
    s_save(sc, OP_AND1, sc->NIL, cdr(sc->code));
    sc->code = car(sc->code);
    s_goto(sc, OP_EVAL);

case OP_AND1:
    if (is_false(sc->value))
        s_return(sc, sc->value);       /* Short-circuit on false */
    else if (sc->code == sc->NIL)
        s_return(sc, sc->value);       /* Last value */
    else {
        s_save(sc, OP_AND1, sc->NIL, cdr(sc->code));
        sc->code = car(sc->code);
        s_goto(sc, OP_EVAL);
    }
```

## Continuations (call/cc)

```c
case OP_CONTINUATION:
    sc->code = car(sc->args);
    sc->args = cons(sc, mk_continuation(sc, sc->dump), sc->NIL);
    s_goto(sc, OP_APPLY);
```

`mk_continuation()` captures the current dump stack into a `T_CONTINUATION` cell. When the continuation is applied, it replaces `sc->dump` with the captured stack and returns the argument as the value of the call/cc expression:

```c
/* In OP_APPLY, continuation case: */
if (is_continuation(sc->code)) {
    sc->dump = cont_dump(sc->code);
    s_return(sc, sc->args != sc->NIL ? car(sc->args) : sc->NIL);
}
```

This implements full first-class continuations — the entire control state is captured and can be invoked later to restore that exact point in execution. Only works correctly with `USE_SCHEME_STACK` (cons-based dump stack).

## Macro Expansion

Macros are detected during argument evaluation (OP_E0ARGS):

```c
case OP_E0ARGS:
    if (is_macro(sc->value)) {
        s_save(sc, OP_DOMACRO, sc->NIL, sc->NIL);
        sc->args = cons(sc, sc->code, sc->NIL);  /* Pass the form as argument */
        sc->code = sc->value;                     /* The macro closure */
        s_goto(sc, OP_APPLY);
    }
```

The macro (a closure with `T_MACRO` flag) receives the unevaluated form, expands it, and returns the result. `OP_DOMACRO` then re-evaluates the expanded form:

```c
case OP_DOMACRO:
    sc->code = sc->value;
    s_goto(sc, OP_EVAL);
```

TinyScheme's macros are implemented via `*compile-hook*` — a global variable that, when defined, is called on every lambda body during closure creation. The default `init.scm` sets it to `macro-expand-all`, which recursively expands macros in the form tree.
