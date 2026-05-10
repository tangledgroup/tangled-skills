---
name: pacote-21-5-0
description: Use pacote 21.5 via npx to inspect, download, and extract npm packages without installing them first. Supports registry packages, git repositories, local files, directories, and remote tarballs for package inspection, dependency analysis, manifest retrieval, security verification with Sigstore attestations, and offline extraction workflows.
version: "0.1.0"
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
  - sigstore
  - attestation
category: tooling
external_references:
  - https://www.npmjs.com/package/pacote
  - https://github.com/npm/pacote
compatibility: Node.js ^20.17.0 || >=22.9.0
---

# pacote 21.5

## Overview

pacote is the JavaScript package handler used internally by the npm CLI. It fetches package manifests, packuments, and tarballs from any source that npm can install — registry specs (`foo@1.x`), git repositories (`github:user/project`), local files (`./package.tgz`), directories (`./my-package`), and remote URLs (`https://example.com/pkg.tgz`).

Version 21.5 is the latest release (as of 2026-03-09), requiring Node.js `^20.17.0 || >=22.9.0`. It adds Sigstore attestation verification, registry signature validation, granular fetch-type allowlists (`allowGit`, `allowRemote`, `allowFile`, `allowDirectory`, `allowRegistry`), git-subdir support per the npa spec, and git-256 SHA length support.

Because pacote is what npm itself uses under the hood, anything you can pass to `npm install` you can pass to pacote. It provides a unified API across all package source types — resolve, extract, manifest, packument, and tarball operations work identically regardless of whether the source is a registry, git repo, file, directory, or remote URL.

## When to Use

- Inspecting npm packages without installing them (manifest, packument lookups)
- Downloading and extracting package tarballs programmatically
- Resolving version specifiers to exact tarball URLs
- Analyzing package dependencies and metadata at build time
- Verifying package integrity with SRI hashes and Sigstore attestations
- Working with git-hosted packages (github:, gitlab:, bitbucket: shortcuts)
- Packing local directories into npm-compatible tarballs
- Building custom installers, lockfile generators, or package analysis tools
- Offline-first workflows where packages need to be pre-fetched and cached

## Core Concepts

**Package specifiers**: pacote accepts any specifier that `npm-package-arg` understands. This includes registry specs (`lodash@4.x`, `express@latest`), git URLs (`github:npm/cli`, `git+ssh://git@github.com/user/repo.git#v1.0.0`), file paths (`./package.tgz`, `file:../my-package`), directory paths (`./packages/my-lib`), and remote URLs (`https://cdn.example.com/pkg-1.0.0.tgz`).

**Fetcher types**: Internally, pacote dispatches to one of five fetcher classes based on the specifier type: `RegistryFetcher` (registry specs), `GitFetcher` (git repos), `FileFetcher` (local tarballs), `DirFetcher` (local directories), and `RemoteFetcher` (URLs). All expose the same API surface.

**Manifests vs packuments**: A manifest is the package metadata for a single version (essentially `package.json` plus `_resolved`, `_integrity`, `_from`). A packument is the full registry document listing all versions, dist-tags, and timestamps for a package name.

**Integrity verification**: pacote computes and verifies Subresource Integrity (SRI) hashes using ssri. Default algorithm is sha512. Mismatched integrity raises `EINTEGRITY` errors. Git dependencies skip integrity checks per npm/rfcs#525.

**Caching**: All fetches are cached via cacache. The default cache location matches npm's platform-specific default. Cache entries are validated by integrity hash, and corrupted cache data triggers automatic refresh.

## CLI Usage

Run pacote from the command line using npx:

```bash
# Resolve a specifier to its tarball URL
npx pacote resolve lodash@4.x

# Resolve with full details (integrity, from)
npx pacote resolve --long express@latest

# Fetch and print package manifest as JSON
npx pacote manifest chalk@5

# Fetch full packument (all versions, dist-tags)
npx pacote packument react

# Download tarball to a file
npx pacote tarball typescript@5 ./typescript.tgz

# Stream tarball to stdout
npx pacote tarball axios@1 -

# Extract a package into a folder
npx pacote extract github:npm/cli /tmp/npm-cli
```

CLI configuration values match npm option names. Additional flags:

- `--long` — Print an object from `resolve`, including integrity and spec
- `--json` — Print result objects as JSON (default when stdout is not a TTY)
- `--cache=/path` — Use custom cache directory
- `--registry=https://reg.example.com/` — Use custom registry
- `--before=2024-01-01` — Only consider versions published before date

## API Reference

All API methods return Promises. The `spec` parameter accepts any npm-compatible specifier string. The `opts` parameter is an options object (detailed in reference files).

```js
import pacote from 'pacote'

// Resolve spec to tarball URL or file path
const resolved = await pacote.resolve('lodash@4.x', opts)
// → 'https://registry.npmjs.org/lodash/-/lodash-4.17.21.tgz'

// Extract package tarball into a directory
const result = await pacote.extract('github:npm/cli', '/tmp/npm-cli', opts)
// → { from, resolved, integrity }

// Fetch package manifest (package.json + metadata)
const manifest = await pacote.manifest('chalk@5', opts)
// → { name, version, _resolved, _integrity, _from, ... }

// Fetch full packument (all versions and dist-tags)
const packument = await pacote.packument('react', opts)
// → { name, versions: { '18.0.0': manifest, ... }, 'dist-tags': { latest: '...' } }

// Get tarball data as a Buffer in memory
const buf = await pacote.tarball('express@4', opts)
// → Buffer with .from, .resolved, .integrity properties

// Save tarball to a file
await pacote.tarball.file('lodash@4.x', './lodash.tgz', opts)
// → { from, resolved, integrity }

// Stream tarball through a handler function
await pacote.tarball.stream('axios@1', (stream) => {
  return new Promise((resolve, reject) => {
    stream.pipe(someWriter)
    someWriter.on('finish', resolve)
    stream.on('error', reject)
  })
}, opts)
```

## Advanced Topics

**Fetcher Types and Spec Resolution**: Deep dive into the five fetcher classes — RegistryFetcher, GitFetcher, FileFetcher, DirFetcher, RemoteFetcher — and how pacote dispatches based on specifier type → [Fetcher Architecture](reference/01-fetcher-architecture.md)

**Options Reference**: Complete reference of all configuration options including cache settings, integrity verification, security allowlists, registry customization, and file mode controls → [Options Reference](reference/02-options-reference.md)

**Security and Verification**: Sigstore attestation verification, registry signature validation, SRI integrity checks, TUF key retrieval, and the allowX family of options for controlling fetch sources → [Security and Verification](reference/03-security-verification.md)
