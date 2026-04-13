# Package Specifier Formats

Complete reference for all supported package specifier formats in pacote.

Pacote supports any package specifier that npm can install, following the [npm-package-arg](https://npm.im/npm-package-arg) specification.

## Registry Packages

Fetch packages from npm registry or compatible registries.

### By Name (Latest Tag)

```bash
npx pacote manifest lodash
npx pacote manifest express
npx pacote manifest react
```

Defaults to the `latest` dist-tag.

### By Exact Version

```bash
npx pacote manifest "lodash@4.17.21"
npx pacote manifest "express@4.18.2"
npx pacote manifest "react@18.2.0"
```

### By Tag

```bash
npx pacote manifest "express@beta"
npx pacote manifest "react@next"
npx pacote manifest "vue@rc"
```

Common tags: `latest`, `beta`, `next`, `rc`, `alpha`, `canary`

### By Version Range

```bash
# Caret range (compatible with)
npx pacote manifest "react@^18.0.0"  # >=18.0.0 <19.0.0

# Tilde range (approximately equivalent)
npx pacote manifest "vue@~3.3.0"     # >=3.3.0 <3.4.0

# Greater than
npx pacote manifest "lodash@>=4.17.0"

# Less than
npx pacote manifest "express@<5.0.0"

# Range
npx pacote manifest "axios@>=1.0.0 <2.0.0"

# Wildcard
npx pacote manifest "chalk@4.*"
```

### Scoped Packages

```bash
npx pacote manifest "@babel/core"
npx pacote manifest "@types/node@latest"
npx pacote manifest "@nestjs/common@^10.0.0"
npx pacote manifest "@scope/package-name@1.2.3"
```

## Git Repositories

Fetch packages directly from git repositories. Pacote runs `prepare` scripts to simulate published packages.

### GitHub

Format: `github:user/repo#commitish`

```bash
# By tag
npx pacote manifest "github:npm/cli#v10.0.0"
npx pacote manifest "github:facebook/react#v18.2.0"

# By branch
npx pacote manifest "github:nvm-sh/nvm#main"
npx pacote manifest "github:expressjs/express#master"

# By commit hash
npx pacote manifest "github:webpack/webpack#a1b2c3d"

# Extract GitHub package
npx pacote extract "github:npm/cli#v10.0.0" ./npm-cli
```

### GitLab

Format: `gitlab:user/repo#commitish`

```bash
npx pacote manifest "gitlab:gitlab-org/gitlab#v16.0.0"
npx pacote manifest "gitlab:namespace/project#main"
```

### Bitbucket

Format: `bitbucket:user/repo#commitish`

```bash
npx pacote manifest "bitbucket:atlassian/atlaskit#v23.0.0"
npx pacote manifest "bitbucket:team/repo#develop"
```

### Direct Git URL

Format: `git+protocol://host/path#commitish`

```bash
# HTTPS
npx pacote manifest "git+https://github.com/nvm-sh/nvm.git#v0.39.0"
npx pacote manifest "git+https://github.com/user/repo.git#main"

# SSH
npx pacote manifest "git+ssh://git@github.com/nvm-sh/nvm.git#main"
npx pacote manifest "git+ssh://git@github.com/user/repo.git#v1.0.0"

# With submodules
npx pacote manifest "git+https://github.com/user/repo.git#commit?depth=1&semver=^1.0.0"
```

### Git Options

Append query parameters to control git behavior:

```bash
# Shallow clone (faster)
npx pacote manifest "github:user/repo#main?depth=1"

# Semver filter
npx pacote manifest "github:user/repo#main?semver=^1.0.0"

# Specific branch with depth
npx pacote manifest "github:user/repo#develop?depth=10"
```

## Tarball URLs

Fetch packages directly from tarball URLs.

### npm Registry Tarballs

```bash
npx pacote manifest "https://registry.npmjs.org/lodash/-/lodash-4.17.21.tgz"
npx pacote manifest "https://registry.npmjs.org/express/-/express-4.18.2.tgz"
```

### Custom Tarball Servers

```bash
npx pacote manifest "https://example.com/packages/my-package.tgz"
npx pacote manifest "https://cdn.example.org/libs/react-18.2.0.tgz"
```

### Local File URLs

```bash
npx pacote manifest "file:///absolute/path/to/package.tgz"
npx pacote manifest "file:./relative/path/package.tgz"
```

## Local Files and Directories

Work with local package.json files or directories.

### Package.json File

Format: `file:path/to/package.json`

```bash
# Absolute path
npx pacote manifest "file:/home/user/project/package.json"

# Relative path
npx pacote manifest "file:./package.json"
npx pacote manifest "file:../sibling-project/package.json"

# Nested path
npx pacote manifest "file:./packages/subpackage/package.json"
```

### Directory with package.json

Format: `file:path/to/folder` or just the path

```bash
# Absolute directory
npx pacote manifest "/home/user/project"
npx pacote manifest "file:/home/user/project"

# Relative directory
npx pacote manifest "./my-package"
npx pacote manifest "../sibling-project"
npx pacote manifest "file:./packages/subpackage"

# Extract local directory as if published
npx pacote extract "./local-package" ./output-folder
```

### Current Directory

```bash
# Package in current directory
npx pacote manifest "."
npx pacote manifest "./"
npx pacote manifest "file:."
```

## Alias Specifiers

Create aliases for packages (npm feature).

Format: `package@alias:target-package@version`

```bash
# Alias lodash to specific version
npx pacote manifest "my-lodash@lodash@4.17.21"

# Alias with scoped package
npx pacote manifest "@myapp/express@express@4.18.2"
```

Note: Alias specifiers are primarily for npm install; pacote resolves them to the target package.

## Special Specifiers

### Git Submodules

```bash
# With submodule support
npx pacote manifest "github:user/repo#commit?submodules=true"
```

### Hosted Git Info Patterns

Pacote recognizes these patterns and converts them appropriately:

| Pattern | Converts To |
|---------|-------------|
| `user/repo` | GitHub `github:user/repo` |
| `gitlab:user/repo` | GitLab repository |
| `bitbucket:user/repo` | Bitbucket repository |
| `pf:organization/repo` | Python Forge (if configured) |

## Specifier Resolution Order

When resolving specifiers, pacote follows this priority:

1. **File paths** - Absolute or relative paths starting with `./`, `../`, or `/`
2. **Git URLs** - URLs starting with `git+` or matching hosted patterns
3. **Tarball URLs** - URLs ending in `.tgz` or `.tar.gz`
4. **Registry packages** - Everything else (name, name@version, @scope/name)

## Examples by Use Case

### Development Dependencies

```bash
# Get latest dev tooling
npx pacote manifest "eslint@latest" --json
npx pacote manifest "@types/node@latest" --json
npx pacote manifest "typescript@~5.3.0" --json
```

### Production Dependencies

```bash
# Pin exact versions
npx pacote manifest "express@4.18.2" --json
npx pacote manifest "react@18.2.0" --json
npx pacote manifest "lodash@4.17.21" --json
```

### Experimental Versions

```bash
# Beta/RC versions
npx pacote manifest "next@canary" --json
npx pacote manifest "react@beta" --json
npx pacote manifest "vue@next" --json
```

### Monorepo Workspaces

```bash
# Access workspace packages
npx pacote manifest "file:./packages/core"
npx pacote manifest "file:./packages/utils"
npx pacote manifest "file:./apps/web"
```

## Validation and Error Handling

### Invalid Specifiers

```bash
# Missing version (valid - uses latest)
npx pacote manifest lodash  # OK

# Malformed git URL
npx pacote manifest "github:invalid"  # Error: Repository not found

# Non-existent package
npx pacote manifest "this-package-does-not-exist-xyz123"  # Error: 404
```

### Common Errors

```bash
# Package not found in registry
Error: 404 Not Found - GET https://registry.npmjs.org/nonexistent

# Git repository not accessible
GitUnknownError: Repository not found
fatal: Could not read from remote repository

# Invalid local path
Error: ENOENT: no such file or directory, open '/path/package.json'

# Invalid tarball URL
Error: 404 Not Found - GET https://example.com/missing.tgz
```

## Tips and Best Practices

1. **Quote complex specifiers** to prevent shell expansion:
   ```bash
   npx pacote manifest "github:user/repo#v1.0.0"  # Correct
   npx pacote manifest github:user/repo#v1.0.0    # May fail
   ```

2. **Use exact versions** for reproducibility:
   ```bash
   npx pacote manifest "lodash@4.17.21"  # Better
   npx pacote manifest "lodash@latest"   # Less reproducible
   ```

3. **Test git access** before relying on it:
   ```bash
   npx pacote manifest "github:user/repo#main" --json
   ```

4. **Verify local paths** are absolute or correctly relative:
   ```bash
   npx pacote manifest "file:./package.json"  # Relative to cwd
   npx pacote manifest "file:/absolute/path"   # Always works
   ```

5. **Check registry availability** for private packages:
   ```bash
   npx pacote --registry=https://private-registry.com manifest @scope/pkg
   ```
