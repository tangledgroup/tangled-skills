# Command Categories

## Contents
- Git
- GitHub CLI
- Cargo / Rust
- JavaScript / TypeScript
- Python
- Go
- Ruby
- .NET
- Docker / Kubernetes
- Files and Search
- Cloud and Data
- Global Flags
- Meta Commands

## Git

| Command | Savings | What changes |
|---------|---------|-------------|
| `rtk git status` | 75–93% | Compact stat format, grouped by state |
| `rtk git log -n 10` | ~80% | One-line commits |
| `rtk git diff` | ~75% | Condensed diff |
| `rtk git add` | ~92% | → "ok" |
| `rtk git commit -m "msg"` | ~92% | → "ok abc1234" |
| `rtk git push` | ~92% | → "ok main" |
| `rtk git pull` | ~90% | → "ok 3 files +10 -2" |

## GitHub CLI

| Command | What changes |
|---------|-------------|
| `rtk gh pr list` | Compact PR listing |
| `rtk gh pr view 42` | PR details + checks |
| `rtk gh issue list` | Compact issue listing |
| `rtk gh run list` | Workflow run status |

## Cargo / Rust

| Command | Savings | What changes |
|---------|---------|-------------|
| `rtk cargo build` | ~80% | Build output compressed |
| `rtk cargo clippy` | ~80% | Lint grouped by file |
| `rtk cargo test` | ~90% | Failures only, pass count |

## JavaScript / TypeScript

| Command | What changes |
|---------|-------------|
| `rtk jest` | Compact (failures only) |
| `rtk vitest` | Compact (failures only) |
| `rtk playwright test` | E2E results (failures only) |
| `rtk tsc` | Errors grouped by file |
| `rtk next build` | Next.js build compact |
| `rtk prettier --check .` | Files needing formatting |
| `rtk eslint .` | Grouped by rule/file |
| `rtk lint biome` | Supports other linters |

## Python

| Command | What changes |
|---------|-------------|
| `rtk pytest` | ~90% — failures only |
| `rtk ruff check` | ~80% — JSON output, grouped |
| `rtk pip list` | Compact dependency tree |
| `rtk pip outdated` | Outdated packages |

## Go

| Command | What changes |
|---------|-------------|
| `rtk go test` | ~90% — NDJSON format, failures only |
| `rtk golangci-lint run` | ~85% — JSON output |

## Ruby

| Command | What changes |
|---------|-------------|
| `rtk rake test` | ~90% — minitest failures only |
| `rtk rspec` | ~60%+ — JSON format |
| `rtk rubocop` | JSON output, grouped by rule |
| `rtk bundle install` | Strips "Using" lines |

## .NET

| Command | What changes |
|---------|-------------|
| `rtk dotnet build` | Build output compressed |
| `rtk dotnet test` | Test results compact |

## Docker / Kubernetes

| Command | Savings | What changes |
|---------|---------|-------------|
| `rtk docker ps` | ~80% | Compact container list |
| `rtk docker images` | ~80% | Compact image list |
| `rtk docker logs <container>` | variable | Deduplicated log lines |
| `rtk docker compose ps` | ~80% | Compose services compact |
| `rtk kubectl pods` | ~80% | Compact pod list |
| `rtk kubectl logs <pod>` | variable | Deduplicated logs |
| `rtk kubectl services` | ~80% | Compact service list |

## Files and Search

| Command | Savings | What changes |
|---------|---------|-------------|
| `rtk ls .` | ~80% | Token-optimized directory tree |
| `rtk read file.rs` | variable | Smart file reading |
| `rtk read file.rs -l aggressive` | high | Signatures only (strips bodies) |
| `rtk smart file.rs` | high | 2-line heuristic code summary |
| `rtk find "*.rs" .` | ~80% | Compact find results |
| `rtk grep "pattern" .` | ~80% | Grouped search results |
| `rtk diff file1 file2` | variable | Condensed diff |

## Cloud and Data

### AWS
| Command | What changes |
|---------|-------------|
| `rtk aws sts get-caller-identity` | One-line identity |
| `rtk aws ec2 describe-instances` | Compact instance list |
| `rtk aws lambda list-functions` | Name/runtime/memory (strips secrets) |
| `rtk aws logs get-log-events` | Timestamped messages only |
| `rtk aws cloudformation describe-stack-events` | Failures first |
| `rtk aws dynamodb scan` | Unwraps type annotations |
| `rtk aws iam list-roles` | Strips policy documents |
| `rtk aws s3 ls` | Truncated with tee recovery |

### Other
| Command | What changes |
|---------|-------------|
| `rtk json config.json` | Structure without values |
| `rtk deps` | Dependencies summary |
| `rtk env -f AWS` | Filtered env vars |
| `rtk log app.log` | Deduplicated logs |
| `rtk curl <url>` | Truncate + save full output |
| `rtk wget <url>` | Download, strip progress bars |
| `rtk summary <long command>` | Heuristic summary |
| `rtk proxy <command>` | Raw passthrough + tracking |

## Global Flags

| Flag | Description |
|------|-------------|
| `-u, --ultra-compact` | ASCII icons, inline format (extra token savings) |
| `-v, --verbose` | Increase verbosity (`-v`, `-vv`, `-vvv`) |

## Meta Commands

| Command | Description |
|---------|-------------|
| `rtk err <cmd>` | Filter errors only from any command output |
| `rtk test <cmd>` | Generic test wrapper — failures only (~90%) |

## Commands Not Rewritten

Built-in AI assistant tools (Claude Code's `Read`, `Grep`, `Glob`) bypass the shell hook. Use shell commands (`cat`/`head`/`tail`, `rg`/`grep`, `find`) or explicit `rtk read`, `rtk grep`, `rtk find` for RTK filtering on those workflows.
