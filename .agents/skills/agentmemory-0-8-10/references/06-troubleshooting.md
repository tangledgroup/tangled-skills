# agentmemory Troubleshooting Guide

## Common Issues

### Memory Not Capturing

#### Symptom
Agent completes tasks but no observations appear in viewer or search results.

#### Diagnosis

**1. Check iii-engine is running:**
```bash
curl http://localhost:49134/health
# Should return: {"status": "ok", "workers": [...]}
```

**2. Verify agentmemory worker connected:**
```bash
curl http://localhost:3111/agentmemory/health
# Check workers array includes "agentmemory"
```

**3. Check hook installation (Claude Code):**
```bash
ls -la ~/.claude/plugins/agentmemory/hooks/
# Should contain 12 hook scripts
```

**4. Verify session started:**
```bash
curl http://localhost:3111/agentmemory/sessions?limit=1
# Check for active session with current project path
```

#### Solutions

**iii-engine not running:**
```bash
# Start iii-engine (usually auto-started by agentmemory)
npx iii-engine

# Or via Docker
docker-compose up -d iii-engine
```

**Hooks not installed:**
```bash
# Reinstall Claude Code plugin
agentmemory install-plugin claude-code

# Verify hooks are executable
chmod +x ~/.claude/plugins/agentmemory/hooks/*.js
```

**Wrong project path:**
```bash
# Check session project matches current directory
curl http://localhost:3111/agentmemory/sessions

# If mismatch, end old session and start new one
curl -X POST http://localhost:3111/agentmemory/session/end
```

---

### Search Returning No Results

#### Symptom
`memory_recall` or `/search` returns empty results despite having sessions.

#### Diagnosis

**1. Check observation count:**
```bash
curl http://localhost:3111/agentmemory/sessions
# Look for observationCount > 0
```

**2. Check compression status:**
```bash
curl http://localhost:3111/agentmemory/metrics
# Look for mem::compress success rate
```

**3. Test BM25 index:**
```bash
curl -X POST http://localhost:3111/agentmemory/diagnostics \
  -d '{"checkIndex": true}'
```

#### Solutions

**No observations captured:**
- See "Memory Not Capturing" above

**Observations not compressed:**
```bash
# Check LLM provider configuration
curl http://localhost:3111/agentmemory/config
# Verify provider and API key are set

# Manually trigger compression
curl -X POST http://localhost:3111/agentmemory/compress-pending
```

**BM25 index corrupted:**
```bash
# Rebuild index
curl -X POST http://localhost:3111/agentmemory/rebuild-index \
  -d '{"force": true}'

# Monitor progress
curl http://localhost:3111/agentmemory/diagnostics?verbose=true
```

**Query too specific:**
```bash
# Try broader query
curl -X POST http://localhost:3111/agentmemory/search \
  -d '{"query": "authentication", "limit": 10}'

# Check smart-search with query expansion
curl -X POST http://localhost:3111/agentmemory/smart-search \
  -d '{"query": "auth", "limit": 10}'
```

---

### Viewer Not Connecting

#### Symptom
Real-time viewer shows "Disconnected" or fails to load.

#### Diagnosis

**1. Check streams server:**
```bash
netstat -an | grep 3112
# Should show LISTEN on port 3112
```

**2. Test WebSocket connection:**
```bash
wscat -c ws://localhost:3112
# Should connect without error
```

**3. Check browser console:**
```javascript
// Look for CORS or TLS errors
// View page source at http://localhost:3111/agentmemory/viewer
```

#### Solutions

**Streams server not running:**
```bash
# Restart agentmemory
pkill agentmemory
agentmemory start

# Or restart Docker containers
docker-compose restart
```

**Wrong port:**
```bash
# Check configured port
curl http://localhost:3111/agentmemory/config | grep streamsPort

# Update viewer URL to match
# Viewer should connect to ws://localhost:${streamsPort}
```

**CORS issues:**
```bash
# Start with CORS enabled (development only)
III_CORS_ENABLED=true agentmemory start
```

**TLS/HTTPS required:**
```bash
# Use HTTPS for viewer in production
# Configure reverse proxy (nginx example below)
```

