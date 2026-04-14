# Mem0 Async Patterns

Non-blocking memory operations for async Python applications including FastAPI, asyncio workers, and concurrent workflows.

## AsyncMemory Overview

`AsyncMemory` provides a non-blocking interface to Mem0's storage layer for use in async frameworks.

```python
from mem0 import AsyncMemory

memory = AsyncMemory()

# All operations are awaitable
result = await memory.add(
    messages=[{"role": "user", "content": "I love hiking"}],
    user_id="alice"
)

results = await memory.search("What does Alice like?", user_id="alice")
```

### Method Parity with Sync Client

| Operation | Async Signature | Notes |
|-----------|----------------|-------|
| Add memories | `await memory.add(...)` | Same arguments as sync |
| Search | `await memory.search(...)` | Returns dict with `results` |
| List all | `await memory.get_all(...)` | Filter by scopes |
| Get one | `await memory.get(memory_id=...)` | Raises `ValueError` if not found |
| Update | `await memory.update(memory_id=..., data=...)` | Partial updates |
| Delete | `await memory.delete(memory_id=...)` | Returns confirmation |
| Delete all | `await memory.delete_all(...)` | Requires scope filter |
| History | `await memory.history(memory_id=...)` | Audit trail |

## FastAPI Integration

### Basic Setup

```python
from fastapi import FastAPI
from mem0 import AsyncMemory

app = FastAPI()
memory = AsyncMemory()  # Single instance per process

@app.post("/memories/")
async def add_memory(messages: list[dict], user_id: str):
    result = await memory.add(messages=messages, user_id=user_id)
    return {"status": "success", "data": result}

@app.get("/memories/search")
async def search_memories(query: str, user_id: str, limit: int = 10):
    result = await memory.search(query=query, user_id=user_id, limit=limit)
    return {"status": "success", "data": result}

@app.delete("/memories/{memory_id}")
async def delete_memory(memory_id: str):
    await memory.delete(memory_id=memory_id)
    return {"status": "deleted"}
```

### Application-Level Initialization

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from mem0 import AsyncMemory

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.memory = AsyncMemory()
    yield
    # Shutdown (cleanup if needed)

app = FastAPI(lifespan=lifespan)

@app.get("/search")
async def search(query: str, user_id: str):
    result = await app.state.memory.search(query=query, user_id=user_id)
    return result
```

### Dependency Injection Pattern

```python
from fastapi import Depends, FastAPI
from typing import AsyncGenerator
from mem0 import AsyncMemory

app = FastAPI()

@asynccontextmanager
async def get_memory() -> AsyncGenerator[AsyncMemory, None]:
    memory = AsyncMemory()
    try:
        yield memory
    finally:
        pass  # Cleanup if needed

async def depend_on_memory() -> AsyncMemory:
    # In practice, reuse a single instance
    return app.state.memory

@app.post("/memories/")
async def add_memory(
    messages: list[dict],
    user_id: str,
    memory: AsyncMemory = Depends(depend_on_memory)
):
    result = await memory.add(messages=messages, user_id=user_id)
    return result
```

## Concurrent Operations

### Batch Adds with asyncio.gather

```python
import asyncio
from mem0 import AsyncMemory

