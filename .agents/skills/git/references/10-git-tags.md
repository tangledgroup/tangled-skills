# Git Tags

## Understanding Tags

Tags are fixed pointers to specific commits, typically used for marking release versions. Unlike branches, tags don't move.

```bash
# Tags point to specific commits permanently
v1.0.0 ──→ Commit abc1234 (release point)
v1.1.0 ──→ Commit def5678 (later release)
```

## Tag Types

### Lightweight Tags

```bash
# Create lightweight tag (just a pointer)
git tag v1.0.0

# On specific commit
git tag v0.9.0 abc1234

# List all tags
git tag

# View tag info
git show v1.0.0
```

### Annotated Tags (Recommended for Releases)

```bash
# Create annotated tag with message
git tag -a v1.0.0 -m "Release version 1.0.0"

# With GPG signature (requires GPG key setup)
git tag -s v1.0.0 -m "Signed release 1.0.0"

# Interactive message entry
git tag -a v1.0.0
# Opens editor for tag message

# View annotated tag details
git show v1.0.0
```

### Tag Comparison

| Feature | Lightweight | Annotated |
|---------|-------------|-----------|
| Storage | Just pointer | Full object in Git |
| Message | No | Yes |
| Signature | No | Optional GPG |
| Creator info | No | Yes |
| Use case | Personal markers | Official releases |

## Creating Tags

### Version Numbering Schemes

```bash
# Semantic Versioning (SemVer)
git tag -a v1.0.0 -m "Major release"
git tag -a v1.1.0 -m "Minor feature addition"
git tag -a v1.1.1 -m "Patch fix"

# Calendar versioning
git tag -a 2024.01.15 -m "January 2024 release"

# Build numbers
git tag -a build-1234 -m "CI build 1234"

# Pre-release tags
git tag -a v2.0.0-alpha
git tag -a v2.0.0-beta.1
git tag -a v2.0.0-rc1
```

### Tag Best Practices

```bash
# Include 'v' prefix (common convention)
git tag v1.0.0  # Good
git tag 1.0.0   # Less common

# Use descriptive messages
git tag -a v1.0.0 -m "Production release: user auth, dashboard, API v2"

# Sign important releases
git tag -s v1.0.0 -m "Signed production release"
```

## Listing and Viewing Tags

### List Tags

```bash
# All tags
git tag

# Sorted alphabetically
git tag --sort=version:refname

# Filter by pattern
git tag -l 'v1.*'      # All v1.x.x tags
git tag -l 'v2.0.*'    # All v2.0.x tags
git tag -l '*-beta'    # All beta tags

# With creation date
git tag -l --sort=creatordate

# Show tagged commits
git tag -l --points-at HEAD  # Tags on current commit
```

### View Tag Information

```bash
# Show tag and commit
git show v1.0.0

# Just tag info (annotated tags only)
git cat-file tag v1.0.0

# Verify GPG signature
git verify-tag v1.0.0

# See what's between tags
git log v1.0.0..v1.1.0 --oneline
```

## Working with Tags

### Checkout Tag (Read-Only)

```bash
# Detached HEAD at tag
git checkout v1.0.0

# View without switching
git show v1.0.0:src/app.js

# Create branch from tag
git switch -c release-branch v1.0.0
```

### Tag Current Commit

```bash
# Quick tag for current HEAD
git tag -a hotfix-2024-01-15 -m "Emergency fix deployed"

# After fixing tagging mistake
git tag -d wrong-tag-name
git tag -a correct-tag -m "Proper message"
```

### Move Tag (Use Carefully!)

```bash
# Delete and recreate (only if tag not pushed)
git tag -d v1.0.0
git tag -a v1.0.0 new-commit-hash -m "Updated release tag"

# WARNING: Don't move published tags!
```

## Pushing and Fetching Tags

### Push Tags to Remote

```bash
# Push specific tag
git push origin v1.0.0

# Push all tags
git push --tags origin

# Push with branch
git push origin main --tags

# Push single tag with force (if already exists)
git push -f origin v1.0.0
```

### Fetch Tags from Remote

```bash
# Fetch all tags
git fetch --tags

# Fetch specific tag
git fetch origin tag v1.0.0

# Fetch with prune (remove deleted tags)
git fetch --tags --prune
```

### Delete Tags

```bash
# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push origin --delete v1.0.0

# Delete multiple tags
git tag -d v1.0.0 v1.0.1 v1.0.2

# Delete remote pattern (Git 2.5+)
git push origin --delete-tags '*-beta'
```

## Tag Workflows

### Release Workflow

```bash
# 1. Ensure on correct branch at release commit
git switch main
git log --oneline -5

# 2. Create annotated tag
git tag -a v1.2.3 -m "Release 1.2.3: New features and bug fixes"

# 3. Sign if important
git tag -s v1.2.3 -m "Signed release 1.2.3"

# 4. Push tag to remote
git push origin v1.2.3

# 5. Verify on remote
git ls-remote --tags origin | grep v1.2.3
```

