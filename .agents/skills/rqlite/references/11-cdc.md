# Change Data Capture (CDC)

Streaming database changes from rqlite to external systems.

## Overview

Change Data Capture (CDC) allows you to stream database changes in real-time to external systems. This is useful for:

- **Cache invalidation**: Keep caches synchronized with database
- **Secondary indexes**: Maintain search indexes (Elasticsearch, etc.)
- **Data warehouses**: Stream data for analytics
- **Audit trails**: Track all data modifications
- **Event-driven architectures**: Trigger workflows on data changes
- **Multi-region replication**: Sync data across geographic regions

## How CDC Works in rqlite

rqlite leverages SQLite's Write-Ahead Logging (WAL) to capture changes:

```
Application → rqlite → WAL → CDC Stream → External System
                      ↓
                  SQLite Database
```

Every write operation is first recorded in the WAL, which CDC can then stream to consumers.

## CDC Configuration

### Enable CDC

CDC is enabled via configuration. Create a CDC config file:

```json
{
  "version": 1,
  "type": "kafka",
  "sub": {
    "brokers": ["kafka1:9092", "kafka2:9092"],
    "topic": "rqlite-changes",
    "username": "rqlite-user",
    "password": "kafka-password"
  }
}
```

Start rqlite with CDC:
```bash
rqlited -node-id=1 \
  -cdc-config=cdc-config.json \
  /var/lib/rqlite/node1
```

## Supported Destinations

### Apache Kafka

Stream changes to Kafka topics:

```json
{
  "version": 1,
  "type": "kafka",
  "sub": {
    "brokers": ["kafka1:9092", "kafka2:9092"],
    "topic": "rqlite-changes",
    "username": "",
    "password": "",
    "sasl_mechanism": "PLAIN",
    "tls_enabled": false
  }
}
```

