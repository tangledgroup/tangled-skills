# CLI Commands Reference

### Server Management

| Command | Description |
|---------|-------------|
| `caddy run` | Start Caddy in foreground (daemon mode) |
| `caddy start` | Start Caddy in background |
| `caddy stop` | Stop running Caddy process |
| `caddy reload` | Gracefully reload config without downtime |

### Configuration

| Command | Description |
|---------|-------------|
| `caddy adapt` | Convert Caddyfile to JSON |
| `caddy validate` | Validate a configuration file |
| `caddy fmt` | Format/pretty-print a Caddyfile |

### Diagnostics & Utilities

| Command | Description |
|---------|-------------|
| `caddy version` | Print version |
| `caddy build-info` | Print build information |
| `caddy list-modules` | List installed modules |
| `caddy environ` | Print environment variables |
| `caddy hash-password` | Hash a password for basicauth |
| `caddy completion` | Generate shell completions |

### Server Utilities

| Command | Description |
|---------|-------------|
| `caddy file-server` | Quick static file server |
| `caddy respond` | Quick hard-coded HTTP server |
| `caddy reverse-proxy` | Quick reverse proxy |

### Storage & Certificates

| Command | Description |
|---------|-------------|
| `caddy trust` | Install CA cert into system trust store |
| `caddy untrust` | Remove CA cert from trust store |
| `caddy storage export` | Export storage contents |
| `caddy storage import` | Import storage contents |

### Upgrade (Experimental)

| Command | Description |
|---------|-------------|
| `caddy upgrade` | Replace binary with latest version |
| `caddy add-package` | Add plugins to current binary |
| `caddy remove-package` | Remove plugins from current binary |
