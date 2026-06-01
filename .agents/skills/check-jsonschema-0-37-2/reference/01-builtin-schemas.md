# Builtin Schemas

## Contents
- Vendor Schemas (SchemaStore and other sources)
- Custom Schemas
- Using Builtin Schemas

## Vendor Schemas

check-jsonschema ships with vendored copies of schemas from SchemaStore and other sources. Use `--builtin-schema vendor.<name>` to select one.

### CI/CD Platforms

| Schema Name | Description |
|---|---|
| `vendor.azure-pipelines` | Azure Pipelines (Microsoft) |
| `vendor.bamboo-spec` | Bamboo Specs (SchemaStore) |
| `vendor.bitbucket-pipelines` | Bitbucket Pipelines (SchemaStore) |
| `vendor.buildkite` | Buildkite Pipelines (Buildkite) |
| `vendor.circle-ci` | CircleCI Config (SchemaStore) |
| `vendor.cloudbuild` | Google Cloud Build (SchemaStore) |
| `vendor.drone-ci` | Drone-CI Config (SchemaStore) |
| `vendor.github-actions` | GitHub Actions (SchemaStore) |
| `vendor.github-workflows` | GitHub Workflows (SchemaStore) |
| `vendor.gitlab-ci` | GitLab CI Config (SchemaStore) |
| `vendor.travis` | Travis Config (SchemaStore) |
| `vendor.woodpecker-ci` | Woodpecker CI (SchemaStore) |

### Configuration Tools

| Schema Name | Description |
|---|---|
| `vendor.changie` | Changie.dev configuration |
| `vendor.citation-file-format` | Citation File Format (CFF) |
| `vendor.codecov` | Codecov Config (SchemaStore) |
| `vendor.compose-spec` | Docker Compose (SchemaStore) |
| `vendor.dependabot` | Dependabot Config v2 (SchemaStore) |
| `vendor.meltano` | Meltano Config (Meltano) |
| `vendor.mergify` | Mergify Config (SchemaStore) |
| `vendor.readthedocs` | ReadTheDocs Config (ReadTheDocs) |
| `vendor.renovate` | Renovate Config (Renovate) |
| `vendor.snapcraft` | Snapcraft Files (Canonical) |
| `vendor.taskfile` | Taskfile Config (Task) |

### GitHub-Specific

| Schema Name | Description |
|---|---|
| `vendor.github-discussion` | GitHub Discussion Templates (SchemaStore) |
| `vendor.github-issue-config` | GitHub Issue Config (SchemaStore) |
| `vendor.github-issue-forms` | GitHub Issue Forms (SchemaStore) |

## Custom Schemas

Custom schemas are maintained by the check-jsonschema project itself:

| Schema Name | Description |
|---|---|
| `github-workflows-require-timeout` | Checks that all GitHub workflow jobs explicitly set `timeout-minutes` (default is 6 hours) |

## Using Builtin Schemas

### CLI usage with uvx

```bash
# Validate GitHub workflows
uvx check-jsonschema --builtin-schema vendor.github-workflows .github/workflows/*.yml

# Validate GitLab CI (with automatic !reference transform)
uvx check-jsonschema --builtin-schema vendor.gitlab-ci .gitlab-ci.yml

# Check that workflows set timeout-minutes
uvx check-jsonschema --builtin-schema github-workflows-require-timeout .github/workflows/*.yml

# Validate Renovate config
uvx check-jsonschema --builtin-schema vendor.renovate renovate.json
```

### Notes on specific schemas

- **Azure Pipelines** (`vendor.azure-pipelines`): Requires `--data-transform azure-pipelines` and `--regex-variant nonunicode` for full compatibility. The pre-commit hook includes these flags automatically.
- **GitLab CI** (`vendor.gitlab-ci`): Requires `--data-transform gitlab-ci` and `--regex-variant nonunicode` to handle `!reference` tags. The pre-commit hook includes these flags automatically.
- **Renovate** (`vendor.renovate`): Uses `--regex-variant nonunicode`. Does not support renovate config embedded in `package.json`.
