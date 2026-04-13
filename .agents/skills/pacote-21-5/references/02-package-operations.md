# Package Operations Workflows

Common workflows and practical use cases for pacote operations.

## Analyze Package Dependencies

Inspect a package's dependency tree without installing:

```bash
# Get all dependencies from manifest
npx pacote manifest <package> --json | jq '.dependencies'

# Get devDependencies
npx pacote manifest lodash --json | jq '.devDependencies'

# Check for specific dependency version
npx pacote manifest express@4.18.2 --json | jq '.dependencies["body-parser"]'

# Compare dependencies across versions
npx pacote manifest "axios@0.21.0" --json | jq '.dependencies' > /tmp/v1.json
npx pacote manifest "axios@1.5.0" --json | jq '.dependencies' > /tmp/v2.json
diff /tmp/v1.json /tmp/v2.json

# Get package with minimal metadata (faster)
npx pacote manifest lodash --json | jq '{name, version, dependencies}'
```

## Audit Package Before Installation

Review package contents and metadata before adding to project:

```bash
# Check package size and file count
npx pacote manifest <package> --json | jq '.dist | {fileCount, unpackedSize}'

# Verify integrity hash matches expected
npx pacote resolve lodash@4.17.21 --long --json | jq '.integrity'

# List all files in package tarball
npx pacote tarball express@4.18.2 - | tar -tz

# Extract and inspect source code
npx pacote extract suspicious-package@latest ./inspect
cat ./inspect/package.json
ls -la ./inspect/

# Check for binary executables
npx pacote manifest <package> --json | jq '.bin'

# Check repository and homepage URLs
npx pacote manifest <package> --json | jq '{repository, homepage, bugs}'
```

## Find Available Versions

Discover all published versions and dist-tags:

```bash
# Get all dist-tags (latest, beta, next, rc, etc.)
npx pacote packument react --json | jq '.dist-tags'

# List all version numbers
npx pacote packument lodash --json | jq 'keys(.versions)'

# Count total versions published
npx pacote packument express --json | jq 'keys(.versions) | length'

# Find version by tag
npx pacote packument vue --json | jq '.dist-tags.next'

# Get latest 10 versions (sorted)
npx pacote packument react --json | jq 'keys(.versions) | sort_by(.) | reverse | .[0:10]'
```

## Compare Package Versions

Differences between package versions:

```bash
# Compare full manifests
npx pacote manifest "express@4.17.0" --json > /tmp/v1.json
npx pacote manifest "express@4.18.2" --json > /tmp/v2.json
diff /tmp/v1.json /tmp/v2.json

# Compare just version and dependencies
npx pacote manifest "axios@0.21.0" --json | jq '{version, dependencies}'
npx pacote manifest "axios@1.5.0" --json | jq '{version, dependencies}'

# Check engine requirements changes
npx pacote manifest "package@1.0.0" --json | jq '.engines'
npx pacote manifest "package@2.0.0" --json | jq '.engines'

# Compare file counts and sizes
npx pacote manifest "lodash@4.17.0" --json | jq '.dist | {fileCount, unpackedSize}'
npx pacote manifest "lodash@4.17.21" --json | jq '.dist | {fileCount, unpackedSize}'
```

## Download for Offline Use

Cache packages for offline installation or analysis:

```bash
# Download single tarball
npx pacote tarball lodash@latest ./offline-packages/lodash.tgz

# Batch download multiple packages
for pkg in lodash express axios react; do
  npx pacote tarball "${pkg}@latest" "./${pkg}.tgz"
done

# Extract to node_modules-style structure
mkdir -p ./node_modules/lodash
npx pacote extract "lodash@latest" ./node_modules/lodash

# Create offline cache with custom directory
npx pacote --cache=/offline/cache tarball express@latest ./express.tgz

# Download entire dependency tree (manual)
# First get dependencies:
npx pacote manifest myapp@latest --json | jq -r '.dependencies | keys[]' | while read dep; do
  npx pacote tarball "${dep}@latest" "./${dep}.tgz"
done
```

## Work with Git Packages

Fetch and inspect packages from git repositories:

```bash
# Get manifest from GitHub tag
npx pacote manifest "github:npm/cli#v10.0.0" --json | jq '{name, version, repository}'

# Resolve git reference to commit hash
npx pacote resolve "github:nvm-sh/nvm#v0.39.0" --long --json

# Extract git package (runs prepare scripts)
npx pacote extract "github:facebook/react#v18.2.0" ./react-src

# Work with GitLab packages
npx pacote manifest "gitlab:gitlab-org/gitlab#v16.0.0" --json

# Work with Bitbucket packages
npx pacote manifest "bitbucket:atlassian/atlaskit#v23.0.0" --json

# Use direct git URL
npx pacote manifest "git+https://github.com/nvm-sh/nvm.git#main" --json
```

Note: Git packages run `prepare` scripts during extraction to simulate published packages (transpilation, bundling, etc.).

## Stream Tarball Operations

Pipe tarball to other tools without saving to disk:

```bash
# List files in package
npx pacote tarball lodash@latest - | tar -tz

# Extract specific file from package
npx pacote tarball express@4.18.2 - | tar -xzO ./index.js > index.js

# Check tarball size without downloading fully
npx pacote tarball react@latest - | wc -c

# Pipe to checksum tool
npx pacote tarball axios@latest - | sha256sum

# Extract and grep for patterns
npx pacote tarball express@4.18.2 - | tar -xzO ./package.json | grep version
```

## Batch Operations

Process multiple packages at once:

```bash
# Get manifests for multiple packages
for pkg in lodash express axios react vue; do
  echo "=== $pkg ==="
  npx pacote manifest "${pkg}@latest" --json | jq '{name, version}'
done

# Download all as tarballs
packages=("lodash" "express" "axios" "chalk")
for pkg in "${packages[@]}"; do
  npx pacote tarball "${pkg}@latest" "./${pkg}.tgz"
done

# Extract multiple to organized structure
mkdir -p ./packages
for pkg in lodash express axios; do
  npx pacote extract "${pkg}@latest" "./packages/${pkg}"
done

# Generate dependency report
npx pacote manifest myapp@latest --json | jq -r '
  "Package: \(.name)@\(.version)\n\
Dependencies:\n\
  \(.dependencies | to_entries | map("  - \(.key): \(.value)") | join("\n"))"
'
```

## Security and Verification

Verify package integrity and signatures:

```bash
# Get expected integrity hash
npx pacote resolve lodash@4.17.21 --long --json | jq '.integrity'

# Verify during fetch with explicit integrity
npx pacote extract "lodash@4.17.21" ./lodash --integrity=sha512-...

# Get packument with signature information
npx pacote packument critical-package --json | jq '.versions."latest".dist.signatures'

# Verify package signatures (requires _keys config)
npx pacote --verify-signatures manifest signed-package --json

# Check for attestation/provenance data
npx pacote manifest pacote@21.5 --json | jq '.dist.attestations'
```

## Performance Optimization

Speed up operations with caching:

```bash
# Use custom cache directory (faster on SSD)
npx pacote --cache=/tmp/pacote-cache manifest lodash --json

# Revalidate cache entries
npx pacote --prefer-online manifest express --json

# Offline mode (use cache only, no network)
npx pacote --offline manifest react --json

# Clear corrupted cache
rm -rf ~/.npm/_cacache

# Check cache hit/miss in output
npx pacote manifest lodash --json  # Look for "cache hit" vs "cache miss"
```

## Custom Registry Operations

Work with private or alternative registries:

```bash
# Use Verdaccio or other private registry
npx pacote --registry=http://localhost:4873 manifest my-private-package --json

# Use npm mirror (faster in some regions)
npx pacote --registry=https://registry.npmmirror.com manifest lodash --json

# With authentication token (set via npm config)
npm config set //registry.npmjs.org/:_authToken=NPM_TOKEN
npx pacote manifest private-package --json

# Scoped registry configuration
npx pacote --@myscope:registry=https://npm.myscope.com manifest @myscope/package --json
```

## Troubleshooting Operations

Debug common issues:

```bash
# Check if package exists in registry
npx pacote packument nonexistent-package-xyz --json 2>&1 | head -5

# Verify specifier format
npx pacote resolve "invalid spec" --long --json 2>&1

# Test git connectivity
npx pacote manifest "github:npm/cli#v10.0.0" --json 2>&1

# Check cache status
ls -la ~/.npm/_cacache/

# Force revalidation
npx pacote --prefer-online manifest lodash --json
```