**Message format:**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "operation": "INSERT",
  "table": "users",
  "old_values": null,
  "new_values": {
    "id": 123,
    "name": "Alice",
    "email": "alice@example.com"
  },
  "primary_key": {"id": 123}
}
```

### RabbitMQ

Publish changes to RabbitMQ queues:

```json
{
  "version": 1,
  "type": "rabbitmq",
  "sub": {
    "url": "amqp://user:pass@rabbitmq:5672/",
    "exchange": "rqlite-changes",
    "exchange_type": "topic",
    "routing_key": "database.*"
  }
}
```

### HTTP Endpoint

Post changes to custom HTTP endpoints:

```json
{
  "version": 1,
  "type": "http",
  "sub": {
    "url": "https://webhook.example.com/rqlite-changes",
    "method": "POST",
    "headers": {
      "Authorization": "Bearer token123",
      "Content-Type": "application/json"
    },
    "batch_size": 100,
    "batch_interval": "1s"
  }
}
```

### Local File

Write changes to local file for processing:

```json
{
  "version": 1,
  "type": "file",
  "sub": {
    "path": "/var/log/rqlite/cdc.log",
    "format": "json",
    "max_size": "100MB",
    "rotation": "daily"
  }
}
```

## Change Event Format

All CDC destinations receive changes in a standardized format:

### INSERT Operation

```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "operation": "INSERT",
  "table": "users",
  "database": "main",
  "new_values": {
    "id": 1,
    "name": "Alice",
    "email": "alice@example.com",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "old_values": null,
  "primary_key": {
    "id": 1
  }
}
```

### UPDATE Operation

```json
{
  "timestamp": "2024-01-15T10:35:00.456Z",
  "operation": "UPDATE",
  "table": "users",
  "database": "main",
  "new_values": {
    "id": 1,
    "name": "Alice Smith",
    "email": "alice@example.com",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "old_values": {
    "id": 1,
    "name": "Alice",
    "email": "alice@example.com",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "primary_key": {
    "id": 1
  },
  "changed_columns": ["name"]
}
```

### DELETE Operation

```json
{
  "timestamp": "2024-01-15T10:40:00.789Z",
  "operation": "DELETE",
  "table": "users",
  "database": "main",
  "old_values": {
    "id": 1,
    "name": "Alice Smith",
    "email": "alice@example.com"
  },
  "new_values": null,
  "primary_key": {
    "id": 1
  }
}
```

## Use Cases and Implementations

### Cache Invalidation

Invalidate cache entries when data changes:

```python
# Consumer service
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'rqlite-changes',
    bootstrap_servers=['kafka1:9092'],
    value_deserializer=lambda x: json.loads(x.decode())
)

for message in consumer:
    change = message.value
    
    if change['operation'] in ['INSERT', 'UPDATE', 'DELETE']:
        table = change['table']
        pk = change['primary_key']
        
        # Invalidate cache for this record
        cache_key = f"{table}:{pk['id']}"
        redis_client.delete(cache_key)
        
        # Or invalidate entire table cache
        # redis_client.delete_pattern(f"{table}:*")
```

### Search Index Synchronization

Keep Elasticsearch in sync with database:

```python
from elasticsearch import Elasticsearch

es = Elasticsearch(['elasticsearch:9200'])

for message in consumer:
    change = message.value
    
    table = change['table']
    pk = change['primary_key']
    doc_id = f"{table}_{pk['id']}"
    
    if change['operation'] == 'INSERT':
        # Index new document
        es.index(index=table, id=doc_id, body=change['new_values'])
        
    elif change['operation'] == 'UPDATE':
        # Update existing document
        es.update(index=table, id=doc_id, body={'doc': change['new_values']})
        
    elif change['operation'] == 'DELETE':
        # Remove from index
        es.delete(index=table, id=doc_id, ignore=[400, 404])
```

### Data Warehouse Streaming

Stream changes to analytics warehouse:

```python
import snowflake.connector

conn = snowflake.connector.connect(
    user='user',
    password='password',
    account='account',
    warehouse='warehouse'
)

cursor = conn.cursor()

for message in consumer:
    change = message.value
    
    table = change['table']
    
    if change['operation'] == 'INSERT':
        values = change['new_values']
        columns = ', '.join(values.keys())
        placeholders = ', '.join(['%s'] * len(values))
        
        cursor.execute(
            f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
            list(values.values())
        )
        
    elif change['operation'] == 'UPDATE':
        values = change['new_values']
        pk = change['primary_key']
        
        set_clause = ', '.join([f"{k}=%s" for k in values.keys() if k not in pk])
        where_clause = ' AND '.join([f"{k}=%s" for k in pk.keys()])
        
        cursor.execute(
            f"UPDATE {table} SET {set_clause} WHERE {where_clause}",
            list(values.values()) + list(pk.values())
        )
```

### Audit Trail

Log all changes for compliance:

```python
import logging

logging.basicConfig(filename='audit.log', level=logging.INFO)

for message in consumer:
    change = message.value
    
    audit_entry = {
        'timestamp': change['timestamp'],
        'operation': change['operation'],
        'table': change['table'],
        'primary_key': change['primary_key'],
        'old_values': change['old_values'],
        'new_values': change['new_values'],
        'user': get_current_user()  # From application context
    }
    
    logging.info(json.dumps(audit_entry))
```

### Event-Driven Workflows

Trigger workflows based on data changes:

```python
from celery import Celery

app = Celery('worker', broker='redis://redis:6379/0')

@app.task
def send_welcome_email(user_data):
    # Send welcome email to new user
    pass

@app.task
def update_analytics(user_id):
    # Update analytics dashboards
    pass

for message in consumer:
    change = message.value
    
    if change['table'] == 'users' and change['operation'] == 'INSERT':
        send_welcome_email.delay(change['new_values'])
        
    elif change['table'] == 'orders' and change['operation'] == 'INSERT':
        update_analytics.delay(change['new_values']['user_id'])
```

## Filtering and Selectivity

### Filter by Table

Only stream changes for specific tables:

```json
{
  "version": 1,
  "type": "kafka",
  "filter": {
    "tables": ["users", "orders"]
  },
  "sub": {
    "brokers": ["kafka1:9092"],
    "topic": "rqlite-changes"
  }
}
```

### Filter by Operation

Stream only specific operation types:

```json
{
  "version": 1,
  "type": "kafka",
  "filter": {
    "operations": ["INSERT", "UPDATE"]
  },
  "sub": {
    "brokers": ["kafka1:9092"],
    "topic": "rqlite-changes"
  }
}
```

### Exclude Tables

Stream all except specified tables:

```json
{
  "version": 1,
  "type": "kafka",
  "filter": {
    "exclude_tables": ["sessions", "temp_data"]
  },
  "sub": {
    "brokers": ["kafka1:9092"],
    "topic": "rqlite-changes"
  }
}
```

## Performance Considerations

### Impact on Database

CDC has minimal impact on rqlite performance:
- Reads from WAL (already written for durability)
- Asynchronous streaming (doesn't block writes)
- Configurable batch sizes for efficiency

### Optimizing CDC Performance

1. **Use batching**: Group changes before sending
   ```json
   {
     "batch_size": 100,
     "batch_interval": "1s"
   }
   ```

2. **Filter early**: Only stream needed tables/operations

3. **Tune destination**: Optimize Kafka/RabbitMQ settings

4. **Monitor lag**: Track consumer lag to detect bottlenecks

### Handling High Volume

For high-volume workloads:

```json
{
  "version": 1,
  "type": "kafka",
  "sub": {
    "brokers": ["kafka1:9092", "kafka2:9092", "kafka3:9092"],
    "topic": "rqlite-changes",
    "partitioner": "round_robin",
    "compression": "snappy"
  },
  "filter": {
    "tables": ["high_volume_table"]
  }
}
```

## Monitoring CDC

### Check CDC Status

```bash
# View CDC metrics in status
curl localhost:4001/status | jq '.cdc'

# Example output:
{
  "enabled": true,
  "events_sent": 15234,
  "events_failed": 0,
  "last_event_time": "2024-01-15T10:30:00Z"
}
```

### Monitor Consumer Lag

For Kafka:
```bash
kafka-consumer-groups --bootstrap-server kafka1:9092 \
  --describe --group rqlite-consumer
```

### Alert on CDC Failures

Set up alerts for:
- Events failed to send > 0
- Consumer lag > threshold
- CDC disabled unexpectedly

## Troubleshooting

### CDC Not Sending Events

**Check configuration:**
```bash
# Verify CDC is enabled
curl localhost:4001/status | grep cdc

# Check config file syntax
cat cdc-config.json | python3 -m json.tool
```

### High Consumer Lag

**Scale consumers:**
- Add more consumer instances
- Increase consumer parallelism
- Optimize consumer processing

### Duplicate Events

CDC may deliver events multiple times in failure scenarios. Design consumers to be idempotent:

```python
# Use primary key for idempotency
def process_change(change):
    pk = change['primary_key']
    
    # Check if already processed
    if is_processed(pk):
        return
        
    # Process change
    do_work(change)
    
    # Mark as processed
    mark_processed(pk)
```

## Next Steps

- Set up [monitoring](10-monitoring.md) for CDC health
- Optimize [performance](09-performance.md) for high-volume workloads
- Configure [security](08-security.md) for CDC destinations
- Use [extensions](12-extensions.md) to enrich change events