**Nginx reverse proxy configuration:**
```nginx
server {
    listen 443 ssl;
    server_name memory.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # REST API
    location /agentmemory {
        proxy_pass http://localhost:3111;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket streams
    location /streams {
        proxy_pass http://localhost:3112;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

### Embedding Provider Failing

#### Symptom
Vector search not working, fallback to BM25-only mode.

#### Diagnosis

**1. Check embedding provider config:**
```bash
curl http://localhost:3111/agentmemory/config | grep -A2 embedding
```

**2. Test embedding generation:**
```bash
curl -X POST http://localhost:3111/agentmemory/test-embedding \
  -d '{"text": "test query", "provider": "openai"}'
```

**3. Check diagnostics:**
```bash
curl -X POST http://localhost:3111/agentmemory/diagnostics \
  -d '{"checkEmbeddings": true}'
```

#### Solutions

**API key not set:**
```bash
# Set API key in ~/.agentmemory/.env
echo "OPENAI_API_KEY=sk-..." >> ~/.agentmemory/.env

# Restart agentmemory
pkill agentmemory && agentmemory start
```

**Local provider not installed:**
```bash
# Install transformers for local embeddings
npm install @xenova/transformers

# Set provider to local
echo "EMBEDDING_PROVIDER=local" >> ~/.agentmemory/.env
```

**Rate limit exceeded:**
```bash
# Configure fallback providers
cat >> ~/.agentmemory/.env << EOF
FALLBACK_PROVIDERS=[
  {"provider": "gemini", "model": "gemini-embedding-exp-03-07", "apiKeyEnv": "GEMINI_API_KEY"},
  {"provider": "voyage", "model": "voyage-3", "apiKeyEnv": "VOYAGE_API_KEY"}
]
EOF

# Restart
pkill agentmemory && agentmemory start
```

**Dimension mismatch:**
```bash
# Check embedding dimensions match index
curl http://localhost:3111/agentmemory/diagnostics

# If mismatch, rebuild index with correct dimensions
curl -X POST http://localhost:3111/agentmemory/rebuild-index
```

---

### LLM Compression Failing

#### Symptom
Observations captured but not compressed into memories.

#### Diagnosis

**1. Check compression metrics:**
```bash
curl http://localhost:3111/agentmemory/metrics
# Look for mem::compress failureCount > 0
```

**2. Check provider configuration:**
```bash
curl http://localhost:3111/agentmemory/config | grep -A4 provider
```

**3. View compression errors:**
```bash
# Check logs
tail -f ~/.agentmemory/logs/compression.log
```

#### Solutions

**Provider API key invalid:**
```bash
# Test API key
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":10,"messages":[{"role":"user","content":"test"}]}'

# Update key if invalid
sed -i 's/ANTHROPIC_API_KEY=.*/ANTHROPIC_API_KEY=sk-ant-.../' ~/.agentmemory/.env
```

**Model not supported:**
```bash
# Use supported model
echo "ANTHROPIC_MODEL=claude-sonnet-4-20250514" >> ~/.agentmemory/.env
# or
echo "GEMINI_MODEL=gemini-2.0-flash" >> ~/.agentmemory/.env
```

**Token limit exceeded:**
```bash
# Increase max tokens for compression
echo "MAX_TOKENS=8192" >> ~/.agentmemory/.env

# Reduce observation batch size
echo "MAX_OBS_PER_SESSION=200" >> ~/.agentmemory/.env
```

**Network timeout:**
```bash
# Increase timeout
echo "COMPRESSION_TIMEOUT_MS=60000" >> ~/.agentmemory/.env

# Configure retry policy
echo "COMPRESSION_MAX_RETRIES=3" >> ~/.agentmemory/.env
```

---

### Knowledge Graph Issues

#### Symptom
Relations not appearing, graph queries return empty results.

#### Diagnosis

**1. Check graph statistics:**
```bash
curl -X POST http://localhost:3111/agentmemory/diagnostics \
  -d '{"checkGraph": true}'
```

**2. List graph nodes:**
```bash
curl "http://localhost:3111/agentmemory/graph/nodes?limit=5"
```

**3. List graph edges:**
```bash
curl "http://localhost:3111/agentmemory/graph/edges?limit=5"
```

#### Solutions

**Graph extraction disabled:**
```bash
# Enable graph extraction
echo "GRAPH_EXTRACTION=true" >> ~/.agentmemory/.env

