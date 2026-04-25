# Core Commands Reference

Detailed reference for all pacote CLI commands with examples and output formats.

## manifest

Fetch a package's manifest (essentially `package.json` plus metadata added by the registry).

### Syntax

```bash
npx pacote manifest <spec> [options]
```

### Options

- `--json` - Output as JSON (default when stdout is not a TTY)
- `--registry=<url>` - Use custom npm registry
- `--before=<date>` - Only consider versions published before date

### Examples

```bash
# Latest version from registry
npx pacote manifest lodash@latest --json

# Specific version
npx pacote manifest express@4.18.2 --json

# Git repository (github:user/repo#tag)
npx pacote manifest "github:npm/cli#v10.0.0" --json

# Version range
npx pacote manifest "react@^18.0.0" --json

# With custom registry
npx pacote --registry=https://registry.npmmirror.com manifest axios --json
```

### Output Format

```json
{
  "name": "lodash",
  "version": "4.17.21",
  "description": "Lodash modular utilities.",
  "homepage": "https://lodash.com/",
  "repository": {
    "type": "git",
    "url": "https://github.com/lodash/lodash.git"
  },
  "dependencies": {},
  "devDependencies": {
    "chalk": "^4.0.0"
  },
  "dist": {
    "shasum": "8a5f6af1c20e9fef8b93825dd7be0ba7ddf93ceb",
    "tarball": "https://registry.npmjs.org/lodash/-/lodash-4.17.21.tgz",
    "fileCount": 52,
    "integrity": "sha512-v2kDEe57lecTulaDIuNTPy3Ry4gLGJ6Z1O3vE1krgXZNrsQ+LFTGHVxVjcXPs17LhbZVGedAJv8XZ1tvj5FvSg==",
    "signatures": [
      {
        "keyid": "SHA256:DhQ8wR5APBvFHLF/+Tc+AYvPOdTpcIDqOhxsBHRwC7U",
        "sig": "MEUCIQDZo+W4JJ5T/9RkS8Wz1uN7Gw+CBvP16yGeT8H9lnb+sAIgKM5Nqj636zyRL2YOUuhbSK2e1DhK2VBaMXiVNIYMq1M="
      }
    ],
    "unpackedSize": 52740
  },
  "_id": "lodash@4.17.21",
  "_resolved": "https://registry.npmjs.org/lodash/-/lodash-4.17.21.tgz",
  "_from": "lodash@latest",
  "_integrity": "sha512-v2kDEe57lecTulaDIuNTPy3Ry4gLGJ6Z1O3vE1krgXZNrsQ+LFTGHVxVjcXPs17LhbZVGedAJv8XZ1tvj5FvSg=="
}
```

### Key Fields

- `name`, `version`, `description` - Package metadata from `package.json`
- `dependencies`, `devDependencies` - Dependency lists
- `dist.tarball` - URL to download the package tarball
- `dist.integrity` - SRI hash for verification
- `_resolved` - Fully resolved tarball URL
- `_from` - Normalized form of the spec passed in
- `_integrity` - Integrity value copied from `dist.integrity`

## resolve

Resolve a package specifier to its fully resolved target (tarball URL, file path, or git repo with commit hash).

### Syntax

```bash
npx pacote resolve <spec> [options]
```

### Options

- `--long` - Include integrity and from fields in output
- `--json` - Output as JSON

### Examples

```bash
# Resolve to tarball URL (simple output)
npx pacote resolve express@latest

# With full details
npx pacote resolve express@latest --long --json

# Resolve git tag to commit hash
npx pacote resolve "github:nvm-sh/nvm#v0.39.0" --long --json

# Resolve specific version
npx pacote resolve "axios@1.5.0" --long --json
```

### Output Format (without --long)

```
https://registry.npmjs.org/express/-/express-4.18.2.tgz
```

### Output Format (with --long --json)

```json
{
  "resolved": "https://registry.npmjs.org/express/-/express-4.18.2.tgz",
  "integrity": "sha512-5/PsL6iGPdfQ/lKM1UuielYgv3BUoJfz1aUwU9vHZ+J7gyvwdQXFEBIEIaxeGf0GIcreATNyBExtalisDbuMqQ==",
  "from": "express@latest"
}
```

### Git Resolution Example

```json
{
  "resolved": "git+ssh://git@github.com/nvm-sh/nvm.git#5b3d188b83f27ec31d97f3f3e6e49220e09b6985",
  "from": "github:nvm-sh/nvm#v0.39.0"
}
```

## packument

Fetch the full packument (all versions and metadata) for a package from the registry.

### Syntax

```bash
npx pacote packument <package-name> [options]
```

Note: Only works with registry packages, not git URLs or local files.

### Options

- `--json` - Output as JSON (default when not TTY)

### Examples

```bash
# Get full packument for react
npx pacote packument react --json

# Extract just dist-tags
npx pacote packument lodash --json | jq '.dist-tags'

# List all version numbers
npx pacote packument express --json | jq 'keys(.versions)'
```

