# ☐ Plan: Update Skills to Latest Upstream Versions

**Depends On:** NONE
**Created:** 2026-05-14T00:00:00Z
**Updated:** 2026-05-14T20:36:00Z
**Current Phase:** ☐ Phase 1
**Current Task:** ☐ Task 1.1

## ☐ Phase 1 Generate Updated Skills (Major Bumps)

These 3 skills have MAJOR version bumps — highest priority, likely breaking changes or significant new features. Use skman to generate new skills from the external references listed.

- ☐ Task 1.1 cryptography-48-0-0 (47.0.0 → 48.0.0)
  - Source: PyPI `cryptography` (confirmed: 48.0.0)
  - Tag: `https://github.com/pyca/cryptography/releases/tag/48.0`
  - Docs: `docs/` dir in repo → https://cryptography.io/en/latest/
  - External refs: https://cryptography.io/en/latest/, https://github.com/pyca/cryptography

- ☐ Task 1.2 nodejs-26-1-0 (24.14.0 → 26.1.0)
  - Source: GitHub `nodejs/node` (confirmed: v26.1.0)
  - Tag: `https://github.com/nodejs/node/releases/tag/v26.1.0`
  - Docs: `doc/` subdirectory in release tarballs, online at https://nodejs.org/api/
  - External refs: https://nodejs.org/api/, https://github.com/nodejs/node

- ☐ Task 1.3 paramiko-5-0-0 (4.0.0 → 5.0.0)
  - Source: PyPI `paramiko` (confirmed: 5.0.0)
  - Tag: `https://github.com/paramiko/paramiko/releases/tag/v5.0.0`
  - Docs: https://docs.paramiko.org (versioned docs, no `docs/` dir in repo root)
  - External refs: https://docs.paramiko.org/, https://github.com/paramiko/paramiko

## ☐ Phase 2 Generate Updated Skills (Minor Bumps)

These 12 skills have MINOR version bumps — new features, typically backward-compatible.

- ☐ Task 2.1 acp-0-13-0 (0.12.2 → 0.13.0)
  - Source: GitHub `agentclientprotocol/agent-client-protocol` (confirmed: v0.13.0 spec, May 12 2026)
  - Tag: `https://github.com/agentclientprotocol/agent-client-protocol/releases/tag/v0.13.0`
  - Docs: https://agentclientprotocol.com (website, no `docs/` dir in repo)
  - Note: Tracks protocol spec version, not SDK. PyPI SDK is 0.10.0, NPM SDK is 0.21.1 — skill covers the protocol itself.
  - External refs: https://agentclientprotocol.com, https://github.com/agentclientprotocol/agent-client-protocol

- ☐ Task 2.2 dirac-0-3-43 (0.2.89 → 0.3.43)
  - Source: npm `dirac-cli` (confirmed: 0.3.43)
  - Docs: https://dirac.run/docs (website docs)
  - External refs: https://www.npmjs.com/package/dirac-cli, https://github.com/dirac-run/dirac

- ☐ Task 2.3 nginx-1-31-0 (1.30.0 → 1.31.0)
  - Source: GitHub `nginx/nginx` (confirmed: 1.31.0, May 13 2026)
  - Tag: `https://github.com/nginx/nginx/releases/tag/release-1.31.0`
  - Docs: https://nginx.org/en/docs/ (official docs site)
  - Note: Security release — patches 6 CVEs including HTTP/2 request injection
  - External refs: https://nginx.org/en/docs/, https://github.com/nginx/nginx

- ☐ Task 2.4 openai-2-36-0 (2.33.0 → 2.36.0)
  - Source: PyPI `openai` (confirmed: 2.36.0)
  - Tag: `https://github.com/openai/openai-python/releases/tag/v2.36.0`
  - Docs: https://platform.openai.com/docs/ (official docs), CHANGELOG.md in repo
  - External refs: https://platform.openai.com/docs/, https://github.com/openai/openai-python

