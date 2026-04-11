# Repository Basics

This reference covers initializing new repositories, cloning existing ones, and basic Git configuration.

## Initializing a Repository

### Create New Repository

```bash
# Initialize in current directory
git init

# Initialize in specific directory
git init my-project

# Initialize as bare repository (for shared repos)
git init --bare /path/to/repo.git
```

### What `git init` Does

- Creates a `.git/` directory containing:
  - `objects/` - Compressed file contents
  - `refs/` - Branch and tag references
  - `HEAD` - Points to current branch
  - `config` - Repository-specific settings
  - `index` - Staging area

### Initializing with Default Branch Name

```bash
# Set default branch to main (Git 2.28+)
git init --initial-branch=main my-project

# Or configure globally
git config --global init.defaultBranch main
```

## Cloning Repositories

### Clone from Remote

```bash
# HTTPS clone
git clone https://github.com/user/repo.git

# SSH clone
git clone git@github.com:user/repo.git

# Clone to specific directory
git clone https://github.com/user/repo.git my-directory

# Shallow clone (only latest commit)
git clone --depth 1 https://github.com/user/repo.git

# Clone specific branch
git clone -b develop https://github.com/user/repo.git

# Bare clone (no working directory)
git clone --bare https://github.com/user/repo.git repo.git
```

### Clone Submodules

```bash
# Clone with submodules recursively
git clone --recursive https://github.com/user/repo.git

# Or initialize existing submodules
git clone https://github.com/user/repo.git
cd repo
git submodule update --init --recursive
```

## Git Configuration

### User Identity (Required)

```bash
# Set globally (recommended)
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# Set per-repository
git config user.name "Project Name"
git config user.email "project@example.com"
```

### Common Global Settings

```bash
# Default editor
git config --global core.editor "code --wait"  # VS Code
git config --global core.editor "vim"          # Vim
git config --global core.editor "nano"         # Nano

# Default branch name
git config --global init.defaultBranch main

# Preferred merge tool
git config --global merge.tool vimdiff

# Alias for common commands
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.last "log -1 HEAD"
```

### Push Configuration

```bash
# Default push current branch to matching remote branch
git config --global push.default current

# Or match all branches (safer for shared repos)
git config --global push.default matching

# Force lexicographic ordering in git ls-files
git config --global ls-files.compatibility true
```

### Viewing Configuration

```bash
# View all config (system, global, local)
git config --list

# View specific setting
git config user.name

# View where setting is defined
git config --show-scope user.name

# View local repo config only
git config --local --list
```

### Config Files Locations

- System-wide: `/etc/gitconfig`
- Global (user): `~/.gitconfig` or `~/.config/git/config`
- Local (repository): `.git/config`

## Ignoring Files

### Creating .gitignore

```bash
# Create .gitignore in repository root
echo "node_modules/" > .gitignore
echo "*.log" >> .gitignore
echo ".env" >> .gitignore
```

### Common .gitignore Patterns

```gitignore
# Dependencies
node_modules/
vendor/
__pycache__/
*.pyc

# Environment files
.env
.env.local
.env.*.local

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*

# Build outputs
dist/
build/
*.exe
*.o
```

### Gitignore Pattern Rules

| Pattern | Meaning |
|---------|---------|
| `*.o` | Matches any file ending in .o |
| `/docs/` | Only matches docs/ at root |
| `docs/` | Matches docs/ anywhere |
| `!*.txt` | Negates - includes .txt files |
| `**/test/` | Matches test/ at any depth |

### Removing Tracked Files from Git (Keep Locally)

```bash
# Remove from tracking but keep file
git rm --cached filename

# Remove multiple files
git rm --cached *.log
git rm --cached node_modules/

# Then commit
git commit -m "Stop tracking log files"
```

## Repository Inspection

### Check Repository Status

```bash
# See which files are tracked
git ls-files

# See untracked files
git ls-files --others --exclude-standard

# See repository size
du -sh .git/
```

### View Remote URLs

```bash
# List all remotes
git remote -v

# Add a remote
git remote add origin https://github.com/user/repo.git

# Change remote URL
git remote set-url origin https://github.com/user/repo.git
```

## Best Practices

1. **Always configure user identity** before making commits
2. **Use meaningful branch names**: `feature/add-login`, `fix/bug-123`
3. **Create .gitignore early** to avoid committing unwanted files
4. **Use shallow clones** for large repos you only need to view
5. **Set up sensible aliases** to speed up common operations
6. **Document custom configurations** in your README

## Migration from Other VCS

### Import from SVN

```bash
# Install git-svn if needed
git svn clone svn://svn.example.com/repo/trunk
```

### Import from Mercurial

```bash
# Use hg-fast-export or similar tools
hg fast-export | git fast-import
```
