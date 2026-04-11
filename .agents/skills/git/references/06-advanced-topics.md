# Advanced Topics

This reference covers advanced Git features: stash, tags, blame, bisect, submodules, and other specialized operations.

## Stash

### What is Stash?

Temporarily save changes without committing. Useful for switching branches or pulling updates when you have uncommitted work.

### Basic Stash Operations

```bash
# Save current changes
git stash

# Save with descriptive message
git stash save "WIP: implementing feature X"

# Or (Git 2.23+):
git stash push -m "Work in progress"

# Save untracked files too
git stash -u
git stash --include-untracked

# Save everything including ignored files
git stash --all
```

### View Stashes

```bash
# List all stashes
git stash list

# Show stash contents
git stash show

# Show with diff
git stash show -p

# Show specific stash
git stash show stash@{2}
```

### Apply and Drop Stashes

```bash
# Apply most recent stash (keep in list)
git stash apply

# Apply and remove from list
git stash pop

# Apply specific stash
git stash apply stash@{2}

# Drop (delete) specific stash
git stash drop stash@{2}

# Drop all stashes
git stash clear

# Clear old stashes (older than 7 days)
git reflog expire --expire=7.ago --stashes
```

### Stash Branches

```bash
# Create branch from stash
git stash branch new-feature stash@{1}

# If no stash specified, uses most recent
git stash branch new-feature
```

### Stash Specific Files

```bash
# Stash only specific files
git add file1.js file2.js
git stash push -m "Partial stash" file1.js file2.js

# Or stash everything except specific files
git stash -- file1.js file2.js  # Everything EXCEPT these
```

## Tags

### What are Tags?

Tags mark specific commits, typically for releases. Unlike branches, tags don't move.

### Create Tags

```bash
# Lightweight tag (just a pointer)
git tag v1.0.0

# Annotated tag (recommended for releases)
git tag -a v1.0.0 -m "Release version 1.0.0"

# Tag specific commit
git tag v0.9.0 abc123

# GPG signed tag
git tag -s v1.0.0 -m "Signed release 1.0.0"
```

### List and View Tags

```bash
# List all tags
git tag

# List tags matching pattern
git tag -l "v1.*"

# List with sorting
git tag -l --sort=-version:refname

# Show tag info
git show v1.0.0

# Verify signed tag
git verify-signature v1.0.0
```

### Delete and Move Tags

```bash
# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push origin --delete v1.0.0

# Move tag (use with caution!)
git tag -d v1.0.0
git tag -a v1.0.0 new-commit -m "Updated release"
git push --force --tags
```

### Push Tags

```bash
# Push specific tag
git push origin v1.0.0

# Push all tags
git push origin --tags

# Push tag with branch
git push origin main --tags
```

### Tag Workflows

```bash
# Semantic versioning workflow
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0

# Pre-release tags
git tag -a v1.1.0-beta.1 -m "Beta release"
git tag -a v1.1.0-rc.1 -m "Release candidate"

# After fixes, create final release
git tag -d v1.1.0-beta.1  # Optional: remove beta tag
git tag -a v1.1.0 -m "Final release 1.1.0"
```

## Blame

### What is Blame?

Shows who last modified each line of a file and when. Useful for understanding code history.

### Basic Blame

```bash
# Show blame for file
git blame src/app.js

# Show with line numbers
git blame -n src/app.js

# Show with commit hash
git blame -L src/app.js

# Compact format
git blame --line-porcelain src/app.js | sed -n 's/^author //p'
```

### Blame Options

```bash
# Ignore whitespace changes
git blame -w src/app.js

# Ignore all whitespace
git blame -W src/app.js

# Show function context
git blame -f src/app.js

# Start from specific line
git blame -L 10,20 src/app.js

# From line to end
git blame -L 10 src/app.js

# Blame at specific commit
git blame v1.0.0 -- src/app.js

# Ignore merges (show original author)
git blame -C src/app.js

# Show moves within file
git blame -M src/app.js

# Show moves between files
git blame -C -C src/app.js
```

### Blame Output Example

