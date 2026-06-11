# Advanced Features

## Variable Binding: `expr as $identifier | ...`

Bind the output(s) of an expression to a variable. Variables are prefixed with `$`.

```bash
echo '{"name":"Alice","age":30}' | jq '.name as $n | .age as $a | "\($n) is \($a)"'
# "Alice is 30"
```

Multiple bindings:

```bash
jq -n '1 as $x | 2 as $y | {$x, $y}'
# {1: null, 2: null}
```

## Destructuring

Destructure arrays and objects directly in binding patterns:

```bash
echo '[1,2,3]' | jq '[., "tag"] as [$head, $rest] | $head'
# 1
```

Object destructuring:

```bash
echo '{"name":"Alice","age":30}' | jq '{name, age} as {$name, $age} | "\($name): \($age)"'
# "Alice: 30"
```

## Defining Functions

**`def`**: Define reusable functions. Functions can take parameters using pipe syntax.

```bash
jq -n 'def double: . * 2; 5 | double'
# 10
```

Functions with named parameters use the pipe:

```bash
jq -n 'def add($x; $y): $x + $y; add(3; 4)'
# 7
```

Multi-parameter functions chain pipes:

```bash
jq -n 'def max3: input as $b | input as $c | [., $b, $c] | max;' \
  --slurp '[1,3,2]' '.[]'
```

## Scoping

Variables and function definitions have scope. `def` inside a filter is local to that filter's context.

## reduce

Iterate over a generator with an accumulator:

```
reduce generator as $var (initial_state; update_expr)
```

```bash
echo '[1,2,3,4,5]' | jq 'reduce .[] as $x (0; . + $x)'
# 15
```

With select in update (1.8+ preserves state across select):

```bash
jq -n 'reduce range(5) as $x (0; . + $x | select($x != 2))'
# 8
```

## foreach

Like `reduce` but emits intermediate states:

```
foreach generator as $var (initial_state; update_expr; output_expr)
```

```bash
jq -n '[1,2,3] | foreach .[] as $x (0; . + $x; {running_total: ., item: $x})'
# {"running_total":1,"item":1}
# {"running_total":3,"item":2}
# {"running_total":6,"item":3}
```

Multiple init values (1.8+):

```bash
jq -n '[1,2] | foreach .[] as $x (0, 1; . + $x)'
# 1
# 3
# 2
# 4
```

## isempty

Test if an expression produces no output: `isempty(expr)` returns `true` if expr produces nothing.

```bash
jq -n 'isempty(empty)'
# true
jq -n 'isempty(1)'
# false
```

## first, last, nth

**`first(expr)`**: Get the first output of a generator.

**`last(expr)`**: Get the last output. `last(empty)` produces no output (1.8+).

**`nth(n; expr)`**: Get the nth (zero-based) output.

```bash
echo '[10,20,30,40]' | jq 'first(.[])'
# 10
echo '[10,20,30,40]' | jq 'last(.[])'
# 40
echo '[10,20,30,40]' | jq 'nth(2; .[])'
# 30
```

## Generators and Iterators

In jq, any expression that can produce multiple outputs is a generator. Key generators:

- `.[]` — iterate array/object
- `range(n)` / `range(from; to)` / `range(from; to; step)` — number sequences
- `recurse(f)` — recursive descent
- Comma operator `,` — produces multiple values
- `repeat(expr)` — infinite repetition (use with `limit`)

```bash
jq -n '[range(3)]'
# [0,1,2]

jq -n '[range(2; 6; 2)]'
# [2,4]
```

## Assignment Operators

**Update-assignment `|=`**: Update a value in place.

```bash
echo '{"a":1}' | jq '.a |= . + 1'
# {"a":2}
```

**Arithmetic update-assignment**: `+=`, `-=`, `*=`, `/=`, `%=`

```bash
echo '{"count":5}' | jq '.count += 3'
# {"count":8}
```

**Alternative update-assignment `//=`**: Update only if current value is `false` or `null`.

**Plain assignment `=`**: Set a value (1.5+).

```bash
echo '{"a":1}' | jq '.b = 2'
# {"a":1,"b":2}
```

Complex assignments with paths:

```bash
echo '[]' | jq '.[5] = "hello"'
# [null,null,null,null,null,"hello"]
```

## Breaking Out of Control Structures

Use `halt` and `halt_error` to stop execution. Use `limit` to bound generators. `empty` suppresses output within a generator context.

## Error Suppression: `?`

The `?` suffix suppresses errors, producing no output on failure. Equivalent to `try . catch empty`.

```bash
echo '[]' | jq '.[5]?'
# (no output)
```

Can be placed on any filter: `.foo.bar?` suppresses errors from the entire chain.
