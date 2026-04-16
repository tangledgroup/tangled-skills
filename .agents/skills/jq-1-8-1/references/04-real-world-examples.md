# Real-World Examples and Recipes

## Working with API Responses

### GitHub API Examples

```bash
# Get repo name and star count from GitHub API
curl -s 'https://api.github.com/repos/jqlang/jq' \
  | jq '{name: .name, stars: .stargazers_count, language: .language}'

# List all commit authors (last 30)
curl -s 'https://api.github.com/repos/jqlang/jq/commits?per_page=30' \
  | jq '[.[] | {author: .commit.author.name, date: .commit.author.date}]'

# Extract specific fields from search results
curl -s 'https://api.github.com/search/repositories?q=jq&sort=stars&per_page=5' \
  | jq '.items[] | {name: .full_name, stars: .stargazers_count, url: .html_url}'

# Get issues with labels
curl -s 'https://api.github.com/repos/jqlang/jq/issues?state=open&per_page=10' \
  | jq '[.[] | select(.labels | map(.name) | index("bug"))] | length'
```

### Generic API Pattern

```bash
# Paginated API with cursor/offset
curl -s 'https://api.example.com/items?page=1&limit=50' \
  | jq '.items[] | {id, name, created_at}'

# Nested response extraction
curl -s 'https://api.example.com/users/123' \
  | jq '{user: .data.user.name, email: .data.user.email, plan: .data.subscription.plan}'

# Filter by condition
curl -s 'https://api.example.com/products' \
  | jq '[.[] | select(.price < 100 and .in_stock == true)]'
```

## Data Transformation Pipelines

### CSV-like JSON to Records

```bash
# Transform array of arrays to objects with headers as keys
echo '[["name","age"],["Alice",30],["Bob",25]]' \
  | jq '(.[0] as $headers | .[1:] | map(
      reduce range($headers|length) as $i ({}; . + {($headers[$i]): .[$i]}))
    )'
# [{"name":"Alice","age":30},{"name":"Bob","age":25}]
```

### Flatten Nested Arrays

```bash
echo '[[1,2],[3,4],[5,6]]' | jq 'flatten'                    # [1, 2, 3, 4, 5, 6]
echo '[[[1,2]],[[[3,4]]]]' | jq 'flatten(2)'                  # [[1,2],[3,4]]
```

### Group and Aggregate

```bash
# Group by field and compute averages
echo '[{"dept":"eng","sal":80},{"dept":"eng","sal":90},{"dept":"sales","sal":70}]' \
  | jq 'group_by(.dept) | map({dept: .[0].dept, avg_salary: ([.[].sal] | add / length), count: length})'

# Group and collect values
echo '[{"g":"a","v":1},{"g":"b","v":2},{"g":"a","v":3}]' \
  | jq 'group_by(.g) | map({group: .[0].g, values: [.[].v]})'

# Pivot/transpose data
echo '[[1,2],[3,4],[5,6]]' | jq 'transpose'                  # [[1,3,5],[2,4,6]]
```

### Deduplication

```bash
# Deduplicate by field (keep first occurrence)
echo '[{"id":1,"v":"a"},{"id":2,"v":"b"},{"id":1,"v":"c"}]' \
  | jq '[group_by(.id)[] | .[0]]'
# [{"id":1,"v":"a"},{"id":2,"v":"b"}]

# Deduplicate entire objects
echo '[1,2,2,3,3,3]' | jq 'unique'                           # [1, 2, 3]
```

### Merging and Joining

```bash
# Merge two objects
echo '{"a":1}' | jq '. + {"b":2}'                            # {"a":1,"b":2}

# Deep merge (requires recursive function)
def deep_merge(a; b):
  if (a | type) == "object" and (b | type) == "object" then
    reduce (b | keys[]) as $k (a; .[$k] = deep_merge(.[$k]; b[$k]))
  else b end;

echo '{"a":{"x":1,"y":2}}' | jq 'deep_merge({}); input' <<< '{"a":{"y":3,"z":4}}'

# Join arrays by common key (requires slurp)
jq -s '.[0] as $left | .[1] as $right | [$left[] | . + ($right[] | select(.id == .id))] ' left.json right.json
```

## Shell Script Integration

### Extracting Values for Shell Variables

```bash
#!/bin/bash
# Single value from JSON
API_URL="https://api.github.com/repos/jqlang/jq"
STARS=$(curl -s "$API_URL" | jq '.stargazers_count')
echo "jq has $STARS stars"

# Multiple values with raw output
read -r NAME VERSION < <(curl -s 'https://api.github.com/repos/jqlang/jq' \
  | jq -r '[.name, .default_branch] | @sh')

# Process multiple JSON objects from a file
while IFS=$'\t' read -r id name; do
  echo "User $id: $name"
done < <(jq -r '.[] | [.id, .name] | @tsv' users.json)

# Conditional logic with exit status
curl -s 'https://api.github.com/repos/jqlang/jq' | jq -e '.fork == false' \
  && echo "This is the original repo" \
  || echo "This is a fork"
```