async def batch_add_memories(memory: AsyncMemory, conversations: list[dict]):
    """Add multiple memories concurrently."""
    
    tasks = [
        memory.add(
            messages=conv["messages"],
            user_id=conv["user_id"]
        )
        for conv in conversations
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle any failures
    successful = 0
    failed = 0
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Task {i} failed: {result}")
            failed += 1
        else:
            successful += 1
    
    return {"successful": successful, "failed": failed}

# Usage
memory = AsyncMemory()
conversations = [
    {"messages": [...], "user_id": f"user_{i}"}
    for i in range(100)
]

stats = await batch_add_memories(memory, conversations)
```

### Concurrent Search Operations

```python
async def parallel_search(memory: AsyncMemory, queries: list[tuple[str, str]]):
    """Search for multiple queries concurrently."""
    
    tasks = [
        memory.search(query=query, user_id=user_id)
        for query, user_id in queries
    ]
    
    results = await asyncio.gather(*tasks)
    return results

# Usage
queries = [
    ("travel preferences", "alice"),
    ("dietary restrictions", "bob"),
    ("hobbies and interests", "charlie")
]

results = await parallel_search(memory, queries)
```

### Rate-Limited Concurrent Operations

```python
import asyncio
from mem0 import AsyncMemory

async def rate_limited_add(memory: AsyncMemory, item: dict, semaphore: asyncio.Semaphore):
    """Add memory with rate limiting."""
    async with semaphore:
        await asyncio.sleep(0.1)  # Rate limit delay
        return await memory.add(**item)

async def batch_with_rate_limit(memory: AsyncMemory, items: list[dict], max_concurrent=5):
    """Batch add with concurrency control."""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    tasks = [
        rate_limited_add(memory, item, semaphore)
        for item in items
    ]
    
    return await asyncio.gather(*tasks)

# Usage
memory = AsyncMemory()
items = [{"messages": [...], "user_id": f"user_{i}"} for i in range(100)]
results = await batch_with_rate_limit(memory, items, max_concurrent=10)
```

## Error Handling and Retries

### Retry Decorator

```python
import asyncio
from functools import wraps

def retry_async_operation(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying async memory operations."""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    
                    print(f"Attempt {attempt + 1} failed: {e}")
                    await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
        
        return wrapper
    return decorator

@retry_async_operation(max_retries=3)
async def robust_add(memory: AsyncMemory, messages: list, user_id: str):
    return await memory.add(messages=messages, user_id=user_id)
```

### Timeout with Retry

```python
async def with_timeout_and_retry(operation, max_retries: int = 3, timeout: float = 10.0):
    """Execute operation with timeout and retry logic."""
    
    for attempt in range(max_retries):
        try:
            return await asyncio.wait_for(operation(), timeout=timeout)
        except asyncio.TimeoutError:
            print(f"Timeout on attempt {attempt + 1}")
        except Exception as exc:
            print(f"Error on attempt {attempt + 1}: {exc}")
        
        if attempt < max_retries - 1:
            await asyncio.sleep(2 ** attempt)
    
    raise Exception(f"Operation failed after {max_retries} attempts")

# Usage
memory = AsyncMemory()

async def search_operation():
    return await memory.search("test query", user_id="alice")

result = await with_timeout_and_retry(search_operation, max_retries=3, timeout=5.0)
```

### Circuit Breaker Pattern

```python
class MemoryCircuitBreaker:
    """Circuit breaker for memory operations."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    async def call(self, func, *args, **kwargs):
        """Execute function through circuit breaker."""
        
        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker open")
        
        try:
            result = await func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
    
    def on_success(self):
        self.failure_count = 0
        self.state = "closed"
    
    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"

# Usage
breaker = MemoryCircuitBreaker(failure_threshold=5)
memory = AsyncMemory()

async def protected_search(query: str, user_id: str):
    return await breaker.call(memory.search, query=query, user_id=user_id)
```

## Integration with Other Async APIs

### OpenAI + Mem0

```python
import asyncio
from openai import AsyncOpenAI
from mem0 import AsyncMemory

async_openai = AsyncOpenAI()
memory = AsyncMemory()

async def chat_with_memory(message: str, user_id: str) -> str:
    """Chat with memory-augmented context."""
    
    # Search memories
    search_result = await memory.search(query=message, user_id=user_id, limit=3)
    relevant_memories = search_result["results"]
    memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant_memories)
    
    # Build prompt with memory
    system_prompt = f"""You are a helpful AI assistant.
User Memories:
{memories_str}

Answer based on the user's memories and preferences."""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]
    
    # Get response from OpenAI
    response = await async_openai.chat.completions.create(
        model="gpt-4.1-nano-2025-04-14",
        messages=messages
    )
    
    assistant_response = response.choices[0].message.content
    
    # Save conversation to memory
    messages.append({"role": "assistant", "content": assistant_response})
    await memory.add(messages, user_id=user_id)
    
    return assistant_response

# Usage
response = await chat_with_memory("What should I eat for dinner?", "alice")
```

### Multiple External APIs

```python
import httpx
from mem0 import AsyncMemory

