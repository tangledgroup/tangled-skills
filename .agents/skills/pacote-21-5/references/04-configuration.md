# Configuration and Options

Complete reference for pacote configuration options, environment variables, and advanced settings.

## CLI Configuration Flags

All npm-compatible configuration can be passed as CLI flags to pacote.

### Cache Control

```bash
# Use custom cache directory
npx pacote --cache=/tmp/pacote-cache manifest lodash

# Default cache locations:
# - Linux: ~/.npm/_cacache
# - macOS: ~/.npm/_cacache
# - Windows: %APPDATA%\npm-cache\_cacache

# Prefer online (revalidate all cache entries)
npx pacote --prefer-online manifest express

# Offline mode (use cache only, no network requests)
npx pacote --offline manifest react

# Clear cache manually
rm -rf ~/.npm/_cacache
```

### Registry Configuration

```bash
# Use custom npm registry
npx pacote --registry=https://registry.npmmirror.com manifest lodash

# Use Verdaccio local registry
npx pacote --registry=http://localhost:4873 manifest my-package

# Scoped registry (for specific @scope packages)
npx pacote --@myscope:registry=https://npm.myscope.com manifest @myscope/package

# Verify package signatures
npx pacote --verify-signatures manifest signed-package
```

### Output Format

```bash
# JSON output (default when stdout is not TTY)
npx pacote manifest axios --json

# Long format for resolve command
npx pacote resolve express@latest --long --json

# Help information
npx pacote --help
npx pacote -h
```

### Security and Access Control

Control what types of packages can be fetched:

```bash
# Disallow git packages (security hardening)
npx pacote --allow-git=none manifest "github:user/repo"

# Allow git only for root packages
npx pacote --allow-git=root manifest "github:user/repo"

# Allow all package types (default)
npx pacote --allow-git=all manifest "github:user/repo"

# Control remote URL fetching
npx pacote --allow-remote=none manifest "https://example.com/package.tgz"

# Control file system access
npx pacote --allow-file=none manifest "file:./package.json"

# Control directory fetching
npx pacote --allow-directory=root manifest "./local-package"

# Control registry access
npx pacote --allow-registry=all manifest lodash
```

Values: `all`, `none`, `root` (only for root context packages)

## File Permission Options

Control extracted file permissions and ownership.

### Umask Configuration

```bash
# Custom umask (default: 0o22)
npx pacote extract lodash@latest ./lodash --umask=0o22
npx pacote extract express@latest ./express --umask=0o022
```

### Minimum Mode Settings

```bash
# Minimum file mode (default: 0o666)
npx pacote extract package@latest ./dest --fmode=0o644

# Minimum directory mode (default: 0o777)
npx pacote extract package@latest ./dest --dmode=0o755

# Combined permissions
npx pacote extract express@latest ./express \
  --umask=0o22 \
  --fmode=0o644 \
  --dmode=0o755
```

### Permission Formula

Extracted file modes are calculated as:

```
extracted_mode = ((tarball_mode | minimum_mode) & ~umask)
```

Example calculation for a file with mode `0o771` in tarball:
```
(0o771 | 0o666) = 0o777  (OR with fmode)
(0o777 & ~0o22) = 0o755  (AND with inverted umask)
```

### Ownership on Unix

When running as root, extracted files inherit ownership from the destination folder to prevent root-owned files in user directories:

```bash
# As root, files will match destination folder ownership
sudo npx pacote extract package@latest /home/user/project/node_modules/package
```

## Advanced API Options

These options are available when using pacote programmatically or via advanced CLI usage.

### Manifest Selection

```bash
# Use specific date for version selection (only versions before this date)
npx pacote manifest "react@18.0.0" --before=2023-01-01

# Custom default tag (instead of 'latest')
npx pacote manifest express --default-tag=beta

# Full metadata from registry (slower but more complete)
npx pacote manifest lodash --full-metadata

# Use slower read-package-json for extra fields like readme
npx pacote manifest lodash --full-read-json
```

### Integrity Verification

```bash
# Verify against expected integrity hash
npx pacote extract "lodash@4.17.21" ./lodash \
  --integrity=sha512-v2kDEe57lecTulaDIuNTPy3Ry4gLGJ6Z1O3vE1krgXZNrsQ+LFTGHVxVjcXPs17LhbZVGedAJv8XZ1tvj5FvSg==

# Verify package signatures (requires _keys config)
npx pacote --verify-signatures manifest signed-package

# Verify Sigstore attestations
npx pacote --verify-attestations manifest verified-package
```

### Caching and Performance

```bash
# Custom cache for packuments (via programmatic API)
# Use Map object to cache between calls

# TUF cache for attestation key material
npx pacote --tuf-cache=/tmp/tuf-cache manifest package-with-attestations

# Where to resolve relative file: dependencies
npx pacote --where=/path/to/project manifest "file:./relative/package"
```

### Pre-resolved Values

When you already know the resolved values, you can shortcut the lookup:

```bash
# Provide pre-resolved tarball URL
npx pacote manifest lodash --resolved=https://registry.npmjs.org/lodash/-/lodash-4.17.21.tgz

# Provide pre-computed integrity
npx pacote extract lodash --integrity=sha512-...
```

## Environment Variables

Pacote respects npm environment variables:

### Registry and Authentication

