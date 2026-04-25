# Troubleshooting Guide

Common issues and solutions for agentmemory.

## Connection Issues

### "Connection refused on port 3111"

**Problem:** The agentmemory server isn't running.

**Solution:** Start the server in a separate terminal:
```bash
npx @agentmemory/agentmemory
```

Keep this terminal open while your agent uses memory.

---

### "iii-engine process started" then "did not become ready within 15s"

**Problem:** The iii-engine background process crashed on startup.

**Solution:** Re-run with verbose output to see the actual error:
```bash
npx @agentmemory/agentmemory --verbose
```

Check stderr for specific errors. Common causes:
- iii-engine binary not found (see Windows setup below)
- Port already in use
- Docker not running (if using Docker fallback)

---

### "Could not start iii-engine"

**Problem:** Neither iii-engine nor Docker is available.

**Solutions:**

**Option A: Install iii-engine manually**

macOS/Linux:
```bash
curl -fsSL https://install.iii.dev/iii/main/install.sh | sh
```

Windows: Download from https://github.com/iii-hq/iii/releases/latest and extract `iii.exe` to PATH or `%USERPROFILE%\.local\bin\`.

**Option B: Use Docker Desktop**

Install Docker Desktop and ensure it's running. agentmemory will auto-detect and use the bundled `docker-compose.yml`.

**Option C: Standalone MCP only**

If you only need MCP tools without the full server:
```bash
npx -y @agentmemory/mcp
```

---

### Port conflict

**Problem:** Port 3111 or 3113 is already in use.

**Solution:** Check what's using the port and either kill it or use a different port:

Linux/macOS:
```bash
lsof -i :3111
# or
netstat -an | grep 3111
```

Windows:
```powershell
netstat -ano | findstr :3111
```

Use a different port:
```bash
III_REST_PORT=3112 npx @agentmemory/agentmemory
```

---

## Memory Retrieval Issues

### "No memories returned"

**Problem 1:** No observations have been captured yet.

**Solution:** Check the real-time viewer at `http://localhost:3113`. If there are no observations, the hooks aren't firing or the server just started.

**Problem 2:** Hooks aren't installed correctly.

**Solution:** For Claude Code, ensure you ran `/plugin install agentmemory`. For other agents, verify MCP config is correct and the agent restarted.

**Problem 3:** Search query doesn't match existing memories.

**Solution:** Try broader search terms or check `memory_profile` to see what concepts are indexed:
```bash
curl http://localhost:3111/agentmemory/profile
```

---

### "Search returns irrelevant results"

**Problem:** BM25-only search lacks semantic understanding.

**Solution:** Install local embeddings for vector search (+8pp recall):
```bash
npm install @xenova/transformers
```

Restart the server. Vector search will auto-enable.

**Alternative:** Use API-based embeddings:
```env
GEMINI_API_KEY=your-key  # Free tier, 1500 RPM
# or
OPENAI_API_KEY=your-key  # $0.02/1M tokens
# or
VOYAGE_API_KEY=your-key  # Optimized for code
```

---

### "Context injection too large/small"

**Problem:** Token budget not appropriate for your use case.

**Solution:** Adjust the token budget:

In `~/.agentmemory/.env`:
```env
TOKEN_BUDGET=3000  # Increase from default 2000
# or
TOKEN_BUDGET=1000  # Decrease for tighter context
```

Or pass budget per-request via MCP tools:
```typescript
await memory_smart_search({
  query: "project state",
  budget: 3000
});
```

---

## Windows Setup Issues

### iii-engine installation on Windows

**Problem:** The official installer is a bash script, not available for PowerShell.

**Solution A: Prebuilt binary (recommended)**