```
^abc1234 (John Doe 2024-01-15 10:30:45 +0000 1) const app = express();
def5678 (Jane Smith 2024-01-16 14:22:10 +0000 2) app.use(cors());
^abc1234 (John Doe 2024-01-15 10:30:45 +0000 3) 
^abc1234 (John Doe 2024-01-15 10:30:45 +0000 4) app.listen(3000);
```

## Bisect

### What is Bisect?

Binary search through commits to find which commit introduced a bug.

### Start Bisect

```bash
# Start bisect session
git bisect start

# Mark current as bad
git bisect bad

# Mark known good commit
git bisect good v1.0.0

# Or specify both at once
git bisect start
git bisect bad HEAD
git bisect good abc123
```

### Test Midpoint

```bash
# Git checks out midpoint commit
# Run your tests...

# Mark as good
git bisect good

# Mark as bad
git bisect bad

# Repeat until bug is found
```

### Bisect with Command

```bash
# Automatically test each commit
git bisect run ./test-script.sh

# Test script should exit 0 for good, non-zero for bad
# Example test script:
#!/bin/bash
npm test && exit 0 || exit 1

# With grep for specific error
git bisect run bash -c 'grep -q "ERROR" logs/app.log && exit 1 || exit 0'
```

### End Bisect

```bash
# Finish and return to original branch
git bisect reset

# Reset and checkout specific commit
git bisect reset main
```

### Bisect Output

```
Bisecting: 25 revisions left to test after this (roughly 5 steps)
[abc123456789] Commit message here

# After completion:
abc123456789 is the first bad commit
commit abc12345678901234567890123456789012345678
Author: John Doe <john@example.com>
Date:   Mon Jan 15 10:30:45 2024 +0000

    Add new feature

This commit introduced the bug.
```

## Submodules

### What are Submodules?

Submodules embed one repository inside another. Useful for sharing code across projects.

### Add Submodule

```bash
# Add submodule at default path
git submodule add https://github.com/user/library.git

# Add at specific path
git submodule add https://github.com/user/library.git lib/library

# Add specific branch
git submodule add -b main https://github.com/user/library.git lib/library

# Add shallow clone
git submodule add --depth 1 https://github.com/user/library.git
```

### Initialize Submodules

```bash
# After cloning repo with submodules
git submodule update --init

# Recursive (submodules of submodules)
git submodule update --init --recursive

# Update to latest on branch
git submodule update --remote

# Update and merge
git submodule update --merge
```

### Work in Submodule

```bash
# Change into submodule directory
cd lib/library

# Make changes, commit, push
git add .
git commit -m "Update library"
git push origin main

# Return to superproject
cd ../..

# Commit the submodule update
git add lib/library
git commit -m "Update library submodule"
```

### List and Status

```bash
# List all submodules
git submodule status

# Show with recursive status
git submodule status --recursive

# Init status (which are initialized)
git submodule status --init
```

### Remove Submodule

```bash
# 1. Remove from tracking
git rm --cached path/to/submodule

# 2. Remove submodule config
git config -f .gitmodules --remove-section submodule.path/to/submodule

# 3. Remove submodule git dir
rm -rf .git/modules/path/to/submodule

# 4. Commit changes
git commit -m "Remove submodule"
```

### Submodule Commands

```bash
# Sync URL (after upstream changes URL)
git submodule sync

# Set to specific branch
git submodule set-branch --branch develop path/to/submodule

# Update all submodules
git submodule update --init --recursive --remote

# Add all submodule changes to index
git add -U
```

## Git Hooks

### What are Hooks?

Scripts that run automatically at specific events (pre-commit, post-commit, etc.).

### Hook Locations

- Local hooks: `.git/hooks/`
- Template hooks: Configurable via `init.templateDir`

### Common Hooks

```bash
# pre-commit: Runs before commit message is edited
# Return non-zero to abort commit
.git/hooks/pre-commit

# prepare-commit-msg: Modify commit message before editor opens
.git/hooks/prepare-commit-msg

# commit-msg: Validate commit message format
.git/hooks/commit-msg

# post-commit: Run after commit (cannot abort)
.git/hooks/post-commit

# pre-push: Run before pushing, can abort push
.git/hooks/pre-push
```

### Example: Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check for trailing whitespace
if git diff --cached --diff-filter=d | grep -q '[[:space:]]$'; then
    echo "Error: Trailing whitespace found"
    exit 1
