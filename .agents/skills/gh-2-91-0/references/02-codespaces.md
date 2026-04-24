# GitHub Codespaces

> **Source:** https://cli.github.com/manual/gh_codespace
> **Loaded from:** SKILL.md (via progressive disclosure)

GitHub Codespaces are cloud-hosted development environments. The `gh codespace` command (alias: `gh cs`) lets you create, manage, and connect to them from the terminal.

## Creating Codespaces

```bash
# Create with defaults
gh codespace create

# Specify branch and machine type
gh codespace create --branch main --machine standardLinux32CoreToledoV3

# Custom dev container configuration
gh codespace create --dev-container-path .devcontainer/Dockerfile
gh codespace create --idle-timeout-minute 10

# Clone repo and create codespace
gh codespace create --repo owner/repo
```

## Listing and Viewing

```bash
# List all your codespaces
gh codespace list

# Filter by repository
gh codespace list --repo owner/repo

# View in browser
gh codespace view my-codespace-abc123
gh codespace view --json name,gitStatus,state
```

## Connecting to Codespaces

```bash
# SSH into a codespace
gh codespace ssh my-codespace-abc123

# Copy files to/from codespace
gh codespace cp myfile.txt my-codespace-abc123:~/myfile.txt
gh codespace cp my-codespace-abc123:~/output.txt ./local-output.txt

# Open in VS Code Desktop
gh codespace code my-codespace-abc123

# Open Jupyter notebook
gh codespace jupyter my-codespace-abc123
```

## Port Management

```bash
# List forwarded ports
gh codespace ports list my-codespace-abc123

# Forward a port
gh codespace ports forward 8080 my-codespace-abc123

# Change port visibility
gh codespace ports visibility 8080 public my-codespace-abc123
gh codespace ports visibility 8080 private my-codespace-abc123
```

## Managing Codespaces

```bash
# Edit codespace settings
gh codespace edit my-codespace-abc123 --display-name "My Workspace"

# Rebuild from scratch (preserves files, reinstalls extensions)
gh codespace rebuild my-codespace-abc123

# Stop a running codespace
gh codespace stop my-codespace-abc123

# View logs
gh codespace logs my-codespace-abc123

# Delete permanently
gh codespace delete my-codespace-abc123
```

## Dev Container Integration

Codespaces use dev container configuration. Common files:

- `.devcontainer/devcontainer.json` — Configuration file
- `.devcontainer/Dockerfile` — Custom Docker image
- `.devcontainer/docker-compose.yml` — Multi-container setup

The `--dev-container-path` flag lets you specify a non-standard location for the configuration.