- ☐ Task 2.5 pycrdt-0-13-0 (0.12.50 → 0.13.0)
  - Source: PyPI `pycrdt` (confirmed: 0.13.0, May 5 2026)
  - Tag: `https://github.com/y-crdt/pycrdt/releases/tag/v0.13.0`
  - Docs: https://y-crdt.github.io/pycrdt/ (website docs)
  - External refs: https://y-crdt.github.io/pycrdt/, https://github.com/y-crdt/pycrdt

- ☐ Task 2.6 sentence-transformers-5-5-0 (5.4.1 → 5.5.0)
  - Source: PyPI `sentence-transformers` (confirmed: 5.5.0)
  - Tag: `https://github.com/huggingface/sentence-transformers/releases/tag/v5.5.0`
  - Docs: https://www.sbert.net/ (website docs), no `docs/` dir in repo
  - External refs: https://www.sbert.net/, https://github.com/huggingface/sentence-transformers

- ☐ Task 2.7 tailwindcss-4-3-0 (4.2.4 → 4.3.0)
  - Source: npm `tailwindcss` (confirmed: 4.3.0)
  - Tag: `https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.3.0`
  - Docs: https://tailwindcss.com/docs (website docs), no `docs/` dir in repo
  - External refs: https://tailwindcss.com/docs, https://github.com/tailwindlabs/tailwindcss

- ☐ Task 2.8 tailwindcss-browser-4-3-0 (4.2.4 → 4.3.0)
  - Source: npm `@tailwindcss/browser` (confirmed: 4.3.0)
  - Tag: `https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.3.0` (shared repo)
  - Docs: https://www.npmjs.com/package/@tailwindcss/browser
  - External refs: https://www.npmjs.com/package/@tailwindcss/browser, https://github.com/tailwindlabs/tailwindcss

- ☐ Task 2.9 transformers-5-8-1 (5.7.0 → 5.8.1)
  - Source: PyPI `transformers` (confirmed: 5.8.1, May 13 2026)
  - Tag: `https://github.com/huggingface/transformers/releases/tag/v5.8.1`
  - Docs: `docs/` dir in repo → https://huggingface.co/docs/transformers/index
  - External refs: https://huggingface.co/docs/transformers/en/index, https://github.com/huggingface/transformers

- ☐ Task 2.10 mermaid-11-15-0 (11.14.0 → 11.15.0)
  - Source: npm `mermaid` (confirmed: 11.15.0, May 11 2026)
  - Tag: `https://github.com/mermaid-js/mermaid/releases/tag/v11.15.0`
  - Docs: https://mermaid.js.org/ (website docs), no `docs/` dir in repo
  - External refs: https://mermaid.js.org/, https://github.com/mermaid-js/mermaid

- ☐ Task 2.11 axios-1-16-1 (1.15.2 → 1.16.1)
  - Source: npm `axios` (confirmed: 1.16.1, published 11h ago)
  - Tag: `https://github.com/axios/axios/releases/tag/v1.16.1`
  - Docs: https://axios-http.com/ (website docs), no `docs/` dir in repo
  - External refs: https://axios-http.com/, https://github.com/axios/axios

- ☐ Task 2.12 logfire-4-33-0 (4.32.1 → 4.33.0)
  - Source: PyPI `logfire` (confirmed: 4.33.0)
  - Tag: `https://github.com/pydantic/logfire/releases/tag/4.33.0`
  - Docs: https://pydantic.dev/logfire/docs/ (website docs)
  - External refs: https://pydantic.dev/logfire/docs/, https://github.com/pydantic/logfire

## ☐ Phase 3 Generate Updated Skills (Patch Bumps)

These 22 skills have PATCH version bumps — bug fixes and minor improvements. Lower priority but still worth updating.

- ☐ Task 3.1 agentmemory-0-9-12 (0.9.4 → 0.9.12)
  - Source: GitHub `rohitg00/agentmemory` (confirmed: 0.9.12 on npm)
  - Tag: `https://github.com/rohitg00/agentmemory/releases/tag/v0.9.12`
  - Docs: README.md in repo, https://www.agent-memory.dev (website)
  - External refs: https://github.com/rohitg00/agentmemory, https://www.npmjs.com/package/@agentmemory/agentmemory

