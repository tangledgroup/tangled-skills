# Output Formatting

## Overview

All `gh` commands that produce list or view output support three formatting modes: human-readable (default), JSON (`--json`), jq filtering (`--jq`), and Go templates (`--template`).

## JSON Output

Use `--json` with a comma-separated list of field names to get structured output:

```bash
# List PRs as JSON
gh pr list --json number,title,author

# Output includes nested objects
gh pr list --json number,title,author
[
  {
    "number": 123,
    "title": "A helpful contribution",
    "author": { "login": "monalisa" }
  }
]
```

Each command documents its available JSON fields. Use `--json` without arguments to see all available fields for that command.

## jq Filtering

Pipe JSON output through jq syntax with `--jq`:

```bash
# Extract specific nested fields
gh pr list --json author --jq '.[].author.login'

# Filter and transform
gh issue list --json number,title,labels --jq '
  map(select((.labels | length) > 0))
  | map(.labels = (.labels | map(.name)))
  | .[:3]
'
```

The `--jq` flag requires `--json` to be set (implicitly or explicitly).

## Go Templates

Use `--template` with Go template syntax for custom formatting:

```bash
# Simple range over results
gh issue list --json title,url --template '
  {{range .}}{{hyperlink .url .title}}{{"\n"}}{{end}}
'

# Table output with helper functions
gh pr list --json number,title,headRefName,updatedAt --template '
  {{range .}}
  {{tablerow (printf "#%v" .number | autocolor "green") .title .headRefName (timeago .updatedAt)}}
  {{end}}
'
```

## Template Helper Functions

`gh` provides several built-in template functions:

**Formatting helpers:**
- `autocolor` — apply automatic color based on value
- `color <style> <input>` — apply specific color style
- `join <sep> <list>` — join list elements with separator
- `pluck <field> <list>` — extract a field from each item in a list
- `tablerow <fields>...` — output a table row
- `tablerender` — finalize and render the table
- `timeago <time>` — format timestamp as relative time
- `timefmt <format> <time>` — format timestamp with Go time format
- `truncate <length> <input>` — truncate string to length
- `hyperlink <url> <text>` — create terminal hyperlink

**String helpers:**
- `contains <arg> <string>` — check if string contains substring
- `hasPrefix <prefix> <string>` — check string prefix
- `hasSuffix <suffix> <string>` — check string suffix
- `regexMatch <regex> <string>` — regex pattern matching

## Combining Formatters

`--jq` and `--template` can be combined with `--json`:

```bash
gh pr view 3519 --json number,title,body,reviews,assignees --template '
{{printf "#%v" .number}} {{.title}}
{{.body}}
{{tablerow "ASSIGNEE" "NAME"}}
{{range .assignees}}{{tablerow .login .name}}{{end}}
{{tablerender}}
{{tablerow "REVIEWER" "STATE"}}
{{range .reviews}}{{tablerow .author.login .state}}{{end}}
{{tablerender}}
'
```

## No-Browser Flag

Many commands that open the browser support `--no-browser` or `-n` to print the URL instead:

```bash
gh browse --no-browser
gh issue view 123 --web --no-browser
```

## Color and Terminal Settings

Control color output with environment variables:

```bash
# Disable colors
export NO_COLOR=1

# Force colors even without TTY
export CLICOLOR_FORCE=1

# Enable accessible color palette
gh config set accessible_colors enabled
```