### Hotfix Workflow

```bash
# 1. Create hotfix branch from tag
git switch -c hotfix/v1.0.1 v1.0.0

# 2. Make fix and commit
git add . && git commit -m "Fix critical bug"

# 3. Tag the hotfix
git tag -a v1.0.1 -m "Hotfix: Critical security patch"

# 4. Merge to main and develop
git switch main
git merge hotfix/v1.0.1
git tag -a v1.0.1 -m "Hotfix merged to main"

# 5. Push everything
git push origin main hotfix/v1.0.1 --tags
```

### Release Candidate Workflow

```bash
# 1. Create RC tag
git tag -a v2.0.0-rc1 -m "Release candidate 1"

# 2. Test, find bugs, fix them

# 3. Create next RC
git tag -d v2.0.0-rc1
git tag -a v2.0.0-rc2 -m "Release candidate 2: Fixed issues from RC1"

# 4. Final release
git tag -a v2.0.0 -m "Final release 2.0.0"
git push origin --tags
```

## GPG Signed Tags

### Setup GPG Key

```bash
# List available keys
gpg --list-keys

# Generate new key (if needed)
gpg --full-generate-key

# Add to git configuration
git config --global user.signingkey KEY_ID
git config --global commit.gpgSign true
```

### Create Signed Tag

```bash
# Sign tag
git tag -s v1.0.0 -m "Signed release"

# Git prompts for GPG passphrase

# Verify signature
git verify-tag v1.0.0

# Output shows:
# gpg: Signature made Mon Jan 15 12:00:00 2024 EST
# gpg:                using RSA key KEY_ID
# gpg: Good signature from "Name <email>"
```

## Describing Commits with Tags

### Find Nearest Tag

```bash
# Describe current commit
git describe --tags

# With distance from tag
git describe --tags --always

# Long format (tag-distance-commit)
git describe --long --tags

# Example output: v1.0.0-5-gabc1234
# Means: 5 commits after v1.0.0, commit abc1234
```

### Custom Descriptions

```bash
# Abbreviated hash
git describe --abbrev=4 --tags

# Match pattern only
git describe --tags 'v[0-9]*'

# Always show something (even if no tag)
git describe --always --dirty  # Shows working tree status
```

## Tag Maintenance

### Cleanup Old Tags

```bash
# List tags to remove
git tag -l '*-alpha'
git tag -l '*-beta'
git tag -l '*-rc*'

# Delete locally
git tag -d v1.0.0-alpha v1.0.0-beta

# Delete from remote
git push origin --delete v1.0.0-alpha v1.0.0-beta

# Prune fetched tags
git fetch --tags --prune
```

### Verify Tag Integrity

```bash
# Check all tag signatures
for tag in $(git tag -l 'v*'); do
  echo "Verifying $tag"
  git verify-tag "$tag" || echo "FAILED: $tag"
done

# List unsigned tags
git for-each-ref --format='%(refname)' refs/tags | while read tag; do
  git verify-tag "${tag#refs/tags/}" 2>/dev/null || echo "Unsigned: $tag"
done
```

## Best Practices

1. **Use annotated tags for releases** - Include message and metadata
2. **Sign important tags** - Use GPG for production releases
3. **Follow versioning convention** - SemVer (v1.0.0) is widely adopted
4. **Never move published tags** - Tags should be immutable once shared
5. **Push tags explicitly** - They don't push with branches by default

## Command Cheat Sheet

```bash
# Create tags
git tag v1.0.0                    # Lightweight
git tag -a v1.0.0 -m "message"    # Annotated
git tag -s v1.0.0 -m "message"    # Signed

# List and view
git tag                           # All tags
git tag -l 'v1.*'                 # Filter pattern
git show v1.0.0                   # View tag details

# Push and delete
git push origin --tags            # Push all tags
git push origin v1.0.0            # Push specific tag
git tag -d v1.0.0                 # Delete local
git push origin --delete v1.0.0   # Delete remote

# Describe commits
git describe --tags               # Nearest tag
git describe --long --always      # Detailed description
```

## Troubleshooting

### Tag Already Exists on Remote

```bash
# Force update (only if you own the tag)
git push -f origin v1.0.0

# Or delete and recreate
git push origin --delete v1.0.0
git push origin v1.0.0
```

### Can't Verify Signature

```bash
# Import public key
gpg --recv-keys KEY_ID

# Or check key is available
gpg --list-keys

# Verify manually
git cat-file tag v1.0.0 | gpg
```

### Missing Tags After Clone

```bash
# Fetch all tags
git fetch --tags

# Clone with tags (default behavior)
git clone --tags https://github.com/user/repo.git
```
