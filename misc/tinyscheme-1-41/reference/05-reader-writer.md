# Reader & Writer

## Contents
- Token Types
- The Lexer (token)
- Atom Reading
- String Reader State Machine
- List and Vector Reading
- Quasiquote Reading
- Sharp Constants
- Printing System

## Token Types

```c
#define TOK_EOF         (-1)
#define TOK_LPAREN       0   /* ( */
#define TOK_RPAREN       1   /* ) */
#define TOK_DOT          2   /* . (dotted pair) */
#define TOK_ATOM         3   /* identifier or number */
#define TOK_QUOTE        4   /* ' */
#define TOK_COMMENT      5   /* ; */
#define TOK_DQUOTE       6   /* " */
#define TOK_BQUOTE       7   /* ` (backquote) */
#define TOK_COMMA        8   /* , (unquote) */
#define TOK_ATMARK       9   /* ,@ (unquote-splicing) */
#define TOK_SHARP        10  /* # (unknown sharp expression) */
#define TOK_SHARP_CONST  11  /* #t, #f, #x, #o, #b, #d, #\ */
#define TOK_VEC          12  /* #( (vector) */
```

Delimiters: `"()\";\f\t\v\n\r "`

## The Lexer (token)

```c
static int token(scheme *sc) {
    int c = skipspace(sc);
    if (c == EOF) return TOK_EOF;
    switch (c = inchar(sc)) {
    case '(':  return TOK_LPAREN;
    case ')':  return TOK_RPAREN;
    case '.':
        c = inchar(sc);
        if (is_one_of(" \n\t", c)) return TOK_DOT;
        backchar(sc, c); backchar(sc, '.');
        return TOK_ATOM;          /* .5 is an atom, not a dot */
    case '\'': return TOK_QUOTE;
    case ';':  /* skip to end of line, then recurse */
        while ((c = inchar(sc)) != '\n' && c != EOF);
        return token(sc);
    case '"':  return TOK_DQUOTE;
    case '`':  return TOK_BQUOTE;
    case ',':
        if ((c = inchar(sc)) == '@') return TOK_ATMARK;
        backchar(sc, c);
        return TOK_COMMA;
    case '#':
        c = inchar(sc);
        if (c == '(') return TOK_VEC;
        if (c == '!') { /* #! comment — skip to EOL */ ... }
        backchar(sc, c);
        if (is_one_of(" tfodxb\\", c)) return TOK_SHARP_CONST;
        return TOK_SHARP;
    default:
        backchar(sc, c);
        return TOK_ATOM;
    }
}
```

`skipspace()` advances past whitespace while tracking line numbers for error reporting (`SHOW_ERROR_LINE`). Comments starting with `;` or `#!` are consumed by the lexer and produce no tokens.

## Atom Reading

Atoms are read as raw strings then parsed:

```c
static pointer mk_atom(scheme *sc, char *q) {
    /* Handle :: qualified names (colon hook) */
    if ((p = strstr(q, "::")) != 0) {
        /* Transform to (*colon-hook* 'symbol qualifier) */
    }

    /* Parse number or symbol */
    p = q; c = *p++;
    if ((c == '+') || (c == '-')) {
        c = *p++;
        if (!isdigit(c)) return mk_symbol(sc, strlwr(q));
    } else if (c == '.') {
        /* .5 style — has decimal point */
    } else if (!isdigit(c)) {
        return mk_symbol(sc, strlwr(q));  /* Not a number → symbol */
    }

    /* Scan rest of string for digits, '.', 'e'/'E' exponent */
    /* If any non-digit found (besides . or e), it's a symbol */
    /* Return mk_real() if decimal point present, mk_integer() otherwise */
}
```

Number parsing handles: optional sign, integer digits, optional decimal point, optional `e`/`E` exponent. Anything else makes it a symbol. All symbols are lowercased (`strlwr`) per R5RS case-insensitivity.

## String Reader State Machine

Strings use a hand-written state machine in `readstrexp()`:

```c
enum { st_ok, st_bsl, st_x1, st_x2, st_oct1, st_oct2 } state = st_ok;
```

State transitions:

- **st_ok** → normal character accumulation
  - `\` → **st_bsl** (backslash escape)
  - `"` → end of string, return
  - anything else → accumulate