### Output Format (truncated)

```json
{
  "name": "react",
  "dist-tags": {
    "latest": "18.2.0",
    "beta": "19.0.0-beta-26f2496093-20240514",
    "next": "19.0.0-rc.1",
    "experimental": "0.0.0-experimental-705268dc-20260409"
  },
  "versions": {
    "18.2.0": {
      "name": "react",
      "version": "18.2.0",
      "description": "React is a JavaScript library for building user interfaces",
      "dist": {
        "shasum": "...",
        "tarball": "https://registry.npmjs.org/react/-/react-18.2.0.tgz",
        "integrity": "sha512-..."
      },
      "dependencies": {
        "loose-envify": "^1.1.0"
      }
    },
    "18.1.0": { ... },
    "17.0.2": { ... }
  },
  "time": {
    "created": "2013-03-29T01:33:28.696Z",
    "18.2.0": "2023-06-15T15:46:53.115Z",
    "18.1.0": "2022-12-30T20:51:37.295Z"
  },
  "_contentLength": 245678
}
```

### Key Fields

- `dist-tags` - Object mapping tag names (latest, beta, next) to version numbers
- `versions` - Object where each key is a version number and value is the manifest for that version
- `time` - Object mapping version numbers to publication timestamps
- `_contentLength` - Size of the packument response

## tarball

Fetch a package tarball and save to file or stream to stdout.

### Syntax

```bash
npx pacote tarball <spec> [<filename>] [options]
```

If `<filename>` is missing or `-`, the tarball is streamed to stdout.

### Options

- `--json` - Output metadata as JSON (when writing to file)

### Examples

```bash
# Download to specific file
npx pacote tarball tinyglobby@latest /tmp/tinyglobby.tgz

# Download specific version
npx pacote tarball "lodash@4.17.21" ./lodash.tgz

# Stream to stdout and list contents
npx pacote tarball axios@latest - | tar -tz

# Stream and extract specific file
npx pacote tarball express@4.18.2 - | tar -xzO ./index.js > index.js

# Save with auto-generated name in current directory
npx pacote tarball chalk@5.0.0
```

### Output Format (when writing to file)

```json
{
  "integrity": "sha512-pn99VhoACYR8nFHhxqix+uvsbXineAasWm5ojXoN8xEwK5Kd3/TrhNn1wByuD52UxWRLy8pu+kRMniEi6Eq9Zg==",
  "resolved": "https://registry.npmjs.org/tinyglobby/-/tinyglobby-0.2.16.tgz",
  "from": "tinyglobby@latest"
}
```

### Streaming Examples

```bash
# List all files in package
npx pacote tarball lodash@latest - | tar -tz

# Check tarball size without full download
npx pacote tarball react@latest - | wc -c

# Pipe to another tool
npx pacote tarball express@4.18.2 - > ./express.tgz
```

## extract

Extract a package's tarball contents into a destination folder.

### Syntax

```bash
npx pacote extract <spec> <destination-folder> [options]
```

### Options

- `--json` - Output result as JSON
- `--umask=<mode>` - Permission mode mask (default: 0o22)
- `--fmode=<mode>` - Minimum file mode (default: 0o666)
- `--dmode=<mode>` - Minimum directory mode (default: 0o777)

### Examples

```bash
# Extract to specific folder
mkdir -p /tmp/packages
npx pacote extract express@4.18.2 /tmp/packages/express

# Extract git package (runs prepare scripts)
npx pacote extract "github:npm/cli#v10.0.0" ./npm-cli

# Extract and examine immediately
npx pacote extract chalk@5.0.0 ./chalk && ls -la ./chalk

# With custom permissions
npx pacote extract lodash@latest ./lodash --umask=0o22 --fmode=0o644
```

### Output Format

```json
{
  "resolved": "https://registry.npmjs.org/express/-/express-4.18.2.tgz",
  "integrity": "sha512-5/PsL6iGPdfQ/lKM1UuielYgv3BUoJfz1aUwU9vHZ+J7gyvwdQXFEBIEIaxeGf0GIcreATNyBExtalisDbuMqQ==",
  "from": "express@4.18.2"
}
```

### Extracted Contents

After extraction, the destination folder contains:

```
express/
├── History.md
├── LICENSE
├── Readme.md
├── index.js
├── lib/
│   ├── application.js
│   ├── request.js
│   ├── response.js
│   └── ...
└── package.json
```

### File Permission Formula

Extracted file modes are calculated as:

```
extracted_mode = ((tarball_mode | minimum_mode) & ~umask)
```

Example: A file with mode `0o771` in tarball, with default `fmode=0o666` and `umask=0o22`:

```
(0o771 | 0o666) = 0o777
(0o777 & ~0o22) = 0o755
```

### Git Package Note

When extracting git packages, pacote runs `prepare` scripts to simulate what would be published. This ensures transpiled/bundled code is available instead of raw source that might need compilation.