# Restart
pkill agentmemory && agentmemory start
```

**Confidence threshold too high:**
```bash
# Lower confidence threshold
echo "GRAPH_CONFIDENCE_THRESHOLD=0.3" >> ~/.agentmemory/.env

# Query with lower threshold
curl -X POST http://localhost:3111/agentmemory/graph-query \
  -d '{"startNodeId": "mem_abc123", "minConfidence": 0.3}'
```

**Graph corrupted:**
```bash
# Rebuild graph from memories
curl -X POST http://localhost:3111/agentmemory/graph/rebuild

# Monitor progress
curl http://localhost:3111/agentmemory/diagnostics?checkGraph=true
```

---

### Team Sync Failing

#### Symptom
Team memories not syncing between members.

#### Diagnosis

**1. Check team configuration:**
```bash
curl http://localhost:3111/agentmemory/team/config \
  -d '{"teamId": "my-team"}'
```

**2. Test sync manually:**
```bash
curl -X POST http://localhost:3111/agentmemory/team/sync \
  -d '{"teamId": "my-team", "verbose": true}'
```

**3. Check mesh connectivity (if using mesh):**
```bash
curl http://localhost:3111/agentmemory/mesh/status
```

#### Solutions

**Team not created:**
```bash
# Create team first
curl -X POST http://localhost:3111/agentmemory/team/create \
  -d '{"teamId": "my-team", "name": "My Team"}'
```

**Auth token mismatch:**
```bash
# Ensure all team members use same AGENTMEMORY_SECRET
# Or configure team-specific auth
curl -X POST http://localhost:3111/agentmemory/team/auth \
  -d '{"teamId": "my-team", "generateToken": true}'
```

**Governance policy blocking:**
```bash
# Check governance policies
curl http://localhost:3111/agentmemory/governance/get \
  -d '{"teamId": "my-team"}'

# Adjust if too restrictive
curl -X POST http://localhost:3111/agentmemory/governance/set \
  -d '{
    "teamId": "my-team",
    "policies": {"requireApproval": false}
  }'
```

---

### Performance Issues

#### Symptom
Slow search responses, high memory usage, laggy viewer.

#### Diagnosis

**1. Check system metrics:**
```bash
curl http://localhost:3111/agentmemory/health
# Look at memory.heapUsed, cpu.percent, eventLoopLagMs
```

**2. Check function latency:**
```bash
curl http://localhost:3111/agentmemory/metrics
# Look for high avgLatencyMs values
```

**3. Profile database queries:**
```bash
# Enable query logging
echo "SQLITE_LOG_QUERIES=true" >> ~/.agentmemory/.env
```

#### Solutions

**Too many observations:**
```bash
# Increase consolidation frequency
echo "AUTO_CONSOLIDATE=true" >> ~/.agentmemory/.env
echo "CONSOLIDATION_THRESHOLD=100" >> ~/.agentmemory/.env

# Run manual consolidation
curl -X POST http://localhost:3111/agentmemory/consolidate
```

**Index too large:**
```bash
# Evict low-retention memories
curl -X POST http://localhost:3111/agentmemory/evict \
  -d '{"minRetentionScore": 0.1, "dryRun": false}'

# Rebuild index with pruning
curl -X POST http://localhost:3111/agentmemory/rebuild-index \
  -d '{"pruneOld": true, "maxAgeDays": 180}'
```

**Memory leak:**
```bash
# Restart agentmemory regularly
# Set up systemd service with restart policy
cat > /etc/systemd/system/agentmemory.service << EOF
[Unit]
Description=agentmemory Service
After=network.target

[Service]
Type=simple
User=${USER}
ExecStart=${HOME}/.npm-global/bin/agentmemory start
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable agentmemory
systemctl restart agentmemory
```

**Embedding bottleneck:**
```bash
# Use faster embedding model
echo "EMBEDDING_PROVIDER=local" >> ~/.agentmemory/.env
# or use cached embeddings
echo "EMBEDDING_CACHE_ENABLED=true" >> ~/.agentmemory/.env
```

---

### Data Corruption

#### Symptom
Errors reading data, SQLite database errors, inconsistent state.

#### Diagnosis

**1. Check database integrity:**
```bash
sqlite3 ~/.agentmemory/state_store.db "PRAGMA integrity_check;"
# Should return: ok
```

**2. Validate export:**
```bash
curl http://localhost:3111/agentmemory/export > /tmp/backup.json
python3 -c "import json; json.load(open('/tmp/backup.json')); print('✓ Valid JSON')"
```

**3. Check for partial writes:**
```bash
curl -X POST http://localhost:3111/agentmemory/diagnostics \
  -d '{"checkIntegrity": true}'
