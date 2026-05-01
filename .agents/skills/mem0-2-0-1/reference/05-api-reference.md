# API Reference

All API Reference docs describe Mem0 Platform REST endpoints (requires API key). Base URL: `https://api.mem0.ai/v1/`.

## Authentication

All API requests require token-based authentication. Include your API key in the `Authorization` header:

```
Authorization: Bearer YOUR_API_KEY
```

## Core Memory Operations

### Add Memories

```
POST /v1/memories/add
```

Store new memories from conversations and interactions.

```json
{
  "messages": [
    {"role": "user", "content": "I love hiking on weekends"},
    {"role": "assistant", "content": "Got it!"}
  ],
  "user_id": "alice"
}
```

### Search Memories

```
POST /v1/memories/search
```

Find relevant memories using semantic search with filters.

```json
{
  "query": "What does Alice like to do?",
  "filters": {"user_id": "alice"},
  "top_k": 5,
  "threshold": 0.15
}
```

### Get All Memories

```
POST /v1/memories
```

Fetch all memories for a specific entity with pagination.

```json
{
  "filters": {"user_id": "alice"}
}
```

### Get Memory

```
GET /v1/memories/{memory_id}
```

Fetch one memory by ID.

### Update Memory

```
PUT /v1/memories/{memory_id}
```

Edit a memory in place.

```json
{
  "data": "Alice loves mountain hiking"
}
```

### Delete Memory

```
DELETE /v1/memories/{memory_id}
```

Remove one memory.

### Delete All Memories

```
DELETE /v1/memories
```

Purge memories matching a scope.

```json
{
  "filters": {"user_id": "alice"}
}
```

## Advanced Memory Operations

### Batch Update

```
PUT /v1/memories/batch-update
```

Update many memories in one call.

### Batch Delete

```
DELETE /v1/memories/batch-delete
```

Delete many memories in one call.

### Memory History

```
GET /v1/memories/{memory_id}/history
```

Get the change log for a memory.

### Feedback

```
POST /v1/memories/feedback
```

Capture user signals on memory quality.

```json
{
  "memory_id": "<id>",
  "score": 1.0,
  "comment": "Accurate"
}
```

### Create Memory Export

```
POST /v1/memories/export
```

Kick off an async export job.

### Get Memory Export

```
GET /v1/memories/export/{export_id}
```

Fetch the result of an export job.

## Events APIs

### Get Events

```
GET /v1/events
```

List async memory operation events.

### Get Event

```
GET /v1/events/{event_id}
```

Fetch one event by ID.

## Entities APIs

### Get Users

```
GET /v1/entities/users
```

List users, agents, or apps known to a project.

### Delete User

```
DELETE /v1/entities/users/{user_id}
```

Remove an entity and all its memories.

## Organizations & Projects

### Create Organization

```
POST /v1/organizations
```

Set up a new organization for multi-tenant isolation.

### Get Organizations

```
GET /v1/organizations
```

List organizations.

### Create Project

```
POST /v1/projects
```

Create a project inside an organization.

### Add Member

```
POST /v1/projects/{project_id}/members
```

Invite a member to a project.

## Webhooks

### Create Webhook

```
POST /v1/webhooks
```

Register a webhook endpoint for real-time notifications.

```json
{
  "url": "https://your-app.com/webhook",
  "events": ["memory.created", "memory.updated"]
}
```

### Update / Delete Webhook

```
PUT /v1/webhooks/{webhook_id}
DELETE /v1/webhooks/{webhook_id}
```

Modify or remove webhook configuration.

## OSS Server Endpoints

The self-hosted server provides compatible endpoints at `http://localhost:8888/` with the same request/response shapes. Auth is handled via JWT tokens (or `AUTH_DISABLED=true` for local dev).
