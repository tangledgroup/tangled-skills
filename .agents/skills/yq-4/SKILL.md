---
name: yq-4
description: >-
  A skill for using yq v4.x, a lightweight and portable command-line YAML, JSON,
  XML, INI, Properties, CSV/TSV, HCL, TOML, Base64, and Lua processor with
  jq-like syntax. Use when reading, writing, transforming, or converting data
  between these formats from the terminal, scripts, CI/CD pipelines, or Docker
  containers without needing Python or Node.js dependencies.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "4.53.2"
tags:
  - yaml
  - json
  - xml
  - ini
  - csv
  - tsv
  - hcl
  - toml
  - lua
  - properties
  - base64
  - config
  - data-processing
category: cli-tool
external_references:
  - https://mikefarah.gitbook.io/yq/
  - https://github.com/mikefarah/yq
---

# yq v4.x

## Overview

`yq` is a lightweight and portable command-line YAML processor written in Go. It uses jq-like syntax but works with YAML files as well as JSON, XML, INI, Properties, CSV/TSV, HCL, TOML, Base64, and Lua. It provides a dependency-free binary for any platform, making it ideal for shell scripts, CI/CD pipelines, and containerized environments.

Under the hood, yq uses [go-yaml v3](https://github.com/go-yaml/yaml/tree/v3) as the YAML parser, which supports [YAML spec 1.2](https://yaml.org/spec/1.2/spec.html). In YAML 1.2, `yes`/`no` are strings, not booleans.

## When to Use

- Reading values from YAML, JSON, XML, INI, Properties, CSV, TSV, HCL, TOML, or Lua files
- Updating configuration files in place (`-i`)
- Converting between formats (YAML to JSON, XML to YAML, CSV to YAML, etc.)
- Merging multiple configuration files together
- Processing multi-document YAML files
- Working with front matter in markdown files (Jekyll, Hugo, etc.)
- Splitting documents into separate files
- Validating YAML files
- Comparing YAML files via normalized diff
- Using in CI/CD pipelines, GitHub Actions, or Docker containers

## Quick Reference

```bash
# Read a value
yq '.a.b[0].c' file.yaml

# Pipe from STDIN
yq '.a.b[0].c' < file.yaml

# Update in place
yq -i '.a.b[0].c = "cool"' file.yaml

# Use environment variables
NAME=mike yq -i '.a.b[0].c = strenv(NAME)' file.yaml

# Convert JSON to YAML
yq -Poy sample.json

# Merge two files
yq -n 'load("file1.yaml") * load("file2.yaml")'

# Create from scratch
yq -n '.a.b.c = "cat"' > newfile.yaml

# Validate a YAML file
yq --exit-status 'tag == "!!map" or tag == "!!seq"' file.yaml > /dev/null
```

## Core Concepts

### Expression Model

Expressions are made up of operators and pipes. A context of nodes is passed through the expression, and each operation takes the context as input and returns a new context as output. That output becomes the input for the next operation.

```bash
# Splat array, filter, extract field
yq '.root.items[] | select(.type == "fruit") | .name' file.yaml
```

### Assignment Forms

- **Plain form (`=`)**: RHS expression runs against the root document context.
  ```bash
  yq '.a = .b' file.yaml   # .a gets the value of .b from root
  ```

- **Relative form (`|=`)**: RHS expression runs with each LHS node as context.
  ```bash
  yq '.[] |= . * 2' file.yaml   # double each array element
  yq '.a |= . + 1' file.yaml    # increment .a by its own value
  ```

### Operator Precedence

The pipe `|` has low precedence. To update deeply selected results, wrap the entire LHS in parentheses:

```bash
# WRONG — returns only the updated snippet
yq '.[] | select(.name == "sally") | .fruit = "mango"' file.yaml

# CORRECT — wraps LHS so full document is returned with update applied
yq '(.[] | select(.name == "sally") | .fruit) = "mango"' file.yaml
```

### Two Commands

- **`eval` (`e`)**: Runs the expression against each YAML document in each file, in sequence (default command).
  ```bash
  yq '.a.b' f1.yml f2.yml   # runs .a.b on each file separately
  ```

- **`eval-all` (`ea`)**: Reads all documents of all files into memory, then runs the expression once against everything. Used for multi-file operations like merge.
  ```bash
  yq ea 'select(fi == 0) * select(fi == 1)' f1.yml f2.yml
  ```

### Key Flags

- `-i` / `--inplace`: Update the first YAML file in place
- `-n` / `--null-input`: Do not read input, simply evaluate the expression (create from scratch)
- `-P` / `--prettyPrint`: Print idiomatic YAML (shorthand for `... style=""`)
- `-I <int>`: Set indentation level (default 2)
- `-j` / `--tojson`: Output as JSON
- `-e` / `--exit-status`: Set exit status if no matches or null/false returned
- `-N` / `--no-doc`: Do not print document separators (`---`)
- `-C` / `--colors`: Force color output
- `-M` / `--no-colors`: Force no color output
- `-p <format>`: Set input format (yaml, json, xml, props, csv, tsv, base64, lua, toml, hcl)
- `-o <format>`: Set output format (same options as -p)
- `-s <expr>` / `--split-exp`: Split results into multiple files using the expression for filenames
- `-f` / `--front-matter`: Process YAML front matter (process or extract)

## Advanced Topics

**Operators Reference**: Complete guide to all yq operators — assign, add, merge, select, delete, string ops, etc. → [Operators Reference](reference/01-operators.md)

**Multi-format Support**: Working with JSON, XML, CSV/TSV, Properties, HCL, TOML, Lua, Base64, and INI formats → [Multi-format Support](reference/02-multi-format.md)

**Advanced Patterns**: Recipes for complex transformations — merging files, reduce, variables, environment integration, front matter, split output, and troubleshooting → [Advanced Patterns](reference/03-advanced-patterns.md)
