# Authentication and Configuration

## Login Methods

tea supports multiple authentication methods, listed from most to least compatible across Gitea deployments:

### Application Token (Recommended)

The most universally compatible method. Generate a token in Gitea user settings under "Applications":

```bash
tea login add
# Select "application token" when prompted
# Paste your token
```

Or non-interactively:

```bash
tea login add --url https://mygitea.example.com --token ghp_xxxxxxxxxxxx
```

Token should have at least **user read** scope. Add additional scopes for write operations.

### OAuth2 Flow (v0.10+)

Interactive browser-based OAuth2 flow. Requires Gitea to support OAuth and a registered OAuth application:

```bash
tea login add --oauth --client-id <id> --redirect-url <url>
```

Since v0.13, OAuth tokens are stored in the OS keyring via credstore for improved security.

### Basic Authentication

Creates a token from username/password on the Gitea server:

```bash
tea login add --user myuser --password mypass
```

### SSH Authentication

Use SSH keys loaded in ssh-agent:

```bash
# Using key fingerprint
tea login add --ssh-agent-key SHA256:xxxxx

# Using certificate with principal
tea login add --ssh-agent-principal myprincipal

# Using specific key file
tea login add --ssh-key ~/.ssh/my_key
```

## Configuration File

Configuration is stored in `$XDG_CONFIG_HOME/tea/config.yml` (typically `~/.config/tea/config.yml`).

The config file supports multiple logins, each identified by the Gitea server URL. A default login can be set with:

```bash
tea login default
```

Config file permissions are restricted to owner-only read/write (v0.12+). File locking is used for safe concurrent access.

## Multiple Instances

tea supports logging into multiple Gitea servers simultaneously. Switch between them:

```bash
tea issues list --login gitea.com
tea issues list --login mygitea.example.com
tea login default --login gitea.com    # set default
```

## Repository Context Detection

When running inside a git repository, tea auto-detects the Gitea login and repository from remote URLs. Override with:

- `--repo` / `-r` — specify repository path or `owner/repo` slug
- `--remote` / `-R` — use a specific git remote name (e.g., `upstream`)
- `--login` / `-l` — use a specific login profile

## Environment Variables

tea reads authentication from environment variables when applicable. The `TEA_CREDENTIALS` variable can hold a base64-encoded config for CI/CD use:

```bash
echo "$TEA_CREDENTIALS" > $HOME/.config/tea/config.yml
```

## Security Considerations

- Config file is owner-only readable (v0.12+)
- OAuth tokens stored in OS keyring (v0.13+)
- `--insecure` flag disables TLS verification (use with caution)
- SSH passphrase only prompted when necessary (v0.12+)
- Token uniqueness check skipped for SSH auth (v0.12+)
