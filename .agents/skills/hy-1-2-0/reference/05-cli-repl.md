# CLI Tools & REPL

## Contents
- hy command
- hy2py translator
- hyc compiler
- REPL class and configuration
- Environment variables

## hy Command

`hy` imitates the `python` command. Without arguments, launches REPL if stdin is TTY, runs stdin as script otherwise.

```bash
hy                          ; REPL (if TTY) or run stdin
hy myprogram.hy             ; run file
hy -c "(+ 1 2)"             ; run code string
hy -m my.module             ; run module (name is mangled)
echo "(- 5 3)" | hy         ; pipe input
```

**Hy-specific options:**
- `--spy`: Print equivalent Python before executing each REPL form
- `--repl-output-fn NAME`: Set output function (`repr` for Python repr, or dotted name like `foo.bar.baz`)

Standard Python options apply: `-O`, `-u`, `-W`, etc. See `hy --help`.

## hy2py Translator

Convert Hy source to Python source. Can execute arbitrary code via macros — don't give it untrusted input.

```bash
hy2py myfile.hy             ; output to stdout
echo "(- 5 3)" | hy2py      ; pipe input
hy2py -o outdir/ mymodule   ; module → folder
hy2py -o out.py myfile.hy   ; file → specific output
```

Output still imports `hy` (see implicit names). To get pure Python, remove the import manually if your code doesn't use Hy-specific features.

## hyc Compiler

Pre-compile Hy source to Python bytecode:

```bash
hyc myfile.hy               ; compile to .pyc
hyc --help
```

Bytecode placement follows `importlib.util.cache_from_source()`. Can execute arbitrary code via macros — don't give it untrusted input.

## REPL Class and Configuration

**`hy.REPL`**: Subclass of `code.InteractiveConsole`. Start programmatically:

```hy
(hy.REPL.run)               ; basic REPL
(.run (hy.REPL :locals {#** (globals) #** (locals)}))  ; with local scope
```

From Python:
```python
import hy
hy.REPL(locals={**globals(), **locals()}).run()
```

Changes to local variables inside REPL are not propagated back.

**Output functions**: Default is `hy.repr` (Hy syntax). Use `--repl-output-fn=repr` for Python repr. No output when value is `None`.

**Special variables**:
- `*1` — result of most recent input (like `_` in Python REPL)
- `*2` — second most recent
- `*3` — third most recent
- `*e` — most recent uncaught exception

## Startup Files

Set `HYSTARTUP` env var to path of Hy file executed on REPL start. Special variables available:

```hy
(setv
  repl-spy True              ; print Python equivalent
  repl-output-fn pformat     ; custom output function
  repl-ps1 "=> "             ; primary prompt
  repl-ps2 "... "            ; continuation prompt)
```

Full example startup file:

```hy
(eval-and-compile
  (import sys os)
  (sys.path.append "~/my-libs"))

(import re json pathlib [Path] hy.pyops *)
(require hyrule [unless])

(setv
  repl-spy True
  repl-output-fn pformat
  repl-ps1 "\x01\x1b[0;32m\x02=> \x01\x1b[0m\x02"
  repl-ps2 "\x01\x1b[0;31m\x02... \x01\x1b[0m\x02")
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HYSTARTUP` | nothing | Path to Hy startup file for REPL |
| `HY_HISTORY` | `~/.hy-history` | Path to save REPL input history |
| `HY_SHOW_INTERNAL_ERRORS` | false | Show internal Hy traceback parts |
| `HY_MESSAGE_WHEN_COMPILING` | false | Print "Compiling FILENAME" on each compile |

Boolean variables: empty string = false, any other value = true.
