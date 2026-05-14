# Authentication

## Overview

`gh` supports multiple authentication methods for GitHub.com and GitHub Enterprise Server instances. Credentials are stored securely using the system keychain or credential store by default.

## Interactive Login

```bash
# Start interactive authentication flow
gh auth login

# Open browser for OAuth device flow
gh auth login --web --clipboard

# Authenticate against a specific host
gh auth login --hostname enterprise.internal
```

The interactive flow guides you through:
1. Selecting the GitHub host (github.com or custom)
2. Choosing authentication method (browser or paste token)
3. Selecting git protocol (HTTPS or SSH)
4. Optionally uploading an SSH key to GitHub

## Token-Based Authentication

```bash
# Read token from standard input
gh auth login --with-token < mytoken.txt

# Read token from a file
gh auth login --with-token <<< "$MY_TOKEN"
```

Token-based authentication is ideal for CI/CD environments. In GitHub Actions:

```yaml
env:
  GH_TOKEN: ${{ github.token }}
```

## Multiple Hosts and Accounts

`gh` supports multiple authenticated hosts simultaneously:

```bash
# Check authentication status
gh auth status

# Switch between accounts on the same host
gh auth switch --user other-account

# Refresh tokens
gh auth refresh

# Add additional scopes
gh auth refresh --scopes admin:org,write:packages

# Remove specific scopes
gh auth refresh --remove-scopes delete_repo

# Reset to default minimum scopes
gh auth refresh --reset-scopes
```

## Logout

```bash
# Log out of a specific host
gh auth logout --hostname enterprise.internal

# Log out of a specific user
gh auth logout --user username
```

## Git Integration

After authenticating, configure git to use `gh` for credential handling:

```bash
gh auth setup-git
```

For SSH protocol:

```bash
gh auth login --git-protocol ssh
```

Skip the SSH key upload prompt during login:

```bash
gh auth login --skip-ssh-key
```

## Token Extraction

Retrieve the current authentication token for scripting:

```bash
# Output the token
gh auth token

# Show token with auth status
gh auth status --show-token
```

## GitHub Enterprise Server

Authenticate to a self-hosted GitHub Enterprise instance:

```bash
gh auth login --hostname ghe.example.com
```

Set `GH_HOST` environment variable for default host:

```bash
export GH_HOST=ghe.example.com
```

## Insecure Storage

On systems without a credential store, use insecure storage (stores tokens in plain text):

```bash
gh auth login --insecure-storage
```

## Default Scopes

The default OAuth scopes requested during login are:
- `repo` — full repository access
- `read:org` — read organization membership
- `gist` — create and modify gists

Additional scopes can be added with `--scopes`:

```bash
gh auth login --scopes admin:org,delete_repo,write:packages
```

## CI/CD Environments

In GitHub Actions workflows, the `GITHUB_TOKEN` is automatically available. For other CI systems, set `GH_TOKEN` or `GITHUB_TOKEN` environment variables with a personal access token having appropriate scopes.