- ☐ Task 3.2 aiohttp-3-13-5 (3.13.0 → 3.13.5)
  - Source: PyPI `aiohttp` (confirmed: 3.13.5)
  - Tag: `https://github.com/aio-libs/aiohttp/releases/tag/v3.13.5`
  - Docs: https://docs.aiohttp.org/en/stable/ (website docs), no `docs/` dir in repo
  - Note: aiohttp-3-13-5 already exists in .agents/skills/ — skip generation, only move old aiohttp-3-13-0 to misc/
  - External refs: https://docs.aiohttp.org/en/stable/, https://github.com/aio-libs/aiohttp

- ☐ Task 3.3 boto3-1-43-7 (1.43.1 → 1.43.7)
  - Source: PyPI `boto3` (confirmed: 1.43.7)
  - Docs: https://boto3.amazonaws.com/v1/documentation/api/latest/ (AWS docs site), no `docs/` dir in repo
  - External refs: https://boto3.amazonaws.com/v1/documentation/api/latest/, https://github.com/boto/boto3

- ☐ Task 3.4 bun-1-3-14 (1.3.13 → 1.3.14)
  - Source: npm `bun` (confirmed: 1.3.14)
  - Docs: https://bun.sh/docs (website docs), no `docs/` dir in repo
  - External refs: https://bun.sh/

- ☐ Task 3.5 caddy-2-11-3 (2.11.2 → 2.11.3)
  - Source: GitHub `caddyserver/caddy` (confirmed: v2.11.3, May 12 2026)
  - Tag: `https://github.com/caddyserver/caddy/releases/tag/v2.11.3`
  - Docs: https://caddyserver.com/docs/ (website docs), no `docs/` dir in repo
  - External refs: https://caddyserver.com/docs/, https://github.com/caddyserver/caddy

- ☐ Task 3.6 chonkie-1-6-6 (1.6.4 → 1.6.6)
  - Source: PyPI `chonkie` (confirmed: 1.6.6)
  - Tag: `https://github.com/chonkie-inc/chonkie/releases/tag/v1.6.6`
  - Docs: https://docs.chonkie.ai (website docs), no `docs/` dir in repo
  - External refs: https://docs.chonkie.ai, https://github.com/chonkie-inc/chonkie

- ☐ Task 3.7 dspy-3-2-1 (3.2.0 → 3.2.1)
  - Source: PyPI `dspy` (confirmed: 3.2.1)
  - Tag: `https://github.com/stanfordnlp/dspy/releases/tag/v3.2.1`
  - Docs: https://dspy.ai/ (website docs), no `docs/` dir in repo
  - External refs: https://dspy.ai/, https://github.com/stanfordnlp/dspy

- ☐ Task 3.8 grafana-13-0-1+security-01 (13.0.1 → 13.0.1+security-01)
  - Source: GitHub `grafana/grafana` (confirmed: v13.0.1+security-01)
  - Tag: `https://github.com/grafana/grafana/releases/tag/v13.0.1%2Bsecurity-01`
  - Docs: https://grafana.com/docs/grafana/latest/ (website docs), no `docs/` dir in repo
  - Note: Security patch — prioritize if security is a concern
  - External refs: https://grafana.com/docs/grafana/latest/, https://github.com/grafana/grafana

- ☐ Task 3.9 mem0-2-0-2 (2.0.1 → 2.0.2)
  - Source: PyPI `mem0ai` (confirmed: 2.0.2)
  - Tag: `https://github.com/mem0ai/mem0/releases/tag/v2.0.2`
  - Docs: https://docs.mem0.ai/ (website docs), no `docs/` dir in repo
  - External refs: https://docs.mem0.ai/llms.txt, https://github.com/mem0ai/mem0

- ☐ Task 3.10 mempalace-3-3-5 (3.3.4 → 3.3.5)
  - Source: PyPI `mempalace` (confirmed: 3.3.5)
  - Tag: `https://github.com/MemPalace/mempalace/releases/tag/v3.3.5`
  - Docs: https://mempalaceofficial.com (website docs), no `docs/` dir in repo
  - External refs: https://github.com/MemPalace/mempalace/releases, https://mempalaceofficial.com

