# Codespaces

## Overview

GitHub Codespaces are cloud-hosted development environments. `gh codespace` provides full lifecycle management from the terminal.

## Creating Codespaces

```bash
# Create a codespace interactively
gh codespace create

# Specify branch and machine type
gh codespace create --branch main --machine standardLinux

# Set display name
gh codespace create --display-name "My Dev Environment"

# Set idle timeout
gh codespace create --idle-timeout 30m

# Set retention period after shutdown
gh codespace create --retention-period 24h

# Choose location
gh codespace create --location EastUs

# Use specific devcontainer
gh codespace create --devcontainer-path .devcontainer/docker-compose.yml
```

Available locations: `EastUs`, `SouthEastAsia`, `WestEurope`, `WestUs2`.

## Managing Codespaces

```bash
# List your codespaces
gh codespace list

# View codespace details
gh codespace view

# Stop a codespace
gh codespace stop

# Delete a codespace
gh codespace delete

# Delete all codespaces
gh codespace delete --all

# Delete codespaces older than N days
gh codespace delete --days 7

# Edit codespace settings
gh codespace edit --display-name "New Name"
gh codespace edit --machine standardLinux

# Rebuild a codespace
gh codespace rebuild

# Full rebuild (recreates from scratch)
gh codespace rebuild --full
```

## SSH Access

```bash
# SSH into a codespace
gh codespace ssh

# Run a command inside the codespace
gh codespace ssh -- ls -la

# Generate SSH config for use with native ssh
gh codespace ssh --config

# Use a specific SSH profile
gh codespace ssh --profile custom-profile
```

## Port Forwarding

```bash
# List exposed ports
gh codespace ports

# Forward a port
gh codespace ports forward 3000:3000

# Set port visibility
gh codespace ports visibility 3000:public
gh codespace ports visibility 3000:private
gh codespace ports visibility 3000:org
```

## File Operations

```bash
# Copy files to/from codespace
gh codespace cp local-file.txt codespace:/path/

# Recursive copy
gh codespace cp -r ./project codespace:/workspace/
```

## Opening IDEs

```bash
# Open in VS Code (desktop)
gh codespace code

# Open in VS Code for the Web
gh codespace code --web

# Use insiders build
gh codespace code --insiders
```

## Jupyter Notebooks

```bash
# Open Jupyter notebook in browser
gh codespace jupyter
```

## Logs

```bash
# View codespace logs
gh codespace logs

# Follow logs in real-time
gh codespace logs --follow
```

## Admin Operations

Organization administrators can manage codespaces across their organization:

```bash
# List org codespaces
gh codespace list --org myorg

# List codespaces for a specific user
gh codespace list --org myorg --user username

# Stop a user's codespace
gh codespace stop --org myorg --user username

# Delete a user's codespace
gh codespace delete --org myorg --user username
```

## Filtering

Use `-c` or `--codespace` to target a specific codespace by name, and `-R` to filter by repository:

```bash
gh codespace view --codespace my-codespace-abc123
gh codespace list --repo owner/repo
```
