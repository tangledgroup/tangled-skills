# Package Manager

Bun's package manager is a Node.js-compatible replacement for npm, yarn, and pnpm — up to 25x faster. It works in existing Node.js projects with no changes needed.

## Core Commands

### `bun install`

Install all dependencies from `package.json`:

```bash
bun install
```

This installs `dependencies`, `devDependencies`, and `optionalDependencies`. Peer dependencies are installed by default. Writes a `bun.lock` lockfile.

As of v1.3.13, `bun install` streams tarballs directly to disk instead of buffering in memory, reducing peak memory usage by ~17x for large dependency trees.

```bash
bun install react              # add a package
bun install react@19.1.1       # specific version
bun install react@latest       # specific tag
bun install --production       # skip devDependencies and optionalDependencies
bun install --frozen-lockfile  # CI mode — fail if lockfile is out of sync
bun install --dry-run          # preview without installing
bun install --verbose          # debug logging
bun install --silent           # no output
```

Omit specific dependency types:

```bash
bun install --omit dev         # skip devDependencies
bun install --omit=dev --omit=peer --omit=optional  # only production deps
```

### `bun add`

Add a package to your project:

```bash
bun add express                # add to dependencies
bun add -d typescript          # add to devDependencies
bun add -o cors                # add to optionalDependencies
bun add -p peer-dep            # add to peerDependencies
bun add git+https://github.com/user/repo.git  # from git
bun add ./local-package        # local path
```

### `bun remove`

```bash
bun remove express
```

### `bun update`

Update packages to latest compatible versions:

```bash
bun update                     # update all
bun update express             # update specific package
```

### `bunx` (alias: `bun x`)

Run packages from npm without explicit installation (~100x faster than `npx`):

```bash
bunx cowsay "Hello world!"
bunx --bun my-cli              # force bun runtime instead of node shebang
bunx -p renovate renovate-config-validator  # binary name differs from package
```

## Publishing

```bash
bun publish                    # publish current package
bun publish --dry-run          # preview
bun publish --access public    # publish scoped package publicly
```

### `bun pm` Commands

```bash
bun pm outdated                # check for outdated packages
bun pm why express             # show dependency tree
bun pm audit                   # security audit
bun pm info express            # package metadata
```

## Workspaces

Configure monorepo workspaces in root `package.json`:

```json
{
  "name": "my-project",
  "version": "1.0.0",
  "workspaces": ["packages/*"]
}
```

Glob patterns are supported, including negation:

```json
{
  "workspaces": ["packages/**", "!packages/**/test/**", "!packages/**/template/**"]
}
```

Reference workspace packages with `workspace:` protocol:

```json
{
  "dependencies": {
    "pkg-b": "workspace:*"     # exact version from package.json
  }
}
```

On publish, `workspace:` versions resolve to actual semver:

- `"workspace:*"` → `"1.0.1"`
- `"workspace:^"` → `"^1.0.1"`
- `"workspace:~"` → `"~1.0.1"`
- `"workspace:1.0.2"` → `"1.0.2"` (explicit override)

Filter workspace operations:

```bash
bun install --filter "pkg-*"          # matching packages
bun install --filter "!pkg-c"         # exclude pkg-c
bun install --filter "./packages/pkg-a"  # path filter
```

## Catalogs

Share dependency versions across workspaces using catalogs:

```json
{
  "catalog": {
    "react": "^18.0.0",
    "typescript": "^5.0.0"
  }
}
```

Then reference in workspace packages with `"catalog"` version:

```json
{
  "dependencies": {
    "react": "catalog"
  }
}
```

## Overrides and Resolutions

Force specific versions for transitive dependencies (supports npm `overrides` and yarn `resolutions`):

```json
{
  "dependencies": {
    "foo": "^2.0.0"
  },
  "overrides": {
    "bar": "~4.4.0"
  }
}
```

## Lifecycle Scripts

Bun does **not** execute lifecycle scripts (`postinstall`, etc.) for installed dependencies by default (security). To allow:

```json
{
  "trustedDependencies": ["my-trusted-package"]
}
```

Re-install after adding to `trustedDependencies`. Scripts run in parallel; adjust concurrency with `--concurrent-scripts`:

```bash
bun install --concurrent-scripts 5
```

## Global Packages

Install CLI tools globally:

```bash
bun install -g cowsay
cowsay "Bun!"
```

## Lockfile

Bun generates `bun.lock` (binary format for speed, with `bun.lockb` as the compiled version). Use `--frozen-lockfile` for reproducible CI installs.

## Global Cache

Bun maintains a global package cache. Packages are downloaded once and linked across projects. The cache location can be configured via `BUN_CACHE_PATH`.

## npmrc Configuration

Standard `.npmrc` file support for registry configuration:

```ini
# .npmrc
registry=https://registry.npmjs.org/
//registry.npmjs.org/:_authToken=NPM_TOKEN
@myscope:registry=https://npm.myscope.com/
```

## Scopes and Registries

Configure per-scope registries in `.npmrc`:

```ini
@myorg:registry=https://npm.myorg.com/
```

Or in `package.json` via `dependencies` with full URLs.