- ☐ Task 3.11 nextjs-16-2-6 (16.2.4 → 16.2.6)
  - Source: npm `next` (confirmed: 16.2.6, 6 days ago)
  - Tag: `https://github.com/vercel/next.js/releases/tag/v16.2.6`
  - Docs: https://nextjs.org/docs (website docs), no `docs/` dir in repo
  - Note: Security release — 13 security fixes including 7 high-severity advisories
  - External refs: https://nextjs.org/docs, https://github.com/vercel/next.js

- ☐ Task 3.12 podman-5-8-2 (5.8.1 → 5.8.2)
  - Source: GitHub `containers/podman` (confirmed: v5.8.2, April 14 2026)
  - Tag: `https://github.com/containers/podman/releases/tag/v5.8.2`
  - Docs: https://docs.podman.io/ (website docs), no `docs/` dir in repo
  - Note: podman-5-8-2 already exists in .agents/skills/ — skip generation, only move old podman-5-8-1 to misc/
  - External refs: https://docs.podman.io/, https://github.com/containers/podman

- ☐ Task 3.13 pulp-3-3-1 (3.3.0 → 3.3.1)
  - Source: PyPI `pulp` (confirmed: 3.3.1)
  - Tag: `https://github.com/coin-or/pulp/releases/tag/2.8.0` (latest release tag may differ from PyPI version)
  - Docs: https://coin-or.github.io/pulp/ (website docs), no `docs/` dir in repo
  - External refs: https://coin-or.github.io/pulp/, https://github.com/coin-or/pulp

- ☐ Task 3.14 ralph-orchestrator-2-9-3 (2.9.2 → 2.9.3)
  - Source: GitHub `mikeyobrien/ralph-orchestrator` (confirmed: v2.9.3)
  - Tag: `https://github.com/mikeyobrien/ralph-orchestrator/releases/tag/v2.9.3`
  - Docs: README.md in repo, https://mikeyobrien.github.io/ralph-orchestrator/ (website)
  - External refs: https://github.com/mikeyobrien/ralph-orchestrator, https://mikeyobrien.github.io/ralph-orchestrator/

- ☐ Task 3.15 rqlite-10-0-5 (10.0.1 → 10.0.5)
  - Source: GitHub `rqlite/rqlite` (confirmed: v10.0.5 via SourceForge mirror)
  - Tag: `https://github.com/rqlite/rqlite/releases/tag/v10.0.5`
  - Docs: https://rqlite.io/docs/ (website docs), no `docs/` dir in repo
  - External refs: https://rqlite.io/docs/, https://github.com/rqlite/rqlite

- ☐ Task 3.16 ruff-0-15-13 (0.15.12 → 0.15.13)
  - Source: PyPI `ruff` (confirmed: 0.15.13)
  - Tag: `https://github.com/astral-sh/ruff/releases/tag/v0.15.13`
  - Docs: https://docs.astral.sh/ruff (website docs), no `docs/` dir in repo
  - External refs: https://docs.astral.sh/ruff, https://github.com/astral-sh/ruff

- ☐ Task 3.17 spec-kit-0-8-10 (0.8.3 → 0.8.10)
  - Source: GitHub `github/spec-kit` (confirmed: v0.8.9+ on releases page)
  - Tag: `https://github.com/github/spec-kit/releases/tag/v0.8.10`
  - Docs: https://speckit.org/ (website docs), no `docs/` dir in repo
  - Note: 7 patch releases accumulated — check changelog for meaningful changes
  - External refs: https://github.com/github/spec-kit

- ☐ Task 3.18 stringzilla-4-6-1 (4.6.0 → 4.6.1)
  - Source: PyPI `stringzilla` (confirmed: 4.6.1)
  - Tag: `https://github.com/ashvardanian/StringZilla/releases/tag/v4.6.1`
  - Docs: README.md in repo, https://docs.rs/stringzilla (Rust docs)
  - External refs: https://github.com/ashvardanian/StringZilla, https://docs.rs/stringzilla

