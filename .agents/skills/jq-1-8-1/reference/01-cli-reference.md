# CLI Reference

## Invocation

```bash
jq [options] <filter> [file...]
jq [options] [<args>] -- from-file <filename> [file...]
jq [options] --from-file <filename> [<args>] [file...]
```

If no input files are given, jq reads from standard input. The filter argument is a jq expression (usually single-quoted to protect shell metacharacters).

## Input Options

**`--null-input` / `-n`**: Don't read any input. Run the filter once with `null` as input. Useful for constructing JSON from scratch or using jq as a calculator.

```bash
jq -n '{pi: 3.14159}'
```

**`--raw-input` / `-R`**: Don't parse input as JSON. Each line of text is passed to the filter as a string. Combined with `--slurp`, the entire input becomes one long string.

```bash
echo "hello world" | jq -R 'split(" ")'
# ["hello","world"]
```

**`--slurp` / `-s`**: Read the entire input stream into a large array and run the filter once. Without `-s`, the filter runs for each JSON value in the input.

```bash
echo '{"x":1} {"x":2}' | jq -s 'add'
# {"x":3}
```

**`--stream`**: Parse input in streaming fashion, outputting `[path, leaf-value]` arrays. Useful for processing very large JSON files that don't fit in memory. Combined with `reduce` or `foreach` to incrementally process data.

```bash
jq --stream '[.[0], .[1]]' huge-file.json
```

**`--stream-errors`**: Like `--stream` but invalid JSON yields error arrays. Implies `--stream`.

**`--seq`**: Use the `application/json-seq` MIME type scheme. ASCII RS character before each output value, LF after. Input parse failures are ignored (with warning).

## Output Options

**`--compact-output` / `-c`**: Compact output — each JSON object on a single line. Essential for piping to other tools.

```bash
echo '[1,2,3]' | jq -c '.[]'
# 1
# 2
# 3
```

**`--raw-output` / `-r`**: If the filter result is a string, print it directly without JSON quotes. Useful for talking to non-JSON systems.

```bash
echo '{"msg":"hello"}' | jq -r '.msg'
# hello
```

**`--raw-output0`**: Like `-r` but prints NUL byte instead of newline after each output. Safe for values containing newlines. Works with `xargs -0`.

```bash
jq -n --raw-output0 '"a b c","d\ne\nf"' | xargs -0 -n1 printf '[%s]\n'
```

**`--join-output` / `-j`**: Like `-r` but no newline after each output.

**`--ascii-output` / `-a`**: Force pure ASCII output — every non-ASCII character replaced with `\uXXXX` escape.

**`--sort-keys` / `-S`**: Output object keys in sorted order. Useful for deterministic/diffable output.

**`--tab`**: Use tab for indentation instead of two spaces.

**`--indent n`**: Use given number of spaces (0–7) for indentation. `--indent 0` produces no indentation but keeps newlines.

```bash
jq --indent 0 '.' <<< '{"foo":["hello","world"]}'
# {
# "foo": [
# "hello",
# "world"
# ]
# }
```

## Color Options

**`--color-output` / `-C`**: Force colored output even when writing to a pipe or file.

**`--monochrome-output` / `-M`**: Disable color output.

When the `NO_COLOR` environment variable is set (non-empty), jq disables color by default. Override with `-C`.

Colors are configurable via `JQ_COLORS` environment variable — a colon-separated list of ANSI escape sequences for different value types. Supports truecolor escapes (`38;2;R;G;B`).

## Argument Passing

**`--arg name value`**: Pass a string argument as `$name` in the program. Value is always a string.

```bash
jq -n --arg name Alice --arg age 30 '{name: $name, age: ($age | tonumber)}'
```

Named arguments are also available as `$ARGS.named`.

**`--argjson name json-text`**: Pass a JSON-encoded value. Unlike `--arg`, the value is parsed as JSON.

```bash
jq -n --argjson count 42 '$count'
# 42
```

**`--slurpfile variable-name filename`**: Read all JSON texts from a file into an array bound to `$variable-name`.

```bash
jq -n --slurpfile config settings.json '$config[0].port'
```

**`--rawfile variable-name filename`**: Read a file's raw content into a string bound to `$variable-name`.

**`--args`**: Remaining arguments are positional strings, available as `$ARGS.positional[]`.

**`--jsonargs`**: Remaining arguments are parsed as JSON texts, available as `$ARGS.positional[]`.

## Other Options

**`-f filename` / `--from-file filename`**: Read the filter from a file instead of the command line.

**`-L directory` / `--library-path directory`**: Prepend directory to the module search path. If used, no builtin search list is applied.

**`--exit-status` / `-e`**: Sets exit code based on last output: 0 if neither `false` nor `null`, 1 if `false` or `null`, 4 if no output produced.

```bash
jq -ne 'true' ; echo $?   # 0
jq -ne 'false' ; echo $?  # 1
jq -ne 'empty' ; echo $?  # 4
```

**`--unbuffered`**: Flush output after each JSON object. Useful for slow data sources piped through jq.

**`--binary` / `-b`**: On Windows, use LF instead of CRLF line endings. For WSL/MSYS2/Cygwin users with native jq.exe.

**`--version` / `-V`**: Output version and exit.

**`--build-configuration`**: Output build configuration and exit.

**`--help` / `-h`**: Show help and exit.

**`--`**: Terminate option processing. Remaining arguments are not interpreted as flags.

**`--run-tests [filename]`**: Run tests from file or stdin. Must be the last option.

## Shell Quoting Rules

- **Unix shells**: Always single-quote the jq program to protect metacharacters: `jq '.["foo"]'`
- **Powershell**: Single-quote the program, escape inner double quotes: `jq '.[\"foo\"]'`
- **Windows cmd.exe**: Double-quote the program, escape inner double quotes: `jq ".[\"foo\"]"`

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Program ran successfully (or last output was truthy with `-e`) |
| 1 | Last output was `false` or `null` (with `-e`) |
| 2 | Usage problem or system error |
| 3 | jq program compile error |
| 4 | No valid result produced (with `-e`) |
