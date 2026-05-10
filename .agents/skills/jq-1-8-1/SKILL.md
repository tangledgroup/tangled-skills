---
name: jq-1-8-1
description: Complete toolkit for jq 1.8.1, the lightweight and flexible command-line JSON processor. Use when parsing, transforming, filtering, or generating JSON data from the shell, piping between commands, processing API responses, or writing reusable JSON transformation scripts with a concise declarative query language.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - json
  - cli
  - data-processing
  - transformation
  - shell
category: data-processing
external_references:
  - https://jqlang.org/
  - https://jqlang.org/manual/v1.8/
  - https://jqlang.org/tutorial/
  - https://github.com/jqlang/jq/releases/tag/jq-1.8-1
  - https://play.jqlang.org
---

# jq 1.8.1

## Overview

jq is a lightweight and flexible command-line JSON processor. Written in portable C with zero runtime dependencies, jq lets you slice, filter, map, and transform structured JSON data with the same ease that `sed`, `awk`, `grep`, and friends let you play with text. It's like `sed` for JSON.

A jq program is a **filter**: it takes an input (JSON data) and produces an output. Filters can be combined — piped, collected into arrays, or chained. Some filters produce multiple results, enabling iteration without explicit loops. Every filter has an input and an output, even literals like `"hello"` or `42`.

jq 1.8.1 is a patch release (July 2025) fixing security issues (CVE-2025-49014, GHSA-f946-j5j2-4w5m), performance regressions from 1.8.0, and build portability improvements.

## When to Use

- Parsing and transforming JSON from command-line tools, APIs, or config files
- Extracting specific fields from nested JSON structures
- Filtering arrays and objects by conditions
- Converting between JSON and other formats (CSV-like output, raw text)
- Validating and pretty-printing JSON
- Building shell pipelines that process structured data
- Writing reusable `.jq` module scripts for complex transformations
- Processing large JSON files with streaming (`--stream`)

## Quick Start

```bash
# Pretty-print JSON
echo '{"name":"Alice","age":30}' | jq '.'

# Extract a field
echo '{"name":"Alice","age":30}' | jq '.name'
# "Alice"

# Raw string output (no quotes)
echo '{"name":"Alice"}' | jq -r '.name'
# Alice

# Filter array elements
echo '[1,2,3,4,5]' | jq '[.[] | select(. > 3)]'
# [4, 5]

# Transform objects
echo '[{"id":1,"name":"a"},{"id":2,"name":"b"}]' | jq '.[].name'
# "a"
# "b"

# Use as calculator
jq -n '2.5 * 4 + 10'
# 20
```

## Core Concepts

**Filters**: A jq program is a filter that takes input and produces output. The simplest filter is `.` (identity), which passes input through unchanged.

**Streams**: Data in jq flows as streams of JSON values. Every expression runs for each value in its input stream and can produce any number of output values. Multiple outputs are separated by whitespace — a `cat`-friendly format.

**Piping**: The `|` operator feeds the output of one filter into another: `.name | uppercase`.

**Array construction**: Wrapping a multi-output filter in `[...]` collects all outputs into an array: `[.items[] | .name]`.

**Object construction**: `{key: value}` builds objects. Use `.` to reference the current input: `{name: .firstName, age: .yearsOld}`.

**Null safety**: Accessing missing keys returns `null` rather than erroring. Use `?//` for default values.

## Usage Examples

```bash
# Pass arguments as variables
jq -n --arg name "Alice" --argjson age 30 '{name: $name, age: $age}'

# Read from a file
jq '.items[] | select(.active)' config.json

# Compact output for piping
curl 'https://api.github.com/repos/jqlang/jq' | jq -c '.stargazers_count'

# Sort keys
jq -S '{b: 2, a: 1}'
# {"a":1,"b":2}

# Slurp multiple JSON values into an array
echo '{"x":1} {"x":2}' | jq -s 'add'
# {"x":3}

# String interpolation
jq -n '"Hello, \($name)!"' --arg name World
# "Hello, World!"

# Exit status based on output
jq -e '.status == "ok"' result.json && echo "passed" || echo "failed"
```

## Advanced Topics

**CLI Options and Invocation**: Command-line flags, input/output modes, color configuration → [CLI Reference](reference/01-cli-reference.md)

**Basic Filters and Navigation**: Object/array access, iteration, comma, pipe, recursive descent → [Filters and Navigation](reference/02-filters-navigation.md)

**Built-in Functions**: Type conversion, math, string operations, array/object functions, dates, regex → [Built-in Functions](reference/03-built-in-functions.md)

**Advanced Features**: Variable binding, destructuring, function definition, reduce, foreach, generators → [Advanced Features](reference/04-advanced-features.md)

**Modules and I/O**: Module system, import/include, input/inputs, streaming parser, assignment operators → [Modules and I/O](reference/05-modules-io.md)