fi

# Run linting
npm run lint || exit 1

# Run tests (optional, can be slow)
# npm test || exit 1

exit 0
```

### Example: Commit Message Hook

```bash
#!/bin/bash
# .git/hooks/commit-msg

# Enforce conventional commits
COMMIT_MSG=$(cat "$1")
if ! echo "$COMMIT_MSG" | grep -Eq '^(feat|fix|docs|style|refactor|test|chore): '; then
    echo "Error: Commit message must follow conventional commits format"
    echo "Example: feat: add new feature"
    exit 1
fi

exit 0
```

### Share Hooks Across Team

```bash
# Create shared hooks directory
mkdir -p .githooks

# Add hooks to repository (not in .git/hooks)
cat > .githooks/pre-commit << 'EOF'
#!/bin/bash
npm run lint
EOF

chmod +x .githooks/pre-commit

# In documentation, instruct team to:
# ln -s ../../.githooks/pre-commit .git/hooks/pre-commit
```

## Git Attributes

### What are Git Attributes?

Define how files should be treated (line endings, binary detection, etc.).

### Create .gitattributes

```bash
# Define attributes for file types
cat > .gitattributes << 'EOF'
# Line endings
*.sh text eol=lf
*.bat text eol=crlf
*.ps1 text eol=crlf

# Binary files
*.png binary
*.jpg binary
*.pdf binary

# Diff drivers
*.md diff=markdown

# Export ignore (don't include in exports)
*.md~ export-ignore
EOF
```

### Common Attributes

| Attribute | Description |
|-----------|-------------|
| `text` | Text file, convert line endings |
| `binary` | Binary file, no conversion |
| `eol=lf` | Use LF line endings |
| `eol=crlf` | Use CRLF line endings |
| `diff=<driver>` | Use custom diff driver |
| `merge=<driver>` | Use custom merge driver |
| `export-ignore` | Don't include in git archive/export |
| `linguist-*` | Language detection overrides |

### Line Ending Management

```bash
# Global config for line endings
git config --global core.autocrlf true    # Windows
git config --global core.autocrlf input   # Unix/Mac
git config --global core.autocrlf false   # No conversion

# In .gitattributes:
* text=auto                    # Auto-detect text files
*.sh text eol=lf              # Force LF for shell scripts
```

## Performance Tips

### Large Repositories

```bash
# Shallow clone (only recent history)
git clone --depth 1 https://github.com/user/large-repo.git

# Clone single branch
git clone --branch main --single-branch https://github.com/user/repo.git

# Partial clone (blobs on demand)
git clone --filter=blob:none https://github.com/user/large-repo.git

# Sparse checkout (only specific directories)
git clone --filter=blob:none --no-checkout https://github.com/user/repo.git
cd repo
git sparse-checkout set src/my-directory
git checkout main
```

### Optimize Repository

```bash
# Clean up unreachable objects
git gc --prune=now --aggressive

# Repack for efficiency
git repack -a -d -f

# Count objects
git count-objects -vH

# Check disk usage
du -sh .git/
```

### Fast Operations

```bash
# Faster log (limit ref resolution)
git log --no-walk

# Faster grep
git grep -e "pattern" -- "*.js"

# Faster status (don't scan untracked)
git status --untracked-files=no

# Faster diff (binary files)
git diff --binary
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Stash conflicts on apply | Resolve manually, then `git stash drop` |
| Tag already exists | `git tag -d <tag>` then recreate |
| Bisect can't find bug | Check test reliability, use `git bisect visualize` |
| Submodule out of sync | `git submodule update --init --recursive` |
| Hook not running | Check permissions: `chmod +x .git/hooks/<hook>` |

## Best Practices

1. **Use annotated tags** for releases - They contain metadata and can be signed
2. **Stash sparingly** - Prefer proper commits for significant work
3. **Bisect with automated tests** - Manual bisect is error-prone
4. **Document submodule usage** - Team needs to know how to initialize them
5. **Share hooks via documentation** - Don't commit to `.git/hooks/` directly
6. **Use .gitattributes early** - Prevent line ending issues before they start
7. **Monitor repository size** - Run `git gc` periodically on large repos