```

#### Solutions

**Database corrupted:**
```bash
# Stop agentmemory
pkill agentmemory

# Backup current database
cp ~/.agentmemory/state_store.db ~/.agentmemory/state_store.db.corrupted

# Restore from last backup
cp ~/.agentmemory/state_store.db.backup ~/.agentmemory/state_store.db

# Or rebuild from export
curl http://localhost:3111/agentmemory/export > /tmp/full-export.json
# Then import into fresh database
```

**Enable automatic backups:**
```bash
echo "BACKUP_INTERVAL_HOURS=24" >> ~/.agentmemory/.env
echo "BACKUP_RETENTION_COUNT=7" >> ~/.agentmemory/.env
```

**Prevent future corruption:**
```bash
# Enable WAL mode for SQLite
echo "SQLITE_WAL_MODE=true" >> ~/.agentmemory/.env

# Enable synchronous writes (slower but safer)
echo "SQLITE_SYNC=NORMAL" >> ~/.agentmemory/.env
```

---

### Migration Issues

#### Symptom
Data from older version not importing correctly.

#### Diagnosis

**1. Check export version:**
```bash
python3 -c "import json; d=json.load(open('export.json')); print(d.get('version'))"
```

**2. Test import in dry-run mode:**
```bash
curl -X POST http://localhost:3111/agentmemory/import \
  -d '{
    "filePath": "/path/to/export.json",
    "dryRun": true
  }'
```

#### Solutions

**Unsupported version:**
```bash
# Upgrade agentmemory first
npm install -g @agentmemory/agentmemory@latest

# Check supported versions
curl http://localhost:3111/agentmemory/config | grep supportedVersions
```

**Schema mismatch:**
```bash
# Use migration endpoint
curl -X POST http://localhost:3111/agentmemory/migrate \
  -d '{
    "sourceVersion": "0.7.0",
    "targetVersion": "0.8.10"
  }'
```

**Partial import:**
```bash
# Import in batches
curl -X POST http://localhost:3111/agentmemory/import \
  -d '{
    "filePath": "/path/to/export.json",
    "sections": ["sessions"],
    "dryRun": false
  }'

# Then import memories
curl -X POST http://localhost:3111/agentmemory/import \
  -d '{
    "filePath": "/path/to/export.json",
    "sections": ["memories", "summaries"],
    "dryRun": false
  }'
```

---

## Debug Mode

Enable verbose logging for troubleshooting:

```bash
# Start in debug mode
AGENTMEMORY_DEBUG=true agentmemory start

# Or enable via API
curl -X POST http://localhost:3111/agentmemory/debug/enable \
  -d '{"level": "verbose", "areas": ["compression", "search", "graph"]}'
```

**Log locations:**
- Main logs: `~/.agentmemory/logs/agentmemory.log`
- Compression logs: `~/.agentmemory/logs/compression.log`
- Search logs: `~/.agentmemory/logs/search.log`
- Error logs: `~/.agentmemory/logs/errors.log`

## Collecting Diagnostics

Generate diagnostics report for support:

```bash
curl -X POST http://localhost:3111/agentmemory/diagnostics/full \
  -d '{
    "includeConfig": true,
    "includeMetrics": true,
    "includeSampleData": true
  }' > /tmp/agentmemory-diagnostics.json

# Share the diagnostics JSON with maintainers
```

## Getting Help

1. **Check documentation**: https://github.com/rohitg00/agentmemory/tree/v0.8.10
2. **Review issues**: https://github.com/rohitg00/agentmemory/issues
3. **Run diagnostics**: Use the diagnostic endpoints above
4. **Check logs**: Review `~/.agentmemory/logs/` for errors
5. **Test with demo**: Run `agentmemory demo` to verify installation