```bash
# Custom registry
export NPM_REGISTRY=https://registry.npmmirror.com
npx pacote manifest lodash

# Authentication token
export NPM_TOKEN=npm_...
npx pacote manifest private-package

# Scoped registry
export NPM_SCOPED_MYSCOPE_REGISTRY=https://npm.myscope.com
npx pacote manifest @myscope/package
```

### Cache and Performance

```bash
# Custom cache directory
export NPM_CACHE=/tmp/npm-cache
npx pacote manifest lodash

# Offline mode
export NPM_OFFLINE=true
npx pacote manifest react

# Prefer online
export NPM_PREFER_ONLINE=true
npx pacote manifest express
```

### Timeout and Retry

```bash
# Fetch timeout in milliseconds (default: 30000)
export NPM_FETCH_TIMEOUT=60000
npx pacote manifest large-package

# Max sockets for concurrent requests
export MAX_SOCKETS=50
npx pacote manifest lodash
```

## npm Config File

Pacote reads from npm's configuration files:

### Global Config

```bash
# Location: ~/.npmrc or /etc/npmrc
# Example ~/.npmrc:
registry=https://registry.npmjs.org/
@myscope:registry=https://npm.myscope.com
//registry.npmjs.org/:_authToken=NPM_TOKEN
fetch-timeout=60000
```

### Project Config

```bash
# Location: ./package.json or ./.npmrc
# In package.json:
{
  "npmConfig": {
    "registry": "https://custom-registry.com",
    "fetch-timeout": 60000
  }
}
```

### Config Priority

Configuration is loaded in this order (later overrides earlier):

1. Built-in defaults
2. Global config (`~/.npmrc`, `/etc/npmrc`)
3. Project config (`./.npmrc`, `package.json`)
4. Environment variables
5. CLI flags (highest priority)

## Custom Registry Setup

### Verdaccio (Local Registry)

```bash
# Start Verdaccio
verdaccio --config /etc/verdaccio/verdaccio.yaml

# Use with pacote
npx pacote --registry=http://localhost:4873 manifest my-package

# Publish to local registry first, then fetch
npm publish --registry=http://localhost:4873
npx pacote --registry=http://localhost:4873 manifest my-local-package
```

### Private npm Registry

```bash
# Configure authentication
npm config set //registry.npmjs.org/:_authToken=NPM_TOKEN

# Or use environment variable
export NPM_TOKEN=npm_...
npx pacote manifest private-package

# Verify token works
npx pacote packument private-package --json | jq '.name'
```

### Corporate Proxy

```bash
# Set proxy in npm config
npm config set proxy=http://proxy.company.com:8080
npm config set https-proxy=https://proxy.company.com:8080

# Or use environment variables
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=https://proxy.company.com:8080
npx pacote manifest lodash
```

## Troubleshooting Configuration

### Check Current Config

```bash
# View all npm configuration
npm config list

# View specific setting
npm config get registry
npm config get cache

# Check effective config for pacote
npx pacote --registry=? manifest lodash 2>&1 | head -3
```

### Debug Mode

```bash
# Enable verbose logging
export NPM_DEBUG=1
npx pacote manifest lodash

# Or use npm loglevel
npx pacote --loglevel=verbose manifest express
```

### Common Configuration Issues

```bash
# Issue: 404 from registry
# Solution: Check registry URL
npm config get registry
npx pacote --registry=https://registry.npmjs.org manifest lodash

# Issue: Authentication failed
# Solution: Verify token
npm config list | grep auth
npm token list

# Issue: Cache corruption
# Solution: Clear cache
rm -rf ~/.npm/_cacache
npx pacote --prefer-online manifest lodash

# Issue: Permission denied on extract
# Solution: Check umask and permissions
npx pacote extract package@latest ./dest --umask=0o22 --fmode=0o644
```

## Performance Tuning

### Optimize for Speed

```bash
# Use fast cache location (SSD)
npx pacote --cache=/ssd-cache/pacote manifest lodash

# Reduce network validation
# (default behavior, no --prefer-online)
npx pacote manifest express

# Parallel downloads (batch operations)
for pkg in lodash express axios react; do
  npx pacote tarball "${pkg}@latest" "./${pkg}.tgz" &
done
wait
```

### Optimize for Reliability

```bash
# Always validate cache
npx pacote --prefer-online manifest critical-package

# Use multiple registries (fallback)
npx pacote --registry=https://registry.npmjs.org manifest package || \
  npx pacote --registry=https://registry.npmmirror.com manifest package

# Increase timeouts for slow networks
npm config set fetch-timeout 120000
npx pacote manifest large-package
```

## Security Best Practices

### Hardened Configuration

```bash
# Disallow git and remote packages in production
npx pacote --allow-git=none --allow-remote=none manifest lodash

# Verify all signatures
npx pacote --verify-signatures manifest critical-package

# Use integrity verification
npx pacote extract package@version ./dest --integrity=sha512-...

# Restrict file system access
npx pacote --allow-file=none manifest package
```

### Audit Configuration

```bash
# Check what registries are configured
npm config list | grep registry

# Verify authentication tokens (don't print values)
npm config list | grep -v "^;.*$" | grep auth

# Check cache location is secure
npm config get cache
ls -la ~/.npm/_cacache
```