async def fetch_with_memory(http_client: httpx.AsyncClient, memory: AsyncMemory, url: str, user_id: str):
    """HTTP request with memory context."""
    
    # Get user preferences from memory
    prefs = await memory.search(query="preferences", user_id=user_id, limit=2)
    preference_headers = {
        "X-User-Preference": "; ".join([r['memory'] for r in prefs["results"]])
    }
    
    # Make request with context
    response = await http_client.get(url, headers=preference_headers)
    
    # Store interaction
    await memory.add(
        messages=[{"role": "user", "content": f"Accessed {url}"}],
        user_id=user_id
    )
    
    return response

# Usage
async with httpx.AsyncClient() as client:
    memory = AsyncMemory()
    response = await fetch_with_memory(client, memory, "https://api.example.com/data", "alice")
```

## Logging and Observability

### Structured Logging

```python
import logging
import time
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_async_operation(operation_name: str):
    """Decorator for logging async memory operations."""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            logger.info(f"Starting {operation_name}")
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"{operation_name} completed in {duration:.2f}s")
                return result
            except Exception as exc:
                duration = time.time() - start_time
                logger.error(f"{operation_name} failed after {duration:.2f}s: {exc}")
                raise
        
        return wrapper
    return decorator

@log_async_operation("Memory Add")
async def logged_memory_add(memory: AsyncMemory, messages: list, user_id: str):
    return await memory.add(messages=messages, user_id=user_id)

@log_async_operation("Memory Search")
async def logged_memory_search(memory: AsyncMemory, query: str, user_id: str):
    return await memory.search(query=query, user_id=user_id)
```

### Metrics Collection

```python
import asyncio
from collections import defaultdict
from mem0 import AsyncMemory

class MemoryMetrics:
    """Collect metrics on memory operations."""
    
    def __init__(self):
        self.latencies = defaultdict(list)
        self.error_counts = defaultdict(int)
        self.success_counts = defaultdict(int)
    
    async def record_operation(self, operation: str, start_time: float, success: bool, error: Exception = None):
        """Record operation metrics."""
        latency = time.time() - start_time
        
        self.latencies[operation].append(latency)
        if success:
            self.success_counts[operation] += 1
        else:
            self.error_counts[operation] += 1
    
    def get_stats(self, operation: str):
        """Get statistics for an operation."""
        latencies = self.latencies[operation]
        
        return {
            "operation": operation,
            "total_calls": len(latencies),
            "avg_latency": sum(latencies) / len(latencies) if latencies else 0,
            "p95_latency": sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0,
            "success_rate": self.success_counts[operation] / len(latencies) if latencies else 0,
            "error_count": self.error_counts[operation]
        }

# Usage with wrapper
metrics = MemoryMetrics()
memory = AsyncMemory()

async def instrumented_search(query: str, user_id: str):
    start_time = time.time()
    try:
        result = await memory.search(query=query, user_id=user_id)
        await metrics.record_operation("search", start_time, True)
        return result
    except Exception as e:
        await metrics.record_operation("search", start_time, False, e)
        raise

# Get stats
stats = metrics.get_stats("search")
print(f"Search P95 latency: {stats['p95_latency']:.2f}s")
```

## Best Practices

1. **Reuse AsyncMemory instances** - Create once per process, don't recreate per request
2. **Use asyncio.gather for batching** - Parallelize independent operations
3. **Implement circuit breakers** - Prevent cascade failures in production
4. **Add timeouts to all operations** - Avoid hanging requests
5. **Log with context** - Include user_id and operation type in logs
6. **Monitor latency percentiles** - Track P95/P99 for SLA compliance
7. **Handle partial failures** - Use `return_exceptions=True` in gather
8. **Test with load** - Verify concurrent behavior under stress

## Troubleshooting Async Issues

| Issue | Solution |
|-------|----------|
| Event loop blocked | Ensure all operations are properly awaited |
| Memory not persisting | Check `await` is used on add operations |
| Connection pool exhausted | Reuse AsyncMemory instance, don't recreate |
| Timeout errors | Add retry logic with exponential backoff |
| Race conditions | Use asyncio.Lock for shared state |
