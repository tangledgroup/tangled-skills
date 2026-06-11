# Command Line Reference

Caddy has a standard Unix-like CLI. Basic usage:

```
caddy <command> [<args...>]
```

## Running Caddy

### `caddy run`

Starts Caddy in the foreground (daemon mode):

```bash
caddy run
caddy run --config /etc/caddy/Caddyfile
caddy run --config /etc/caddy/caddy.json --adapter caddyfile
caddy run --resume          # Resume last saved config
caddy run --watch           # Watch config file for changes (development only)
caddy run --environ         # Print environment before starting
caddy run --envfile .env    # Load env vars from file
caddy run --pidfile /run/caddy.pid
```

If a `Caddyfile` exists in the current directory and no config is specified, it is loaded automatically.

### `caddy start`

Same as `run` but runs in background:

```bash
caddy start --config Caddyfile
```

Use `caddy stop` to terminate. Discouraged for system services — use `run` with systemd instead.

### `caddy stop`

Gracefully stops the running Caddy process via the admin API:

```bash
caddy stop
caddy stop --address localhost:2020   # Custom admin address
```

## Configuration Management

### `caddy reload`

Zero-downtime config reload (uses admin API):

```bash
caddy reload
caddy reload --config /etc/caddy/Caddyfile
caddy reload --force                  # Force reload even if config unchanged
caddy reload --address localhost:2020
```

This is the correct way to change configuration in production. Do not stop and restart Caddy to change config — that causes downtime.

### `caddy adapt`

Convert Caddyfile to native JSON without running it:

```bash
caddy adapt --config Caddyfile
caddy adapt --pretty                  # Indented output
caddy adapt --validate                # Check for validity (stronger than adaptation)
```

Validation catches errors that arise during provisioning (e.g., missing certificate files).

### `caddy validate`

Validate a configuration file:

```bash
caddy validate --config Caddyfile
caddy validate --envfile .env
```

Deserializes config and provisions all modules without starting the server.

## Utility Commands

### `caddy file-server`

Production-ready static file server:

```bash
caddy file-server --root /var/www
caddy file-server --listen :8080
caddy file-server --domain example.com
caddy file-server --browse            # Enable directory listing
caddy file-server --templates         # Enable template rendering
caddy file-server --access-log        # Enable access log
caddy file-server --debug             # Verbose logging
caddy file-server --precompressed gzip zstd
```

Disables admin API for easy multi-instance use.

### `caddy reverse-proxy`

Quick reverse proxy:

```bash
caddy reverse-proxy --from :8080 --to localhost:9000
caddy reverse-proxy --from :8080 --to localhost:9001 localhost:9002
caddy reverse-proxy --from example.com --to localhost:3000
caddy reverse-proxy --from :8080 --to localhost:9000 --change-host-header
caddy reverse-proxy --from :8080 --to localhost:9000 --internal-certs
```

### `caddy respond`

Quick HTTP response server for testing:

```bash
caddy respond                         # Empty 200 on random port
caddy respond "Hello, world!"         # Custom body
caddy respond --status 503            # Custom status
caddy respond --listen :8080-8084     # Multiple servers (port range)
```

### `caddy hash-password`

Hash passwords for basic_auth:

```bash
echo "mypassword" | caddy hash-password
caddy hash-password --plaintext mypassword
caddy hash-password --algorithm argon2id   # Recommended
caddy hash-password --algorithm bcrypt
caddy hash-password --bcrypt-cost 14
```

### `caddy fmt`

Format/prettify a Caddyfile:

```bash
caddy fmt
caddy fmt --overwrite
caddy fmt --diff
```

## System Commands

### `caddy trust`

Install local CA root certificate into system trust store:

```bash
sudo caddy trust
sudo caddy trust --ca local
```

Required when Caddy runs as unprivileged user (e.g., systemd service) and needs to install its local CA.

### `caddy untrust`

Remove local CA root from trust store:

```bash
sudo caddy untrust
sudo caddy untrust --cert /path/to/root.crt
```

### `caddy upgrade`

Upgrade Caddy binary to latest release (experimental):

```bash
caddy upgrade
caddy upgrade --keep-backup
```

### `caddy add-package` / `caddy remove-package`

Add or remove third-party modules (experimental):

```bash
caddy add-package github.com/caddy-dns/cloudflare
caddy remove-package github.com/some/plugin
```

## Information Commands

### `caddy version`

Print version:

```bash
caddy version
```

### `caddy build-info`

Print Go build information:

```bash
caddy build-info
```

### `caddy list-modules`

List installed modules:

```bash
caddy list-modules
caddy list-modules --packages --versions
caddy list-modules --skip-standard
caddy list-modules --json
```

### `caddy environ`

Print environment as seen by Caddy:

```bash
caddy environ
```

Useful for debugging systemd or init system configurations.

### `caddy completion`

Generate shell completion scripts:

```bash
caddy completion bash
caddy completion zsh
caddy completion fish
caddy completion powershell
```

### `caddy manpage`

Generate manual pages:

```bash
caddy manpage --directory /path/to/man
```

## Storage Commands

### `caddy storage export` / `import`

Export/import Caddy's data storage (experimental):

```bash
caddy storage export -c Caddyfile -o backup.tar
caddy storage import -c Caddyfile -i backup.tar

# Migrate between storage modules:
caddy storage export -c Caddyfile.old -o- | caddy storage import -c Caddyfile.new -i-
```

## Signals

Caddy handles Unix signals:

- `SIGINT` — Graceful exit. Send again to force immediate exit.
- `SIGQUIT` — Immediate quit with cleanup.
- `SIGTERM` — Graceful exit.
- `SIGUSR1` — Reload config (only if started with `caddy run` and a config file, and no API changes made).
- `SIGUSR2` — Ignored.
- `SIGHUP` — Ignored.

Graceful exit stops accepting new connections, drains existing ones, then closes. Configurable grace period applies.

## Exit Codes

- `0` — Normal exit
- `1` — Failed startup (do not auto-restart; fix config first)
- `2` — Forced quit without cleanup
- `3` — Failed quit with cleanup errors