- **st_bsl** → after backslash
  - `0`-`7` → **st_oct1** (start octal escape)
  - `x`/`X` → **st_x1** (start hex escape)
  - `n`/`t`/`r`/`"`/`\` → emit special char, back to **st_ok**
  - anything else → emit literal, back to **st_ok**

- **st_x1** → first hex digit
  - valid hex → **st_x2** (need second digit)
  - invalid → error

- **st_x2** → second hex digit
  - valid hex → emit character, back to **st_ok**
  - invalid → error

- **st_oct1** → first octal digit
  - `0`-`7` → **st_oct2**
  - other → emit first digit as char, push back current

- **st_oct2** → second octal digit
  - `0`-`7` and value < 32 → emit combined octal
  - `0`-`7` and value >= 32 → error
  - other → emit first digit, push back

Supports: `\n`, `\t`, `\r`, `\"`, `\\`, `\xDD` (hex), `\DDD` (octal up to 2 digits).

## List and Vector Reading

List reading uses the opcode chain OP_RDSEXPR → OP_RDLIST → OP_RDDOT:

```c
case OP_RDSEXPR:
    switch (sc->tok) {
    case TOK_LPAREN:
        sc->tok = token(sc);
        if (sc->tok == TOK_RPAREN) s_return(sc, sc->NIL);
        sc->nesting_stack[sc->file_i]++;
        s_save(sc, OP_RDLIST, sc->NIL, sc->NIL);
        s_goto(sc, OP_RDSEXPR);

    case TOK_ATOM:
        s_return(sc, mk_atom(sc, readstr_upto(sc, DELIMITERS)));

    case TOK_DQUOTE:
        x = readstrexp(sc);
        setimmutable(x);
        s_return(sc, x);

    /* ... other token types ... */
    }

case OP_RDLIST:
    sc->args = cons(sc, sc->value, sc->args);  /* Collect element */
    sc->tok = token(sc);
    if (sc->tok == TOK_RPAREN) {
        sc->nesting_stack[sc->file_i]--;
        s_return(sc, reverse_in_place(sc, sc->NIL, sc->args));
    } else if (sc->tok == TOK_DOT) {
        s_save(sc, OP_RDDOT, sc->args, sc->NIL);
        s_goto(sc, OP_RDSEXPR);
    } else {
        s_save(sc, OP_RDLIST, sc->args, sc->NIL);
        s_goto(sc, OP_RDSEXPR);
    }

case OP_RDDOT:
    if (token(sc) != TOK_RPAREN) Error_0(sc, "illegal dot expression");
    sc->nesting_stack[sc->file_i]--;
    s_return(sc, reverse_in_place(sc, sc->value, sc->args));
```

Elements are collected in reverse order (cons to front), then reversed at the end. Dotted pairs `(a b . c)` collect `a` and `b`, then use `c` as the cdr terminator instead of NIL.

Nesting is tracked via `nesting_stack[file_i]` — incremented on `(`, decremented on `)`. Mismatched parentheses are detected at the start of OP_EXE_5.

## Quasiquote Reading

Quasiquoting is handled at read time by wrapping forms in special symbols:

```c
case TOK_BQUOTE:
    s_save(sc, OP_RDQQUOTE, sc->NIL, sc->NIL);
    s_goto(sc, OP_RDSEXPR);

case OP_RDQQUOTE:
    s_return(sc, cons(sc, sc->QQUOTE, cons(sc, sc->value, sc->NIL)));

case TOK_COMMA:
    s_save(sc, OP_RDUNQUOTE, sc->NIL, sc->NIL);
    s_goto(sc, OP_RDSEXPR);

case OP_RDUNQUOTE:
    s_return(sc, cons(sc, sc->UNQUOTE, cons(sc, sc->value, sc->NIL)));

case TOK_ATMARK:
    s_save(sc, OP_RDUQTSP, sc->NIL, sc->NIL);
    s_goto(sc, OP_RDSEXPR);

case OP_RDUQTSP:
    s_return(sc, cons(sc, sc->UNQUOTESP, cons(sc, sc->value, sc->NIL)));
```

