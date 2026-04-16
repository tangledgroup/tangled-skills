---
name: pacote-21-5
description: Use pacote 21.5 via npx to inspect, download, and extract npm packages without installing them first. Supports registry packages, git repositories, local files, directories, and tarballs for package inspection, dependency analysis, and offline extraction workflows.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - npm
  - packages
  - npx
  - download
  - extract
  - manifest
  - registry
  - git-packages
category: tooling
required_environment_variables: []
---

# pacote-21-5

Use pacote 21.5 via `npx` to fetch, inspect, and extract npm packages without requiring prior installation. Works with any package specifier npm supports: registry packages, GitHub repositories, tarball URLs, local files, and directories.

## When to Use

- Inspect package manifests (`package.json`) without installing dependencies
- Download package tarballs for offline use or analysis
- Extract packages to examine source code or file structure
- Resolve package specifiers to concrete versions and tarball URLs
- Analyze package metadata, dependencies, and dist-tags
- Work with git-hosted packages (GitHub, GitLab, Bitbucket)
- Fetch full packuments to see all available versions of a package

## Quick Start

### Get Package Manifest

Fetch the manifest for any package:

```bash
npx pacote manifest <spec> --json
```

See [Core Commands](references/01-core-commands.md) for detailed examples and output formats.

### Resolve Package Specifier

Resolve a specifier to its tarball URL or git reference:

```bash
npx pacote resolve <spec> --long --json
```

See [Core Commands](references/01-core-commands.md) for resolution examples.

### Download and Extract Packages

Download tarballs or extract packages to directories:

```bash
npx pacote tarball <spec> <output-file.tgz>
npx pacote extract <spec> <destination-folder>
```

See [Package Operations](references/02-package-operations.md) for detailed workflows.

### Work with Different Package Types

Pacote supports registry packages, git repositories, tarball URLs, and local files:

```bash
# Registry package
npx pacote manifest lodash@latest --json

# Git repository
npx pacote manifest "github:npm/cli#v10.0.0" --json

# Tarball URL
npx pacote manifest "https://registry.npmjs.org/lodash/-/lodash-4.17.21.tgz"

# Local file
npx pacote manifest "file:./package.json"
```

See [Package Specifiers](references/03-package-specifiers.md) for complete format documentation.

## Reference Files

- [`references/01-core-commands.md`](references/01-core-commands.md) - Detailed command reference with examples (manifest, resolve, packument, tarball, extract)
- [`references/02-package-operations.md`](references/02-package-operations.md) - Common workflows: dependency analysis, package auditing, version comparison, offline downloads
- [`references/03-package-specifiers.md`](references/03-package-specifiers.md) - All supported specifier formats: registry, git (GitHub/GitLab/Bitbucket), tarball URLs, local files/directories
- [`references/04-configuration.md`](references/04-configuration.md) - Configuration options: cache control, registry settings, authentication, output formats, file permissions
- [`references/05-troubleshooting.md`](references/05-troubleshooting.md) - Common issues and solutions: git authentication, cache problems, network errors, permission issues

**Note:** `{baseDir}` refers to the skill's base directory (e.g., `.agents/skills/pacote-21-5/`). All paths are relative to this directory.

## Troubleshooting

See [Troubleshooting Guide](references/05-troubleshooting.md) for solutions to common issues including:
- Git authentication errors for private repositories
- Cache corruption and clearing
- Network timeouts and registry failures
- File permission issues on extraction

## Package Specifier Formats