1. Open https://github.com/iii-hq/iii/releases/latest
2. Download `iii-x86_64-pc-windows-msvc.zip` (or `iii-aarch64-pc-windows-msvc.zip` for ARM)
3. Extract `iii.exe` to PATH or `%USERPROFILE%\.local\bin\`
4. Verify:
   ```powershell
   iii --version
   ```
5. Run agentmemory:
   ```powershell
   npx -y @agentmemory/agentmemory
   ```

**Solution B: Docker Desktop**

1. Install Docker Desktop for Windows
2. Start Docker Desktop (check system tray icon)
3. Run agentmemory (auto-detects Docker):
   ```powershell
   npx -y @agentmemory/agentmemory
   ```

**Solution C: WSL2**

Run agentmemory in WSL2 where the bash installer works:
```bash
curl -fsSL https://install.iii.dev/iii/main/install.sh | sh
npx @agentmemory/agentmemory
```

---

### "iii-config.docker.yaml is a directory"

**Problem:** Docker created an empty directory instead of mounting the file.

**Solution:** This was fixed in v0.8.7. Upgrade:
```bash
npm install -g @agentmemory/agentmemory@latest
```

If still occurring, ensure Docker Desktop is actually running (system tray icon visible).

---

## Token Usage Concerns

### "Agent burning too many tokens"

**Problem:** `AGENTMEMORY_AUTO_COMPRESS=true` causes LLM calls on every tool use.

**Solution:** This is OFF by default since v0.8.8. Check your config:

In `~/.agentmemory/.env`:
```env
AGENTMEMORY_AUTO_COMPRESS=false  # Default, zero LLM calls
```

Restart the server. The startup banner will show:
```
Auto-compress: OFF (default, #138)
```

If you want LLM-generated summaries (opt-in):
```env
AGENTMEMORY_AUTO_COMPRESS=true
```

Expect token usage proportional to tool call frequency (~50-200 calls/hour on active sessions).

---

### "How much does agentmemory cost?"

**Answer:** With local embeddings (recommended): **$0/year**.

With API embeddings:
- Gemini: Free tier (1500 RPM) usually sufficient
- OpenAI: ~$10/year for heavy use (~170K tokens/year)
- Voyage AI: Paid, check pricing

Token savings vs full context: **92% fewer tokens** (~170K vs 19.5M tokens/year).

Check your savings:
```bash
curl http://localhost:3111/agentmemory/status
```

Or view the dashboard at `http://localhost:3113`.

---

## Privacy and Security

### "Are my API keys safe?"

**Answer:** Yes. agentmemory strips secrets before storage:

- OpenAI keys (`sk-`, `sk-proj-`)
- Anthropic keys (`sk-ant-`)
- GitHub tokens (`ghp_`, `ghs_`, `ghu_`)
- AWS access keys
- Bearer tokens
- Custom `<private>` tags

The privacy filter runs on every observation before storage.

---

### "Is my memory exposed to the network?"

**Answer:** No. Since v0.8.2, agentmemory binds to `127.0.0.1` by default (localhost only).

To verify:
```bash
netstat -an | grep 3111
# Should show 127.0.0.1:3111, not 0.0.0.0:3111
```

If you need network access (Docker, remote agents), use `AGENTMEMORY_SECRET` for authentication:
```env
AGENTMEMORY_SECRET=your-secure-secret
```

---

### "How do I secure mesh sync?"

**Answer:** Mesh sync requires `AGENTMEMORY_SECRET` on both peers since v0.8.2:

Instance A:
```env
AGENTMEMORY_SECRET=shared-secret
```

Instance B:
```env
AGENTMEMORY_SECRET=shared-secret
```

Sync:
```typescript
await memory_mesh_sync({
  remoteUrl: 'http://instance-a:3111',
  secret: 'shared-secret',
  direction: 'bidirectional'
});
```

---

## Performance Issues

### "Slow search responses"

**Problem 1:** Large knowledge graph causing slow traversal.

**Solution:** Limit graph depth in queries:
```typescript
await memory_graph_query({
  startEntity: 'JWT',
  maxDepth: 2  // Default, don't exceed 3
});
```

**Problem 2:** Vector embeddings on CPU.

**Solution:** Use API-based embeddings for faster inference:
```env
EMBEDDING_PROVIDER=gemini
GEMINI_API_KEY=your-key
```

---

### "High memory usage"

**Problem:** Large observation history in memory.

**Solution:** Enable auto-eviction:
```env
LESSON_DECAY_ENABLED=true  # Default, ensures old memories evict
CONSOLIDATION_ENABLED=true  # Compress observations into summaries
```

Manually trigger consolidation:
```typescript
await memory_consolidate();
```

---

## Integration Issues

### "Claude Code plugin not loading"

**Problem:** Plugin install incomplete or MCP server not auto-wired.

**Solution:** Since v0.8.9, the plugin auto-wires MCP. Verify:

1. Start server: `npx @agentmemory/agentmemory`
2. In Claude Code:
   ```
   /plugin marketplace add rohitg00/agentmemory
   /plugin install agentmemory
   ```
3. Check health:
   ```bash
   curl http://localhost:3111/agentmemory/health
   ```

If skills fail with "Contains expansion" error, upgrade to v0.8.9+ (skills rewritten as pure prompts).

---

### "Hermes/OpenClaw plugin not capturing"

**Problem:** Plugin not enabled or server URL incorrect.

**Solution:** Check plugin config:

For Hermes (`~/.hermes/plugins/memory/agentmemory/config.yaml`):
```yaml
enabled: true
base_url: http://localhost:3111
```

For OpenClaw (`~/.openclaw/plugins/memory/agentmemory/config.yaml`):
```yaml
enabled: true
base_url: http://localhost:3111
```

Ensure server is running and restart the agent.

---

### "MCP tools not available in agent"

**Problem:** Agent hasn't restarted after MCP config change.

**Solution:** Restart your agent completely. MCP servers are only loaded at agent startup.

Verify MCP connection:
```bash
# Check server is running
curl http://localhost:3111/agentmemory/health

# Test MCP tools directly
npx -y @agentmemory/mcp
```

---

## Data Management

### "How do I backup my memory?"

**Solution:** Use the export endpoint:
```bash
curl http://localhost:3111/agentmemory/export > backup.json
```

Or via MCP:
```typescript
await memory_export({
  format: 'json',
  includeObservations: true,
  includeMemories: true
});
```

Restore later:
```bash
curl -X POST http://localhost:3111/agentmemory/import \
  -H "Content-Type: application/json" \
  --data-binary @backup.json
```

---

### "How do I delete old memories?"

**Solution:** Use the forget endpoint with audit trail:
```bash
curl -X POST http://localhost:3111/agentmemory/forget \
  -H "Content-Type: application/json" \
  -d '{"ids": ["mem-old-123"], "reason": "Outdated information"}'
```

Or via MCP:
```typescript
await memory_governance_delete({
  memoryIds: ['mem-old-123'],
  reason: 'Outdated after refactor'
});
```

---

### "How do I reset everything?"

**Solution:** Delete the data directory:
```bash
rm -rf ~/.agentmemory
```

Restart the server. A fresh database will be created.

---

## Debugging

### "Enable verbose logging"

**Solution:** Run with verbose flag:
```bash
npx @agentmemory/agentmemory --verbose
```

---

### "Check real-time viewer"

**Solution:** Open `http://localhost:3113` to see:
- Live observation stream
- Session explorer
- Memory browser
- Knowledge graph visualization
- Health dashboard
- Token savings calculator

---

### "Run diagnostics"

**Solution:** Use the diagnose endpoint:
```bash
curl http://localhost:3111/agentmemory/diagnose
```

Or via MCP:
```typescript
await memory_diagnose();
```

Response includes health checks and recommendations.

---

### "Auto-heal stuck state"

**Solution:** Use the heal endpoint:
```bash
curl -X POST http://localhost:3111/agentmemory/heal
```

Or via MCP:
```typescript
await memory_heal();
```

Attempts to fix common issues like stuck leases, corrupted indexes, etc.

---

## Getting Help

If you're still stuck:

1. Check the viewer at `http://localhost:3113` for visual debugging
2. Run diagnostics: `curl http://localhost:3111/agentmemory/diagnose`
3. Review verbose logs: `npx @agentmemory/agentmemory --verbose`
4. Check GitHub issues: https://github.com/rohitg00/agentmemory/issues
5. Review CHANGELOG for recent fixes: https://github.com/rohitg00/agentmemory/blob/v0.8.9/CHANGELOG.md
