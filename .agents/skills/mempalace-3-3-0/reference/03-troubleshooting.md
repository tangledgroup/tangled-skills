# Troubleshooting

### Palace Not Found

```bash
# Initialize first
mempalace init ~/projects/myapp

# Or specify palace path explicitly
mempalace mine ~/projects/myapp --palace ~/.mempalace/palace
```

### ChromaDB Version Mismatch

```bash
# Check current version
mempalace status

# Migrate if needed
mempalace migrate --dry-run        # preview changes
mempalace migrate --yes            # apply migration
```

### Rebuild Palace Index

```bash
# Repair vector index from SQLite metadata
mempalace repair --yes

# Creates backup at ~/.mempalace/palace.backup
```

### Split Concatenated Transcripts

Some exports concatenate multiple sessions:

```bash
# Preview split
mempalace split ~/chats/ --dry-run

# Split files with 3+ sessions
mempalace split ~/chats/ --min-sessions 3

# Custom output directory
mempalace split ~/chats/ --output-dir ~/chats-split/
```

### No Closets Created

Closets are only created for project mining (not conversation mode yet):

```bash
# Mine as project to create closets
mempalace mine ~/projects/myapp  # creates closets

# Conversations use direct drawer search (fallback path)
mempalace mine ~/chats/ --mode convos  # no closets yet
```