- ☐ Task 3.19 textual-8-2-6 (8.2.5 → 8.2.6)
  - Source: PyPI `textual` (confirmed: 8.2.6)
  - Tag: `https://github.com/Textualize/textual/releases/tag/0.82.6` (check tag format — may be 0.82.6 not 8.2.6)
  - Docs: https://textual.textualize.io/ (website docs), no `docs/` dir in repo
  - External refs: https://textual.textualize.io/, https://github.com/Textualize/textual

- ☐ Task 3.20 ty-0-0-35 (0.0.33 → 0.0.35)
  - Source: PyPI `ty` (confirmed: 0.0.35)
  - Tag: `https://github.com/astral-sh/ty/releases/tag/v0.0.35`
  - Docs: https://docs.astral.sh/ty/ (website docs), no `docs/` dir in repo
  - External refs: https://docs.astral.sh/ty/, https://github.com/astral-sh/ty

- ☐ Task 3.21 usearch-2-25-2 (2.25.1 → 2.25.2)
  - Source: PyPI `usearch` (confirmed: 2.25.2)
  - Tag: `https://github.com/unum-cloud/usearch/releases/tag/v2.25.2`
  - Docs: https://unum-cloud.github.io/USearch/ (website docs), no `docs/` dir in repo
  - External refs: https://unum-cloud.github.io/USearch/, https://github.com/unum-cloud/usearch

- ☐ Task 3.22 uv-0-11-14 (0.11.8 → 0.11.14)
  - Source: PyPI `uv` (confirmed: 0.11.14)
  - Tag: `https://github.com/astral-sh/uv/releases/tag/0.11.14`
  - Docs: https://docs.astral.sh/uv/ (website docs), no `docs/` dir in repo
  - Note: 6 patch releases accumulated — check changelog for meaningful changes
  - External refs: https://docs.astral.sh/uv/, https://github.com/astral-sh/uv

## ☐ Phase 4 Validate and Regenerate README

After all skills are generated, validate each one and regenerate the skills table.

- ☐ Task 4.1 Validate all newly generated skills
  - Run: `for d in .agents/skills/*/; do bash .agents/skills/skman/scripts/validate-skill.sh "$d" 2>/dev/null || echo "FAIL: $d"; done`
  - Use skman's validate-skill.sh for each skill
- ☐ Task 4.2 Regenerate README.md skills table
  - Run: `bash .agents/skills/skman/scripts/gen-skills-table.sh`
- ☐ Task 4.3 Commit changes with conventional commit message
  - Message: `chore(skills): update 37 skills to latest upstream versions`

## ☐ Phase 5 Move Outdated Skills to misc/

After new skills are generated and validated, move old skill directories to `misc/` to preserve history without cluttering `.agents/skills/`. This is done last so that if generation fails for any skill, the old version remains available.

- ☐ Task 5.1 Batch-move all 37 outdated skills to misc/
  - Run: `for d in acp-0-12-2 agentmemory-0-9-4 aiohttp-3-13-0 axios-1-15-2 boto3-1-43-1 bun-1-3-13 caddy-2-11-2 chonkie-1-6-4 cryptography-47-0-0 dirac-0-2-89 dspy-3-2-0 grafana-13-0-1 logfire-4-32-1 mem0-2-0-1 mempalace-3-3-4 mermaid-11-14-0 nextjs-16-2-4 nginx-1-30-0 nodejs-24-14-0 openai-2-33-0 paramiko-4-0-0 podman-5-8-1 pulp-3-3-0 pycrdt-0-12-50 ralph-orchestrator-2-9-2 rqlite-10-0-1 ruff-0-15-12 sentence-transformers-5-4-1 spec-kit-0-8-3 stringzilla-4-6-0 tailwindcss-4-2-4 tailwindcss-browser-4-2-4 textual-8-2-5 transformers-5-7-0 ty-0-0-33 usearch-2-25-1 uv-0-11-8; do mv ".agents/skills/$d" "misc/$d"; done`
  - Verify: `ls misc/ | wc -l` should increase by 37
  - Note: Skip aiohttp-3-13-5 and podman-5-8-1 since those skills already exist in .agents/skills/ at the target version — only move the old versions (aiohttp-3-13-0, podman-5-8-1)
