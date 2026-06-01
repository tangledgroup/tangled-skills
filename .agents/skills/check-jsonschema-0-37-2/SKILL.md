---
name: check-jsonschema-0-37-2
description: CLI tool for validating JSON, YAML, TOML, and JSON5 files against JSON Schema. Use when verifying configuration files, CI/CD workflows, or any structured data against a schema in the terminal via `uvx check-jsonschema`. Supports local and remote schemas, 25+ builtin schemas for popular tools, and pre-commit integration.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - check-jsonschema
  - json-schema
  - validation
  - cli-tool
  - pre-commit
  - schema-validation
category: cli-tool
external_references:
  - https://pypi.org/project/check-jsonschema/0.37.2/
  - https://github.com/python-jsonschema/check-jsonschema/tree/0.37.2
---

# check-jsonschema 0.37.2

## Overview

`check-jsonschema` is a CLI tool for validating JSON, YAML, TOML, and JSON5 instance files against a JSON Schema. It runs via `uvx check-jsonschema` (no installation required) and supports schemas from local files, remote HTTP(S) URLs, or 25+ builtin schemas for popular CI/CD and configuration tools.

Built on the `jsonschema` library, it validates instances and reports errors with clear path-based messages. Remote schemas are automatically downloaded and cached.

## When to Use

- Validating JSON or YAML files against a JSON Schema in the terminal
- Checking CI/CD configuration files (GitHub Actions, GitLab CI, etc.) against their official schemas
- Verifying custom configuration files match an expected schema
- Running schema validation as part of a pre-commit hook
- Debugging schema validation errors with detailed output

## Core Concepts

### Execution

Always run via `uvx` for ephemeral execution — no persistent installation:

```bash
uvx check-jsonschema --version
```

### Schema Selection (mutually exclusive, pick one)

| Option | Description |
|--------|-------------|
| `--schemafile <path-or-url>` | Validate against a local file or remote HTTP(S) URL |
| `--builtin-schema <name>` | Use a vendored schema (e.g., `vendor.github-workflows`) |
| `--check-metaschema` | Validate files as JSON Schemas themselves (checks `$schema` key) |

### Instance File Formats

Files are auto-detected by extension: `.json`, `.yaml`, `.yml`, `.toml`. JSON5 requires the `json5` or `pyjson5` package installed alongside check-jsonschema. Use `--force-filetype <json|yaml|toml|json5>` to override detection.

### Output Formats

- **TEXT** (default): Human-readable error paths and messages
- **JSON**: Machine-parseable output via `-o JSON` or `--output-format JSON`

## Usage Examples

### Validate against a local schema

```bash
uvx check-jsonschema --schemafile schema.json instance.json
```

### Validate multiple files

```bash
uvx check-jsonschema --schemafile config-schema.json configs/*.json
```

### Validate against a remote schema

```bash
uvx check-jsonschema --schemafile https://json.schemastore.org/package instance.json
```

### Validate YAML files

```bash
uvx check-jsonschema --schemafile schema.json config.yaml
```

### Validate GitHub Actions workflows with builtin schema

```bash
uvx check-jsonschema --builtin-schema vendor.github-workflows .github/workflows/*.yml
```

### Validate a file as a JSON Schema itself

```bash
uvx check-jsonschema --check-metaschema my-schema.json
```

### Verbose output with color control

```bash
# More verbose (errors only)
uvx check-jsonschema -v --schemafile schema.json instance.json

# Even more verbose (includes filenames checked)
uvx check-jsonschema -vv --schemafile schema.json instance.json

# Force color or disable it
uvx check-jsonschema --color always --schemafile schema.json instance.json
uvx check-jsonschema --color never --schemafile schema.json instance.json
```

### JSON output for scripting

```bash
uvx check-jsonschema -o JSON --schemafile schema.json instance.json
```

### Disable format validation

Some schemas use `format` constraints not enforced by all validators. Disable them if needed:

```bash
# Disable all format checks
uvx check-jsonschema --disable-formats '*' --schemafile schema.json instance.json

# Disable specific formats
uvx check-jsonschema --disable-formats email,uri --schemafile schema.json instance.json
```

### Exit codes

- `0`: All instances valid
- `1`: Validation errors found
- `2`: Usage error (bad arguments, missing files)

## Advanced Topics

**Builtin Schemas**: 25+ vendored schemas for CI/CD tools, config formats, and more → [Builtin Schemas](reference/01-builtin-schemas.md)

**Pre-commit Hooks**: Configuring check-jsonschema as a pre-commit hook with ready-made hooks for popular tools → [Pre-commit Hooks](reference/02-pre-commit-hooks.md)

**Advanced Options**: Format validation, data transforms, caching, optional parsers, and FAQ → [Advanced Options](reference/03-advanced-options.md)
