# Security and Verification

pacote 21.5 provides multiple layers of package integrity and authenticity verification, from basic SRI hash checking to full Sigstore attestation validation.

## Subresource Integrity (SRI)

Every fetched tarball is verified against its Subresource Integrity hash. pacote uses the `ssri` library for parsing, computing, and comparing integrity values.

**How it works**: When fetching from the registry, the packument's `dist.integrity` field provides the expected SRI string. If not present (older packages), `dist.shasum` (hex-encoded sha1) is converted to an SRI string. During tarball download or cache retrieval, cacache and npm-registry-fetch compute the actual hash and compare it against the expected value. Mismatch raises an `EINTEGRITY` error with automatic cache cleanup and retry.

**Default algorithm**: sha512. Can be overridden via `opts.defaultIntegrityAlgorithm`.

**Multiple algorithms**: ssri supports multiple hash algorithms in a single integrity string. When merging integrity values (e.g., from lockfile and registry), pacote merges new algorithms rather than replacing existing ones. Conflict detection only triggers when the same algorithm produces different hashes.

```js
// Verify with expected integrity
const manifest = await pacote.manifest('lodash@4.17.21', {
  integrity: 'sha512-qLM8OBqmFkEkHAmBiorXpvBLPzquCvZlH1PPu2jjzA0WX3Y24bmpLgIcbFWjYw0ppRNeXU8T/5WusV5vo2yMqw=='
})
```

**Git dependencies**: Integrity checks are explicitly skipped for git-sourced packages (per npm/rfcs#525). Any `opts.integrity` is silently removed in GitFetcher's constructor.

## Registry Signature Verification

npm registry publishes signatures alongside package tarballs. pacote can verify these signatures when `verifySignatures: true` is set.

**How it works**: The manifest's `dist.signatures` array contains signature objects with `keyid` and `sig` fields. pacote looks up the corresponding public key from the registry's keys endpoint (`/-/npm/v1/keys`) using the configured `_keys` option. It verifies the SHA256 signature over the message `name@version:integrity`.

**Key validation**: Public keys are checked for expiration against the package publish time. Expired keys raise `EEXPIREDSIGNATUREKEY`. Missing keys raise `EMISSINGSIGNATUREKEY`.

**Error codes**:
- `EINTEGRITYSIGNATURE` — Signature verification failed
- `EMISSINGSIGNATUREKEY` — No public key found for the signature's keyid
- `EEXPIREDSIGNATUREKEY` — Public key has expired

```js
const manifest = await pacote.manifest('some-package@1.0.0', {
  verifySignatures: true,
  '//registry.npmjs.org/:_keys': [
    { keyid: 'SHA256:...', pemkey: '-----BEGIN PUBLIC KEY...\n...' }
  ]
})
// manifest._signatures contains verified signatures
```

## Sigstore Attestation Verification

As of pacote 21.x, Sigstore attestations can be verified when `verifyAttestations: true` is set. This provides cryptographic proof of package provenance using the Sigstore framework.

**How it works**: When the registry includes `dist.attestations`, pacote fetches the attestation bundles and verifies each one using the `sigstore` library (v4.0.0). Two types of attestations are supported:

1. **Key-based attestations** (publish attestations): Signed with a keyid that maps to a registry public key. Requires `_keys` configuration. The key's expiration is checked against the attestation's integrated timestamp from the transparency log.

2. **Keyless attestations** (Sigstore/Fulcio): Self-contained bundles with embedded signing certificates. No registry keys required — the certificate chain is verified against Fulcio roots and the transparency log (Rekor).

**Verification steps**:
1. Fetch attestation bundles from the registry
2. Parse the DSSE envelope payload to extract the statement
3. Verify the statement subject matches the package PURL (`pkg:npm/name@version`)
4. Verify the statement subject's sha512 digest matches the tarball integrity
5. Call `sigstore.verify(bundle, options)` with TUF cache and key selector

**TUF integration**: Attestation key material (Fulcio certificates, Rekor logs) is retrieved via The Update Framework (TUF). The `tufCache` option controls where TUF metadata is stored.

**Error codes**:
- `EATTESTATIONSUBJECT` — Statement subject doesn't match package name/version or integrity
- `EATTESTATIONVERIFY` — Sigstore verification failed
- `EMISSINGSIGNATUREKEY` — Keyed attestation but no corresponding public key found
- `EEXPIREDSIGNATUREKEY` — Public key expired relative to integrated timestamp

**Exposed data**: As of 21.5.0, fetched attestation bundles are exposed on the manifest as `_attestationBundles` when verification is enabled, along with `_attestations` pointing to the registry attestations URL.

```js
const manifest = await pacote.manifest('some-package@1.0.0', {
  verifyAttestations: true,
  tufCache: '/path/to/tuf-cache'
})
// manifest._attestations — registry attestations reference
// manifest._attestationBundles — verified bundle objects (21.5.0+)
```

## Fetch Source Allowlists

pacote 21.x introduces granular control over which package source types are allowed to be fetched. This enables security policies that restrict certain fetch methods in production or CI environments.

**allowGit** (`'all'` | `'none'` | `'root'`) — Controls git spec fetching. Default: `'all'`. Set to `'none'` to block all git dependencies (common in production lockfile installs).

**allowRemote** (`'all'` | `'none'` | `'root'`) — Controls remote URL fetching. Default: `'all'`.

**allowFile** (`'all'` | `'none'` | `'root'`) — Controls local file spec fetching. Default: `'all'`.

**allowDirectory** (`'all'` | `'none'` | `'root'`) — Controls directory spec fetching. Default: `'all'`.

**allowRegistry** (`'all'` | `'none'` | `'root'`) — Controls registry spec fetching. Added in 21.4.0.

When a fetch is blocked, pacote throws an error with code `EALLOWGIT`, `EALLOWREMOTE`, `EALLOWFILE`, `EALLOWDIRECTORY`, or `EALLOWREGISTRY` respectively, including the package specifier.

```js
// Production install: block git and remote, allow registry only
await pacote.extract('my-app@1.0.0', '/tmp/app', {
  allowGit: 'none',
  allowRemote: 'none',
  _isRoot: true // root deps can still use all types if configured as 'root'
})

// CI policy: only root (direct) deps allowed from git
await pacote.manifest('github:user/repo', {
  allowGit: 'root',
  _isRoot: false // throws EALLOWGIT for non-root deps
})
```

## Cache Integrity

pacote's caching layer uses cacache which stores content by digest. On cache read, the stored integrity is verified. If corruption is detected (`EINTEGRITY` or `Z_DATA_ERROR`), pacote:

1. Logs a warning about corrupted cached data
2. Removes the corrupted cache entry via `cacache.rm.content()`
3. Retries the fetch from the resolved source
4. Stores the fresh data with verified integrity

This ensures that even if disk corruption occurs, pacote will recover transparently rather than serving corrupted package data.

## File Ownership Safety

When running as root on Unix systems, extracted files and folders have their uid/gid set to match the containing folder's ownership. This prevents root-owned files from appearing in `node_modules` when running `sudo npm install`.

The tar extraction always sets `preserveOwner: false` to ignore ownership metadata from the tarball itself.
