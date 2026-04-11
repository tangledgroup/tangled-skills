# Git Setup and Initialization

## Initial Configuration

### Required Identity Setup

Before making commits, configure your identity:

```bash
# Set your name (appears in commit history)
git config --global user.name "Your Full Name"

# Set your email (used for attribution and notifications)
git config --global user.email "you@example.com"

# Verify configuration
git config --list
```

### Common Global Settings

```bash
# Default text editor
git config --global core.editor "code --wait"  # VS Code
git config --global core.editor "nvim"         # Neovim
git config --global core.editor "vim"          # Vim

# Default branch name for new repositories
git config --global init.defaultBranch main

# Show color in output
git config --global color.ui auto

# Alias for common commands
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.last "log -1 HEAD"
```

### Credential Storage (Recommended)

```bash
# Store credentials in memory for 15 minutes
git config --global credential.helper cache

# Store credentials permanently (Linux/macOS)
git config --global credential.helper store

# Use OS keychain (macOS)
git config --global credential.helper osxkeychain

# Use OS keychain (Windows)
git config --global credential.helper wincred
```

## Creating New Repositories

### Initialize in Current Directory

```bash
# Create new repository
git init

# Creates .git directory with all tracking infrastructure
# No commits yet - just an empty repository
```

### Initialize from Tarball/Existing Files

```bash
# Extract project files
tar xzf project.tar.gz
cd project

# Initialize repository
git init

# Add all files to staging area
git add .

# Create initial commit
git commit -m "Initial import of project"
```

### Clone Existing Repositories

```bash
# HTTPS (requires authentication for private repos)
git clone https://github.com/user/repository.git

# SSH (requires SSH key setup)
git clone git@github.com:user/repository.git

# Clone to specific directory
git clone https://github.com/user/repo.git my-project-folder

# Shallow clone (only latest commit - faster)
git clone --depth 1 https://github.com/user/repo.git

# Clone single branch only
git clone --branch main --single-branch https://github.com/user/repo.git

# Bare clone (for server/repository hosting)
git clone --bare https://github.com/user/repo.git repo.git
```

### Initialize as Submodule

```bash
# Add existing repository as submodule
git submodule add https://github.com/user/lib-repo.git libs/mylib

# Initialize and update all submodules after cloning
git submodule update --init --recursive
```

## Repository Structure

```
my-project/
├── .git/                    # Git metadata (hidden)
│   ├── HEAD                 # Points to current branch
│   ├── config               # Repository-specific settings
│   ├── objects/             # Compressed file contents
│   ├── refs/                # Branch and tag references
│   └── index                # Staging area snapshot
├── README.md
├── src/
├── package.json
└── .gitignore              # Files to ignore
```

## .gitignore Configuration

### Create gitignore File

```bash
# Create from template (e.g., Node.js)
curl https://raw.githubusercontent.com/github/gitignore/main/Node.gitignore > .gitignore

# Or create manually
cat > .gitignore << 'EOF'
# Dependencies
node_modules/

# Environment files
.env
.env.local

# Build outputs
dist/
build/

# IDE
.vscode/
.idea/

# OS files
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*
EOF
```

### Common Patterns

```gitignore
# Ignore all .log files
*.log

# Ignore node_modules directory
node_modules/

# Ignore .env but not .env.example
.env
!.env.example

# Ignore everything except README.md
*
!README.md

# Directory-specific ignores
logs/
temp/
**/test-output/
```

### Verify What's Ignored

```bash
# Check if file is ignored
git check-ignore -v filename

# See status including ignored files
git status --ignored

# Force add ignored file (use carefully)
git add -f ignored-file.txt
```

## Best Practices

1. **Configure identity early** - Set name and email before first commit
2. **Use .gitignore from day one** - Prevent clutter in repository
3. **Choose appropriate remote** - HTTPS for public, SSH for private repos
4. **Shallow clones for large repos** - Faster initial download with `--depth 1`
5. **Verify branch name** - Set `init.defaultBranch` to avoid "master" vs "main" confusion

## Verification Commands

```bash
# Check Git version
git --version

# View configuration
git config --list --show-origin

# Test identity
git config user.name
git config user.email

# Check repository status
git status

# Verify remote URL
git remote -v
```
