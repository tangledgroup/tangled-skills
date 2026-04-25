# Attestation & Security

> **Source:** https://cli.github.com/, https://github.com/cli/cli#verification-of-binaries
> **Loaded from:** SKILL.md (via progressive disclosure)

## Build Provenance Attestations

Since v2.50.0, `gh` produces [Build Provenance Attestation](https://github.blog/changelog/2024-06-25-artifact-attestations-is-generally-available/), enabling cryptographically verifiable paper-trail back to the origin repository, git revision, and build instructions. Attestations are signed via Public Good [Sigstore](https://www.sigstore.dev/) PKI.

### Verify a Release (with gh installed)

```bash
gh at verify -R cli/cli gh_2.91.0_macOS_arm64.zip
```

Output:

```
Loaded digest sha256:... for file://gh_2.91.0_macOS_arm64.zip
Loaded 1 attestation from GitHub API
✓ Verification succeeded!

sha256:... was attested by:
REPO     PREDICATE_TYPE                  WORKFLOW
cli/cli  https://slsa.dev/provenance/v1  .github/workflows/deployment.yml@refs/heads/trunk
```

### Verify with Sigstore cosign

```bash
cosign verify-blob-attestation \
  --bundle cli-cli-attestation-3120304.sigstore.json \
  --new-bundle-format \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com" \
  --certificate-identity="https://github.com/cli/cli/.github/workflows/deployment.yml@refs/heads/trunk" \
  gh_2.91.0_macOS_arm64.zip
```

## Attestation Commands

- `gh attestation download` — Download attestation bundles for artifacts
- `gh attestation trusted-root` — Display the Sigstore public good trusted root JSON
- `gh attestation verify <digest>` — Verify artifact provenance against attestations in a repository

## Release Asset Verification

Verify signatures on release assets:

```bash
# Verify an entire release
gh release verify v2.91.0

# Verify a specific asset
gh release verify-asset v2.91.0 binary-linux-amd64
```

## Authentication Security

### Token Scopes

When authenticating, `gh auth login` lets you choose scopes:

- **web** — Access to GitHub web API
- **repo** — Full repository access (for private repos)
- **read:org** — Read organization membership
- **workflow** — Manage GitHub Actions workflows

### Git Protocol Selection

Choose between HTTPS and SSH for git operations:

```bash
gh auth login --git-protocol ssh
gh config set git_protocol ssh
```

SSH avoids credential helper setup but requires configured SSH keys.

### GitHub Enterprise Server

For GitHub Enterprise Server, specify the host:

```bash
gh auth login --hostname ghe.example.com
```

Use `GH_ENTERPRISE_TOKEN` or `GITHUB_ENTERPRISE_TOKEN` environment variables for non-interactive authentication.
