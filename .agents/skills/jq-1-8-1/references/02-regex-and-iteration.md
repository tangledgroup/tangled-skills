# Regular Expressions and Iteration

## Regular Expression Functions

### test() — Does String Match?

```bash
echo '"hello123"' | jq 'test("[0-9]+")'              # true
echo '"abc"' | jq 'test("[0-9]+")'                    # false
```

### match() — Extract Match Information

```bash
# Returns object with string, offset, captures
echo '"hello123world456"' | jq '[match("[0-9]+").string]'
# ["123"]

echo '"abc123def"' | jq 'match("(?<letters>[a-z]+)(?<digits>[0-9]+)")'
# {"string":"abc123","offset":0,"captures":[...]}
```

### capture() — Extract Named Groups as Object

```bash
echo '"user=alice,role=admin"' \
  | jq 'capture("user=(?<u>[a-z]+),role=(?<r>[a-z]+)")'
# {"u":"alice","r":"admin"}
```

### scan() — Find All Matches

```bash
echo '"abc123def456"' | jq '[scan("[a-z]+")]'
# ["abc", "def"]

echo '"a1b2c3"' | jq '[scan("[0-9]")]'
# ["1", "2", "3"]
```

### sub() / gsub() — Substitution

```bash
# gsub — global replacement (all occurrences)
echo '"hello world"' | jq 'gsub("o"; "0")'           # "hell0 w0rld"

# sub — first match only
echo '"hello world"' | jq 'sub("o"; "0")'            # "hell0 world"
```

### split() / splits()

```bash
# split() — returns array of substrings
echo '"a,b,c"' | jq 'split(",")'                      # ["a","b","c"]

# splits() — iterator (produces multiple outputs)
echo '"a,,b,,c"' | jq 'splits(",")'                    # "a", "", "b", "", "c"
```

## Generators and Iteration

### range()

```bash
# range(end) — 0 to end-1
echo 'null' | jq -n '[range(5)]'                       # [0, 1, 2, 3, 4]

# range(start;end)
echo 'null' | jq -n '[range(2;6)]'                     # [2, 3, 4, 5]

# range(start;end;step)
echo 'null' | jq -n '[range(0;10;3)]'                  # [0, 3, 6, 9]
```

### repeat() — Infinite Generator

```bash
# Generate repeating values (must be bounded with limit/skip/first/last)
echo 'null' | jq -n '[limit(5; repeat(1))]'            # [1, 1, 1, 1, 1]
echo 'null' | jq -n '[repeat("x")[:3]]'               # ["x", "x", "x"]
```

### until() — Loop Until Condition

```bash
# Fibonacci: keep adding until first element exceeds 10
echo 'null' | jq -n '[1,0] | until(.[0] > 10; [.[0]+1, .[1]+.[0]]) | .[1]'
# Result: sums accumulated while condition is false

# Simple countdown
echo '5' | jq 'until(. <= 0; . - 1)'                   # 0
```

### while() — Loop While Condition True

```bash
# Countdown with intermediate results
echo 'null' | jq -n '[5, 0] | while(. > 0; [.[0]-1, .[1]+1])'
# [[4,1],[3,2],[2,3],[1,4],[0,5]]
```

### recurse() — Recursive Descent

```bash
# Walk all descendants of an object
echo '{"a":{"b":1,"c":{"d":2}}}' | jq '[recurse(.[]?)]'
# [{"a":{"b":1,"c":{"d":2}}},{"b":1,"c":{"d":2}},{"d":2},1,2]

# Only recurse into objects
echo '{"a":{"b":1},"c":{"d":{"e":2}}}' | jq '[recurse(.[]? | select(type == "object"))]'
```

### walk() — Recursive Transform

```bash
# Sort all arrays in a nested structure
echo '{"a":[3,1,2],"b":{"c":[5,4]}}' \
  | jq 'walk(if type == "array" then sort else . end)'
# {"a":[1,2,3],"b":{"c":[4,5]}}

# Convert all string numbers to actual numbers
echo '{"a":"1","b":"2"}' | jq 'walk(if type == "string" and test("^[0-9]+$") then tonumber else . end)'
```

### limit() / skip() / first() / last()

```bash
# Limit output to N results
echo '[1,2,3,4,5]' | jq '[.[] | limit(3; .)]'         # [1, 2, 3]
echo '[1,2,3,4,5]' | jq '[skip(2); .[]]'              # [3, 4, 5]

# first() / last() from generator
echo 'null' | jq -n '[first(range(100))]'              # [0]
echo 'null' | jq -n '[last(range(100))]'               # [99]

# nth(index) — get element at index
echo 'null' | jq -n '[nth(5; range(10))]'              # [5]
```

## Reduce and Foreach

### reduce() — Fold/Reduce

```bash
# Sum array elements
echo '[1,2,3,4,5]' | jq 'reduce .[] as $x (0; . + $x)'   # 15

# Build object from array
echo '[{"k":"a","v":1},{"k":"b","v":2}]' \
  | jq 'reduce .[] as $item ({}; .[$item.k] = $item.v)'
# {"a":1,"b":2}

# Count occurrences
echo '["a","b","a","c","b","a"]' \
  | jq 'reduce .[] as $x ({}; .[$x] += 1)'
# {"a":3,"b":2,"c":1}
```

### foreach() — Streaming Reduction

```bash
# Running sum with intermediate results
echo '[1,2,3,4,5]' | jq 'foreach .[] as $x ([0]; . + [$x])'

# Process items one at a time without buffering all results
```

## SQL-Style Operators (jq 1.6+)

```bash
# IN operator
echo '{"a":1}' | jq '.a | in([1,2,3])'              # true

# BETWEEN equivalent
echo '5' | jq '(. >= 1 and . <= 10)'                  # true

# IS NULL / IS NOT NULL
echo 'null' | jq 'if . == null then "is null" else "not null" end'
```
