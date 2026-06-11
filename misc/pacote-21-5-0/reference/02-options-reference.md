# Options Reference

All pacote API methods accept an `opts` object. Options are passed through to `npm-registry-fetch` and `cacache`, so anything those modules accept is also valid. The opts object is cloned internally and mutated during processing to add integrity, resolved, and other computed properties.

## Cache Options

**cache** — Where to store cache entries and temp files. Passed to cacache. Defaults to npm's platform-specific default (`~/.npm/_cacache` on Unix, `%APPDATA%\npm-cache\_cacache` on Windows).

```js
{ cache: '/tmp/my-pacote-cache' }
```

**tufCache** — Where to store TUF metadata/target files when retrieving attestation key material. Defaults to npm's default TUF cache location.

```js
{ tufCache: '/tmp/my-tuf-cache' }
```

**packumentCache** — A `Map` object for caching packument requests between pacote calls. Avoids repeated registry hits for the same packument within a single command execution.

```js
const packumentCache = new Map()
await pacote.manifest('lodash@4', { packumentCache })
await pacote.manifest('lodash@4.17', { packumentCache }) // uses cached packument
```

## Integrity Options

**integrity** — Expected SRI integrity string for the fetched tarball. Mismatched values raise `EINTEGRITY` errors. Passed as a string; internally parsed by ssri.

```js
{ integrity: 'sha512-abc123...' }
```

**resolved** — Shortcut to skip resolution and use a known resolved value directly. Should be specified if already known from a previous operation or lockfile.

```js
{ resolved: 'https://registry.npmjs.org/lodash/-/lodash-4.17.21.tgz' }
```

**defaultIntegrityAlgorithm** — Default hash algorithm when no integrity is provided. Defaults to `'sha512'`.

## Network Options

**registry** — The npm registry URL. Defaults to `https://registry.npmjs.org/`. Trailing slashes are normalized.

```js
{ registry: 'https://npm.pkg.github.com/' }
```

**preferOnline** — Revalidate cache entries even when not strictly necessary. Defaults to `false`.

**preferOffline** — Prefer cached data even if stale. Passed through to npm-registry-fetch.

**offline** — Only use cached data, never make network requests. Passed through to npm-registry-fetch.

**replaceRegistryHost** — Controls whether tarball URLs are rewritten to use the configured registry host. Values: `'npmjs'` (default, rewrites `registry.npmjs.org`), `'never'`, `'always'`, or a specific hostname.

## Manifest Selection Options

**defaultTag** — The default dist-tag when no version is specified. Defaults to `'latest'`.

```js
{ defaultTag: 'next' } // foo@ → foo@next instead of foo@latest
```

**before** — A Date object. When picking a manifest from a packument, only considers versions published before this date. Requires `fullMetadata: true` (automatically enabled when `before` is set).

```js
{ before: new Date('2024-01-01') }
```

**fullMetadata** — Fetch full packument metadata including author, description, etc. Defaults to `true` when `before` is set, otherwise `false`. Corgi format (minimal metadata) is used by default for performance.

```js
{ fullMetadata: true }
```

**fullReadJson** — Use the slower `read-package-json` instead of `read-package-json-fast` to include extra fields like "readme" in manifests. Defaults to `false`.

## Security Allowlist Options

As of pacote 21.x, you can control which fetch source types are allowed. Each option accepts `'all'`, `'none'`, or `'root'`:

**allowGit** — Whether to allow git specs. Defaults to `'all'`. Set to `'none'` to block all git dependencies.

**allowRemote** — Whether to allow remote URL specs. Defaults to `'all'`.

**allowFile** — Whether to allow local file specs. Defaults to `'all'`.

**allowDirectory** — Whether to allow directory specs. Defaults to `'all'`.

**allowRegistry** — Whether to allow registry specs (version, range, tag, alias). Added in 21.4.0.

When set to `'root'`, the fetch type is only allowed if `opts._isRoot` is `true`. This enables policies where direct dependencies can use git but transitive dependencies cannot.

```js
// Block all git and remote fetches
{ allowGit: 'none', allowRemote: 'none' }

// Allow git only for root (direct) dependencies
{ allowGit: 'root', _isRoot: true }
```

**_isRoot** — Whether the package being fetched is in a root context. Defaults to `false`. Informs the `allowX` options about request context.

## File Mode Options

**umask** — Permission mode mask for extracted files and directories. Defaults to `0o22`. Applied after minimum modes to prevent group/world-writable files.

**fmode** — Minimum permission mode for extracted files. Defaults to `0o666`. Files are at least this permissive.

**dmode** — Minimum permission mode for extracted directories. Defaults to `0o777`. Directories are at least this permissive.

The extraction formula is: `(tarball_entry_mode | minimum_mode) & ~umask`. To respect exact tarball modes (even if unusable), set both `fmode` and `dmode` to `0`.

## Script Execution Options

**ignoreScripts** — When true, skip running `prepare` lifecycle scripts during directory and git package preparation. Added in 20.0.0.

**foregroundScripts** — When true, run prepare scripts with `'inherit'` stdio instead of `'pipe'`, showing output directly.

**scriptShell** — Shell to use for running prepare scripts. Passed to `@npmcli/run-script`.

## npm CLI Integration Options

**npmBin** — The npm binary to use for preparing directories and git packages. Defaults to `'npm'`. Set to `'yarn'` when using yarn.

**npmInstallCmd** — Command arguments for installing deps during preparation. Defaults to `['install', '--force']`.

**npmCliConfig** — Additional CLI flags passed to npm during preparation. pacote sets sensible defaults including `--no-progress`, `--no-save`, `--no-audit`, `--include=dev`, `--include=peer`, `--include=optional`.

**where** — Base folder for resolving relative `file:` dependencies.

## Signature and Attestation Options

**verifySignatures** — When true, verify the integrity signature of manifests if present. Requires `_keys` config entry scoped to the registry.

**verifyAttestations** — When true, verify Sigstore attestations if present. Supports both key-based (publish attestations with registry keys) and keyless (Sigstore/Fulcio) attestation verification.

**_keys** — Registry public keys for signature verification. Configured as `${registryHost}:_keys` in the opts object.

## DirFetcher-Specific Options

**tree** — A pre-loaded Arborist tree for packing directories. If not provided, `Arborist` must be set.

**Arborist** — The `@npmcli/arborist` constructor. Required by DirFetcher if `tree` is not provided.

**prefix** — Tar prefix path for directory packing.

**workspaces** — Workspace configuration for directory packing.

## Registry Fetcher Options

**allowGitIgnore** — When true, allows `.gitignore` files to be treated as `.npmignore` during extraction. Controls whether `.gitignore` is renamed to `.npmignore` in extracted packages.
