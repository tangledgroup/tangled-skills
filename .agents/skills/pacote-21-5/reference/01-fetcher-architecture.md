# Fetcher Architecture

pacote dispatches to one of five fetcher classes based on the specifier type parsed by `npm-package-arg`. All fetchers extend a common `FetcherBase` class that handles shared concerns: tarball extraction, caching via cacache, integrity verification, retry logic, and file mode management.

## Specifier Type Dispatch

The `FetcherBase.get(spec, opts)` factory method parses the spec using `npm-package-arg` and routes to the appropriate fetcher:

```
spec type        → fetcher class
─────────────────────────────────────
'git'            → GitFetcher
'remote'         → RemoteFetcher
'version'        → RegistryFetcher
'range'          → RegistryFetcher
'tag'            → RegistryFetcher
'alias'          → RegistryFetcher
'file'           → FileFetcher
'directory'      → DirFetcher
```

Each fetcher can be instantiated directly for advanced usage:

```js
import { GitFetcher, RegistryFetcher, FileFetcher, DirFetcher, RemoteFetcher } from 'pacote'

const rf = new RegistryFetcher({ type: 'version', name: 'lodash', rawSpec: '4.17.21' }, opts)
const manifest = await rf.manifest()
```

## FetcherBase (Common Base Class)

All fetchers inherit shared behavior from `FetcherBase`:

**Constructor**: Accepts a spec string and options object. Parses the spec via `npm-package-arg`, clones opts to avoid mutation side effects, sets up cache paths, and initializes file mode defaults.

**resolve()**: Returns a Promise resolving to the fully resolved target — tarball URL, file path, or git repo with commit hash. Implemented by each subclass.

**manifest()**: Returns a Promise resolving to the manifest object (package.json + `_resolved`, `_integrity`, `_from`, `_id`). Implemented by each subclass.

**packument()**: Returns a Promise resolving to the packument. Only `RegistryFetcher` fetches real packuments; other fetchers simulate one from their manifest.

**tarball()**: Returns a Promise resolving to a Buffer with `.from`, `.resolved`, and `.integrity` properties attached. Uses the shared caching and retry pipeline.

**tarballStream(handler)**: Internal method that feeds tarball data through a stream handler function. Handles cache lookup, cache corruption detection, and automatic retry on retriable errors (`EINTEGRITY`, `ENOENT`, `Z_DATA_ERROR`). The handler MUST return a Promise.

**extract(dest)**: Extracts the package tarball into a destination folder. Cleans the destination first, then pipes the tarball through `tar.x()` with mode filtering. Returns `{ from, resolved, integrity }`.

**Cache behavior**: Tarballs are cached by integrity digest via cacache. On fetch, pacote first tries the cache. If cache data is corrupted (integrity mismatch), it cleans the entry and retries from the resolved source. RemoteFetcher delegates caching to `npm-registry-fetch`/make-fetch-happen rather than duplicating it in pacote.

## RegistryFetcher

Handles registry specs: `version`, `range`, `tag`, and `alias`.

**resolve()**: Fetches the packument, picks the manifest using `npm-pick-manifest`, and returns `dist.tarball` as the resolved URL. Throws if no `dist.tarball` is present.

**packument()**: Fetches from the registry with appropriate Accept headers. By default requests "corgi" format (`application/vnd.npm.install-v1+json`) which returns minimal metadata suitable for installation. When `fullMetadata: true`, requests full JSON including author, description, etc. Falls back to full format if corgi returns 404 (some registries don't support it). Supports `packumentCache` — a Map to avoid repeated registry hits within a single command.

**manifest()**: Fetches the packument, uses `npm-pick-manifest` to select the version matching the spec, normalizes the package.json via `@npmcli/package-json`, and enriches with `_resolved`, `_integrity`, `_from`, and optionally `_time`. Handles integrity merging from `dist.integrity` or legacy `dist.shasum`.

**Tarball fetching**: Delegates actual tarball download to `RemoteFetcher` — the registry provides a tarball URL, and RemoteFetcher handles the HTTP fetch with integrity verification.

## GitFetcher

Handles git specs: `github:user/repo`, `git+ssh://...`, `git://...`, etc.

**resolve()**: For hosted git platforms (GitHub, GitLab, Bitbucket), resolves without cloning by fetching remote refs via `@npmcli/git`. If the committish is a full SHA (40 or 64 hex chars), it skips cloning entirely and constructs the tarball URL directly. For non-hosted repos or ambiguous committishes, performs a shallow clone to determine HEAD.

**Hosted shortcut**: When a full SHA is provided for a hosted repo, pacote downloads the tarball directly from the platform's archive endpoint instead of cloning. This is significantly faster.

**SSH vs HTTPS**: Prefers HTTPS URLs (faster, passphrase-less for public repos, supports private repos with auth). Falls back to SSH only when HTTPS fails and no auth is present.

**Integrity skip**: Git dependencies never have integrity checks enforced (per npm/rfcs#525). Any `opts.integrity` is silently removed.

**prepare scripts**: When generating tarballs from git directories, prepare scripts are run to simulate what would be published. Uses `_PACOTE_NO_PREPARE_` environment variable to prevent infinite recursion in circular git dependencies.

**gitSubdir support**: As of 21.2.0, supports the `gitSubdir` field per the npm-package-arg spec, allowing packages within subdirectories of git repositories.

## FileFetcher

Handles file specs: `./package.tgz`, `file:/path/to/package.tgz`.

**resolve()**: Returns the fully resolved file path immediately — no network access needed.

**manifest()**: Extracts the tarball to a temp directory, reads package.json, and returns it enriched with `_resolved`, `_integrity`, `_from`.

**extract(dest)**: Calls the base class extract, then ensures bin scripts are marked executable (best-effort chmod).

**Tarball stream**: Returns a simple file read stream via `fs-minipass`.

## DirFetcher

Handles directory specs: `./my-package`, `file:/path/to/my-package`.

**resolve()**: Returns the fully resolved directory path.

**manifest()**: Reads package.json directly from the directory using `@npmcli/package-json`. No extraction needed.

**Tarball generation**: Unlike other fetchers, DirFetcher does not have a pre-existing tarball. It generates one on-the-fly by:
1. Running the `prepare` script (if present and `ignoreScripts` is not set)
2. Getting the file list via `npm-packlist` (using either a provided `tree` or loading via `@npmcli/arborist`)
3. Streaming files into a tar archive via `tar.c()`

**Arborist dependency**: Requires either `opts.tree` (a pre-loaded Arborist tree) or `opts.Arborist` (the Arborist constructor) to determine which files to include in the pack. This matches npm's own packing behavior.

**DirFetcher.tarCreateOptions(manifest)**: Static method exposed as public API for constructing tar creation options from a manifest.

## RemoteFetcher

Handles remote URL specs: `https://example.com/package.tgz`.

**resolve()**: Returns the resolved URL immediately. Supports `replaceRegistryHost` option to redirect tarball URLs to a different registry host.

**manifest()**: Same as FileFetcher — extracts to temp dir and reads package.json.

**Tarball fetching**: Uses `npm-registry-fetch` with integrity verification. Sends pacote-specific headers (`pacote-version`, `pacote-req-type`, `pacote-pkg-id`, `pacote-integrity`). Does not duplicate caching since `npm-registry-fetch` handles it via make-fetch-happen/cacache.

**Stream handling**: Returns a Minipass stream with `hasIntegrityEmitter` flag set, allowing the base class to piggyback on the fetch layer's integrity events rather than wrapping in a separate integrity stream.