So `` `(a ,b ,@c) `` reads as:
```
(quasiquote (a (unquote b) (unquote-splicing c)))
```

The actual expansion is handled by Scheme-level code in `init.scm`, not the reader.

## Sharp Constants

`mk_sharp_const()` handles `#t`, `#f`, `#o...`, `#d...`, `#x...`, `#b...`, `#\...`:

```c
static pointer mk_sharp_const(scheme *sc, char *name) {
    if (!strcmp(name, "t")) return sc->T;
    if (!strcmp(name, "f")) return sc->F;
    if (*name == 'o') { /* octal */ sscanf("0%s", name+1); return mk_integer(); }
    if (*name == 'd') { /* decimal */ return mk_integer(); }
    if (*name == 'x') { /* hex */ sscanf("0x%s", name+1); return mk_integer(); }
    if (*name == 'b') { /* binary */ return mk_integer(binary_decode(name+1)); }
    if (*name == '\\') { /* character literal */
        if (strcmp(name+1, "space") == 0) c = ' ';
        else if (strcmp(name+1, "newline") == 0) c = '\n';
        else if (name[1] == 'x') sscanf hex;
        else if (is_ascii_name(name+1, &c)); /* #\nul, #\esc, etc. */
        else if (name[2] == 0) c = name[1];   /* #\a → 'a' */
        return mk_character(sc, c);
    }
    return sc->NIL;
}
```

Unknown sharp expressions invoke `*sharp-hook*` if defined, allowing user-defined reader extensions.

## Printing System

### atom2str — Convert cell to string representation

```c
static void atom2str(scheme *sc, pointer l, int f, char **pp, int *plen) {
    if (l == sc->NIL)          p = "()";
    else if (l == sc->T)       p = "#t";
    else if (l == sc->F)       p = "#f";
    else if (l == sc->EOF_OBJ) p = "#<EOF>";
    else if (is_port(l))       p = "#<PORT>";
    else if (is_number(l))     /* format with optional radix f */
    else if (is_string(l))     p = strvalue(l);  /* raw content, not quoted */
    else if (is_character(l))  /* #\space, #\newline, #\\x20, or literal char */
    else if (is_symbol(l))     p = symname(l);
    else if (is_proc(l))       snprintf("#<%s PROCEDURE %ld>", procname(l), procnum(l));
    else if (is_closure(l))    p = "#<CLOSURE>";
    else if (is_foreign(l))    snprintf("#<FOREIGN PROCEDURE %ld>", procnum(l));
    else if (is_continuation(l)) p = "#<CONTINUATION>";
}
```

The `f` parameter controls number radix: 0/1 = default, 2 = binary, 8 = octal, 10 = decimal, 16 = hex.

### OP_P0LIST / OP_P1LIST — Recursive S-expression printing

```c
case OP_P0LIST:
    if (is_vector(sc->args)) {
        putstr(sc, "#(");
        s_goto(sc, OP_PVECFROM);
    } else if (!is_pair(sc->args)) {
        printatom(sc, sc->args, sc->print_flag);
        s_return(sc, sc->T);
    } else if (car == QUOTE && ok_abbrev(cdr)) {
        putstr(sc, "'");
        sc->args = cadr(sc->args);
        s_goto(sc, OP_P0LIST);  /* Print '(a b) as shorthand */
    } else {
        putstr(sc, "(");
        s_save(sc, OP_P1LIST, cdr(sc->args), sc->NIL);
        sc->args = car(sc->args);
        s_goto(sc, OP_P0LIST);
    }

case OP_P1LIST:
    if (is_pair(sc->args)) {
        putstr(sc, " ");
        s_save(sc, OP_P1LIST, cdr(sc->args), sc->NIL);
        sc->args = car(sc->args);
        s_goto(sc, OP_P0LIST);
    } else if (sc->args != sc->NIL) {
        putstr(sc, " . ");
        printatom(sc, sc->args, sc->print_flag);
    }
    putstr(sc, ")");
    s_return(sc, sc->T);
```

`ok_abbrev(x)` checks if `x` is `(symbol . NIL)`, enabling `'` shorthand for quoted lists. Dotted pairs print as `(a b . c)`. Vectors print as `#(a b c)`.

### write vs display

`sc->print_flag = 1` (write mode): strings are printed with quotes and escapes, symbols are quoted.
`sc->print_flag = 0` (display mode): strings are printed raw, no quoting.
