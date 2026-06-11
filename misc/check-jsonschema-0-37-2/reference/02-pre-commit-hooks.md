# Pre-commit Hooks

## Contents
- Generic Hooks
- Specialized Hooks (by tool/platform)
- Example Configurations
- Hook Implementation Details

## Generic Hooks

### `check-jsonschema`

Validate JSON or YAML files against a schema on disk or fetched via HTTP(S). You must specify a schema using pre-commit `args`.

```yaml
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-jsonschema
      files: ^data/.*\.json$
      args: ["--schemafile", "schemas/foo.json"]
```

### `check-metaschema`

Validate JSON Schema files against their matching metaschema, as specified in their `$schema` key.

```yaml
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-metaschema
      files: ^schemas/.*\.json$
```

## Specialized Hooks

Each specialized hook uses a builtin schema with appropriate flags pre-configured.

### CI/CD Platforms

```yaml
# Azure Pipelines
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-azure-pipelines

# Bamboo Specs
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-bamboo-spec

# Bitbucket Pipelines
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-bitbucket-pipelines

# Buildkite
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-buildkite

# CircleCI
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-circle-ci

# Google Cloud Build
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-cloudbuild

# Drone-CI
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-drone-ci

# GitHub Workflows
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-github-workflows

# GitLab CI
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-gitlab-ci

# Travis
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-travis

# Woodpecker CI
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-woodpecker-ci
```

### Configuration Tools

```yaml
# Changie
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-changie

# Citation File Format
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-citation-file-format

# Codecov
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-codecov

# Docker Compose
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-compose-spec

# Dependabot
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-dependabot

# Meltano
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-meltano

# Mergify
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-mergify

# ReadTheDocs
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-readthedocs

# Renovate
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-renovate

# Snapcraft
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-snapcraft

# Taskfile
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-taskfile
```

### GitHub-Specific

```yaml
# GitHub Actions (reusable)
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-github-actions

# GitHub Discussion Templates
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-github-discussion

# GitHub Issue Config
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-github-issue-config

# GitHub Issue Forms
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-github-issue-forms
```

## Example Configurations

### Reimplement check-github-workflows manually

The generic `check-jsonschema` hook can replicate specialized hooks:

```yaml
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-jsonschema
      name: "Check GitHub Workflows"
      files: ^\.github/workflows/[^/]+$
      types: [yaml]
      args: ["--schemafile", "https://json.schemastore.org/github-workflow"]
```

### Use a builtin schema with the generic hook

```yaml
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-jsonschema
      name: "Check GitHub Workflows set timeout-minutes"
      files: ^\.github/workflows/[^/]+$
      types: [yaml]
      args: ["--builtin-schema", "github-workflows-require-timeout"]
```

### Add JSON5 support for Renovate

```yaml
- repo: https://github.com/python-jsonschema/check-jsonschema
  rev: 0.37.2
  hooks:
    - id: check-renovate
      additional_dependencies: ['pyjson5']
```

## Hook Implementation Details

Specialized hooks are auto-generated from `src/check_jsonschema/catalog.py`. Each hook's `entry` command includes the appropriate `--builtin-schema`, `--data-transform`, and `--regex-variant` flags. For example:

- `check-azure-pipelines` → `--builtin-schema vendor.azure-pipelines --data-transform azure-pipelines --regex-variant nonunicode`
- `check-gitlab-ci` → `--builtin-schema vendor.gitlab-ci --data-transform gitlab-ci --regex-variant nonunicode`
- `check-renovate` → `--builtin-schema vendor.renovate --regex-variant nonunicode`

The `files` regex and `types` for each hook are pre-configured to match the expected file patterns for that tool.