Pacote supports all npm package specifier formats via [npm-package-arg](https://npm.im/npm-package-arg):

### Registry Packages

```bash
# By name (defaults to @latest tag)
npx pacote manifest lodash

# By version
npx pacote manifest "lodash@4.17.21"

# By tag
npx pacote manifest "express@beta"

# Version range
npx pacote manifest "react@^18.0.0"
npx pacote manifest "vue@~3.3.0"
```

### Git Repositories

```bash
# GitHub (github:user/repo#commitish)
npx pacote manifest "github:npm/cli#v10.0.0"
npx pacote manifest "github:facebook/react#v18.2.0"

# GitLab (gitlab:user/repo#commitish)
npx pacote manifest "gitlab:gitlab-org/gitlab#v16.0.0"

# Bitbucket (bitbucket:user/repo#commitish)
npx pacote manifest "bitbucket:atlassian/atlaskit#v23.0.0"

# Direct git URL
npx pacote manifest "git+https://github.com/nvm-sh/nvm.git#v0.39.0"
npx pacote manifest "git+ssh://git@github.com/nvm-sh/nvm.git#main"
```

### Tarball URLs

```bash
# Direct tarball URL from npm registry
npx pacote manifest "https://registry.npmjs.org/lodash/-/lodash-4.17.21.tgz"

# Custom tarball server
npx pacote manifest "https://example.com/packages/my-package.tgz"
```

### Local Files and Directories

```bash
# Local package.json file
npx pacote manifest "file:./path/to/package.json"

# Local directory with package.json
npx pacote manifest "file:./path/to/folder"
npx pacote manifest "./relative/path"
npx pacote manifest "/absolute/path"
```

## Configuration Options

Pacote accepts npm-compatible configuration flags. Common options:

### Cache Control

```bash
# Use custom cache directory
npx pacote --cache=/tmp/pacote-cache manifest lodash

# Prefer online (revalidate cache)
npx pacote --prefer-online manifest express

# Offline mode (use cache only)
npx pacote --offline manifest react
```

### Registry Configuration

```bash
# Use custom registry
npx pacote --registry=https://registry.npmmirror.com manifest lodash

# Verify package signatures
npx pacote --verify-signatures manifest critical-package
```

### Output Format

```bash
# JSON output (default when not TTY)
npx pacote manifest axios --json

# Long format for resolve command
npx pacote resolve express@latest --long --json

# Help
npx pacote --help
```

## Common Workflows

### Analyze Package Dependencies

Inspect a package's dependency tree without installing:

```bash
# Get dependencies from manifest
npx pacote manifest <package> --json | jq '.dependencies'

# Check for outdated dependencies
npx pacote manifest lodash --json | jq '{name, version, dependencies}'

# Compare versions between packages
npx pacote manifest "express@4.18.0" --json | jq '.dependencies.body-parser'
npx pacote manifest "express@4.18.2" --json | jq '.dependencies.body-parser'
```

### Audit Package Before Installation

Review package contents and metadata before adding to project:

```bash
# Check package size and file count
npx pacote manifest <package> --json | jq '.dist | {fileCount, unpackedSize}'

# Verify integrity hash
npx pacote resolve <package> --long --json | jq '.integrity'

# List all files in package
npx pacote tarball <package> - | tar -tz

# Extract and inspect source
npx pacote extract <package> ./inspect && cat ./inspect/package.json
```

### Find Available Versions

Discover all published versions and dist-tags:

```bash
# Get all dist-tags (latest, beta, next, etc.)
npx pacote packument react --json | jq '.dist-tags'

# List all versions (may be large)
npx pacote packument lodash --json | jq 'keys(.versions)'

# Find version published before date
npx pacote manifest "react@18.0.0" --json --before=2023-01-01
```

### Work with Git Packages

Fetch and inspect packages from git repositories:

```bash
# Get manifest from GitHub tag
npx pacote manifest "github:npm/cli#v10.0.0" --json | jq '{name, version, repository}'

# Resolve git reference to commit hash
npx pacote resolve "github:nvm-sh/nvm#v0.39.0" --long --json

# Extract git package (runs prepare scripts)
npx pacote extract "github:facebook/react#v18.2.0" ./react-src
```

Note: Git packages run `prepare` scripts during extraction to simulate published packages (transpilation, bundling, etc.).

### Download for Offline Use

Cache packages for offline installation or analysis:

```bash
# Download tarball with custom cache
npx pacote --cache=/offline/packages tarball lodash@latest ./lodash.tgz

# Batch download multiple packages
for pkg in lodash express axios; do
  npx pacote tarball "${pkg}@latest" "./${pkg}.tgz"
done

# Extract to node_modules-style structure
mkdir -p ./node_modules/lodash
npx pacote extract "lodash@latest" ./node_modules/lodash
```

### Compare Package Versions

Differences between package versions:

```bash
# Compare manifests side by side
npx pacote manifest "express@4.17.0" --json > /tmp/v1.json
npx pacote manifest "express@4.18.2" --json > /tmp/v2.json
diff /tmp/v1.json /tmp/v2.json

# Check dependency changes
npx pacote manifest "axios@0.21.0" --json | jq '.dependencies'
npx pacote manifest "axios@1.5.0" --json | jq '.dependencies'
```

## Advanced Usage

### Stream Tarball Contents

Pipe tarball to other tools without saving to disk:

```bash
# List files in package
npx pacote tarball lodash@latest - | tar -tz

# Extract specific file from package
npx pacote tarball express@4.18.2 - | tar -xzO ./index.js > index.js

# Check tarball size without downloading fully
npx pacote tarball react@latest - | wc -c
```

### Custom Registry and Authentication

Work with private registries:

```bash
# Use Verdaccio or other private registry
npx pacote --registry=http://localhost:4873 manifest my-private-package

# With authentication token
npm config set //registry.npmjs.org/:_authToken=NPM_TOKEN
npx pacote manifest private-package --json

# Scoped registry
npx pacote --@myscope:registry=https://npm.myscope.com manifest @myscope/package
```

### Integrity Verification

Verify package integrity using SRI hashes:

```bash
# Get expected integrity hash
npx pacote resolve lodash@4.17.21 --long --json | jq '.integrity'

# Verify during fetch (automatically done by default)
npx pacote extract "lodash@4.17.21" ./lodash --integrity=sha512-dXf...

# Get packument with signatures
npx pacote packument critical-package --json | jq '.versions."latest".dist.signatures'
```

### File Permissions and Ownership

Control extracted file permissions:

```bash
# Custom umask for extracted files
npx pacote extract lodash@latest ./lodash --umask=0o22

# Minimum file mode (fmode) and directory mode (dmode)
npx pacote extract express@latest ./express --fmode=0o644 --dmode=0o755
```

Default permissions formula:
```
extracted_mode = ((tarball_mode | minimum_mode) & ~umask)
```

### Git Fetcher Options

Control git package fetching behavior:

```bash
# Disallow git packages (security)
npx pacote --allow-git=none manifest "github:user/repo"

# Allow only for root packages
npx pacote --allow-git=root manifest "github:user/repo"

# Allow all types (default)
npx pacote --allow-git=all manifest "github:user/repo"
```

## Troubleshooting

### Git Authentication Errors

When fetching from private git repositories:

```bash
# Error: Could not read from remote repository
# Solution: Configure git credentials or use HTTPS with token

# For GitHub, use token authentication
npx pacote manifest "git+https://x-access-token:${GITHUB_TOKEN}@github.com/user/private-repo.git#main"
```

### Cache Issues

Clear or relocate cache if corrupted:

```bash
# Find default cache location
npm config get cache

# Clear pacote cache
rm -rf ~/.npm/_cacache

# Use custom cache directory
npx pacote --cache=/tmp/clean-cache manifest lodash
```

### Network Errors

Handle registry timeouts or failures:

```bash
# Increase timeout (via npm config)
npm config set fetch-timeout 60000

# Retry with different registry mirror
npx pacote --registry=https://registry.npmmirror.com manifest lodash

# Offline mode with cached data
npx pacote --offline manifest lodash
```

### Permission Denied on Extract

Fix file permission issues:

```bash
# Extract with custom permissions
npx pacote extract package@latest ./dest --umask=0o22 --fmode=0o644 --dmode=0o755

# As root, ownership matches destination folder (prevents root-owned files)
sudo npx pacote extract package@latest ./node_modules/package
```

### Large Package Downloads

Handle memory issues with large packages:

```bash
# Stream instead of buffering in memory
npx pacote tarball large-package@latest - | tar -xzC ./dest

# Use file output instead of buffer
npx pacote tarball large-package@latest package.tgz
```

## API Reference Summary

| Command | Description | Returns |
|---------|-------------|---------|
| `pacote resolve <spec>` | Resolve specifier to tarball URL or git ref | Resolved URL/ref |
| `pacote manifest <spec>` | Fetch package manifest (package.json + metadata) | Manifest object |
| `pacote packument <spec>` | Fetch full packument (all versions) | Packument object |
| `pacote tarball <spec> [file]` | Download tarball to file or stdout | Tarball data |
| `pacote extract <spec> <folder>` | Extract package to directory | Extraction result |

### Common Flags

| Flag | Description |
|------|-------------|
| `--json` | Output as JSON (default when not TTY) |
| `--long` | Include integrity and from fields (resolve command) |
| `--cache=<path>` | Use custom cache directory |
| `--registry=<url>` | Use custom npm registry |
| `--prefer-online` | Revalidate cache entries |
| `--offline` | Use cache only, no network |
| `--verify-signatures` | Verify package signatures |
| `--allow-git=all\|none\|root` | Control git package fetching |

## Notes

- All commands work via `npx` without prior installation: `npx pacote <command>`
- Package specifiers follow [npm-package-arg](https://npm.im/npm-package-arg) format
- Git packages run `prepare` scripts to simulate published packages
- Default cache location matches npm's default (`~/.npm/_cacache`)
- Integrity verification is automatic using SRI hashes from registry
- File extraction prevents root-owned files when running as root on Unix
