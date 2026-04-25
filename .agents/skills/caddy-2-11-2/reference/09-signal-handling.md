# Signal Handling

| Signal | Behavior |
|--------|----------|
| `SIGINT` | Graceful exit (send again for immediate) |
| `SIGQUIT` | Immediate quit, cleans up storage locks |
| `SIGTERM` | Graceful exit |
| `SIGUSR1` | Reload config (if running with Caddyfile, no API changes) |