### Generating JSON for Other Tools

```bash
# Generate JSON config from shell variables
jq -n \
  --arg host "$DB_HOST" \
  --arg port "$DB_PORT" \
  --arg user "$DB_USER" \
  '{database: {host: $host, port: ($port | tonumber), username: $user}}'

# Generate JSON array for API upload
jq -n '[range(3) | {id: ., name: ("item-\(.)"), active: true}]'

# Build from existing data with transformations
cat users.json | jq '[.[] | select(.active) | {email: .email, role: .role}]' > active_users.json
```

### Log Parsing

```bash
# Parse JSON log entries and extract fields
cat app.log | jq -r 'select(.level == "ERROR") | "[\(.timestamp)] \(.message)"'

# Aggregate log levels
cat app.log | jq -s '[.[] | .level] | group_by(.) | map({level: .[0], count: length})'

# Find unique IPs from access logs
cat access.log | jq -r '.ip' | sort | uniq -c | sort -rn | head -10
```

## JSON Generation

### Building JSON from Scratch

```bash
# Simple object construction with -n (null input)
jq -n '{name: "jq", version: "1.8.1", features: ["filtering","transformation"]}'

# Use --arg for shell variable interpolation
NAME="myapp" VERSION="2.0" jq -n \
  --arg name "$NAME" --arg ver "$VERSION" \
  '{"application": $name, "version": $ver}'

# Generate array of objects
jq -n '[range(5) | {id: ., label: ("item-\(.)")}]'
# [{"id":0,"label":"item-0"},{"id":1,"label":"item-1"},...]

# Build from inputs
echo 'null' | jq -n --slurpfile config config.json '{app: "myapp", config: $config[0]}'
```

### Template-like Patterns

```bash
# Create a structured report
jq -n \
  --arg date "$(date +%Y-%m-%d)" \
  --argjson count 42 \
  --arg status "OK" \
  '{report: {date: $date, summary: {total_items: $count, status: $status}}}'

# Generate HTML from JSON data
jq -r '.[] | "<li>" + .name + "</li>"' items.json | paste -sd '\n' - > list.html
```

## Data Validation

### Schema-like Validation

```bash
# Check required fields exist
echo '{"name":"Alice"}' | jq 'if has("name") and (.name | type) == "string" then "valid" else "missing name" end'

# Validate email format (basic regex check)
echo '"user@example.com"' | jq 'if test("^[^@]+@[^@]+\\.[^@]+$") then "valid email" else "invalid email" end'

# Validate nested structure
echo '{"user":{"email":"test@test.com"}}' \
  | jq 'if (.user | has("email")) and (.user.email | type) == "string" then "valid" else "invalid" end'
```

### Data Quality Checks

```bash
# Find null/missing values in array
echo '[{"a":1},{"b":null},{"c":3}]' | jq '[.[] | select(.a == null or .b == null)]'

# Check for duplicate IDs
echo '[{"id":1},{"id":2},{"id":1}]' | jq 'group_by(.id) | map(select(length > 1))'

# Find out-of-range values
echo '[10, 50, 150, 200]' | jq '[.[] | select(. < 0 or . > 100)]'   # [150, 200]
```

## Common Patterns Cheat Sheet

| Task | jq Expression |
|------|---------------|
| Pretty print | `jq '.'` |
| Extract field | `jq '.field'` |
| Nested field | `jq '.a.b.c'` |
| Array element | `jq '.[0]'` |
| All array elements | `jq '.[]'` |
| Filter array | `jq '[.[] | select(. > 5)]'` |
| Count elements | `jq 'length'` or `jq '[.[]] | length'` |
| Sum values | `jq '[.[].amount] | add'` |
| Group by field | `jq 'group_by(.category)'` |
| Sort array | `jq 'sort'` or `jq 'sort_by(.field)'` |
| Unique values | `jq '[.[] | .field] | unique'` |
| Create object | `jq '{new_key: .old_key}'` |
| Delete field | `jq 'del(.field)'` |
| Add field | `jq '. + {new: "value"}'` |
| Raw output | `jq -r '.field'` |
| Compact output | `jq -c '.'` |
| No input (null) | `jq -n '{key: "value"}'` |
| Pass shell var | `jq --arg x "$VAR" '{val: $x}'` |
| Slurp all input | `jq -s '.'` |
| Read raw lines | `jq -R '.'` |
