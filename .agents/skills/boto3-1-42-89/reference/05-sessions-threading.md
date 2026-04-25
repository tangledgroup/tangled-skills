# Sessions and Threading

## Session Fundamentals

### What is a Session?

A `Session` object manages state for AWS connections including:
- Credentials
- Region configuration
- Profile settings
- Service clients and resources

### Default Session

Boto3 creates a default session automatically when you use the module-level functions:

```python
import boto3

# These all use the default session
s3 = boto3.client('s3')
ec2 = boto3.resource('ec2')
dynamodb = boto3.resource('dynamodb')
```

### Creating Custom Sessions

```python
import boto3

# Create a new session with default settings
session = boto3.session.Session()

# Create clients from the session
s3 = session.client('s3')
ec2 = session.resource('ec2')

# Create session with specific profile
session = boto3.Session(profile_name='production')
s3 = session.client('s3')

# Create session with explicit credentials (not recommended)
session = boto3.Session(
    aws_access_key_id='ACCESS_KEY',
    aws_secret_access_key='SECRET_KEY',
    region_name='us-west-2'
)
dynamodb = session.client('dynamodb')

# Create session with profile and override region
session = boto3.Session(
    profile_name='production',
    region_name='eu-west-1'  # Override profile's region
)
```

## Session Configuration

### Using Profiles

```python
import boto3

# Use default profile (from ~/.aws/credentials and ~/.aws/config)
session = boto3.Session()

# Use named profile
prod_session = boto3.Session(profile_name='production')
dev_session = boto3.Session(profile_name='development')

# Create clients from each session
prod_s3 = prod_session.client('s3')
dev_s3 = dev_session.client('s3')
```

### Session with Config Object

```python
import boto3
from botocore.config import Config

# Create config with retry settings
config = Config(
    retries={
        'mode': 'standard',
        'total_max_attempts': 10
    },
    connect_timeout=10,
    reads_timeout=60
)

# Create session and pass config to clients
session = boto3.Session(profile_name='production')
s3 = session.client('s3', config=config)
```

### Accessing Session Metadata

```python
import boto3

session = boto3.Session(profile_name='production')

# Get session credentials
creds = session.get_credentials()
if creds:
    print(f"Access Key: {creds.access_key}")
    print(f"Secret Key: {creds.secret_key}")
    print(f"Token: {creds.token}")

# Get session region
print(session.region_name)

# Get session profile name
print(session.profile)

# Get underlying botocore session
botocore_session = session._session
print(botocore_session.user_agent())
```

## Thread Safety Guidelines

### Thread-Safe Components

| Component | Thread-Safe? | Can Share Across Threads? |
|-----------|--------------|---------------------------|
| **Client** | ✅ Yes | ✅ Yes (recommended) |
| **Resource** | ❌ No | ❌ No (create per thread) |
| **Session** | ❌ No | ❌ No (create per thread) |
| **Paginator** | ⚠️ Limited | ⚠️ Create per thread |
| **Config** | ✅ Yes | ✅ Yes (immutable) |

### Using Clients in Threads (Safe)

```python
import boto3
from concurrent.futures import ThreadPoolExecutor

# Create single client - safe to share across threads
s3_client = boto3.client('s3', region_name='us-east-1')

def upload_file(filename):
    """Thread-safe function using shared client"""
    with open(filename, 'rb') as f:
        s3_client.put_object(
            Bucket='my-bucket',
            Key=filename,
            Body=f.read()
        )
    return f"Uploaded {filename}"

# Use thread pool with shared client
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(upload_file, ['file1.txt', 'file2.txt', 'file3.txt']))

for result in results:
    print(result)
```

### Using Resources in Threads (Not Safe)

```python
import boto3
from concurrent.futures import ThreadPoolExecutor

def upload_with_resource(filename):
    """Create new resource per thread - NOT sharing"""
    # Create new session and resource for this thread
    session = boto3.session.Session()
    s3 = session.resource('s3')
    bucket = s3.Bucket('my-bucket')
    
    bucket.upload_file(filename, filename)
    return f"Uploaded {filename}"

# Each thread gets its own resource
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(upload_with_resource, ['file1.txt', 'file2.txt']))
```

### Using Sessions in Threads (Not Safe)

```python
import boto3
import boto3.session
from concurrent.futures import ThreadPoolExecutor

def worker(task_id):
    """Create new session per thread"""
    # Create thread-local session
    session = boto3.session.Session()
    s3_client = session.client('s3')
    
    # Use client for this thread's operations
    response = s3_client.list_buckets()
    return len(response.get('Buckets', []))

# Each thread creates its own session
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(worker, range(10)))
```

## Multi-Threading Patterns

### Pattern 1: Shared Client with Thread Pool

```python
import boto3
from concurrent.futures import ThreadPoolExecutor, as_completed

class S3Uploader:
    def __init__(self, bucket_name, region='us-east-1'):
        self.bucket = bucket_name
        # Single client shared across threads
        self.s3_client = boto3.client('s3', region_name=region)
        
    def upload_single(self, local_path, s3_key=None):
        """Upload a single file"""
        if s3_key is None:
            s3_key = local_path
            
        with open(local_path, 'rb') as f:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=s3_key,
                Body=f.read()
            )
        return s3_key
        
    def upload_multiple(self, file_paths, max_workers=10):
        """Upload multiple files in parallel"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all upload tasks
            future_to_file = {
                executor.submit(self.upload_single, fp): fp 
                for fp in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_file):
                filepath = future_to_file[future]
                try:
                    result = future.result()
                    results.append(('success', result))
                except Exception as e:
                    results.append(('error', filepath, str(e)))
                    
        return results

# Usage
uploader = S3Uploader('my-bucket')
files = ['file1.txt', 'file2.txt', 'file3.txt', 'file4.txt']
results = uploader.upload_multiple(files, max_workers=5)

for result in results:
    if result[0] == 'success':
        print(f"Uploaded: {result[1]}")
    else:
        print(f"Failed: {result[1]} - {result[2]}")
```

### Pattern 2: Thread-Local Sessions

```python
import boto3
import boto3.session
from concurrent.futures import ThreadPoolExecutor
import threading

# Thread-local storage for sessions
thread_local = threading.local()

def get_thread_local_session():
    """Get or create a session for the current thread"""
    if not hasattr(thread_local, 'session'):
        thread_local.session = boto3.session.Session()
    return thread_local.session

def process_data(data_item):
    """Process data using thread-local session"""
    session = get_thread_local_session()
    s3_client = session.client('s3')
    
    # Use client for operations
    response = s3_client.list_buckets()
    bucket_count = len(response.get('Buckets', []))
    
    return {
        'item': data_item,
        'bucket_count': bucket_count
    }

# Process items in parallel
items = list(range(100))
with ThreadPoolExecutor(max_workers=20) as executor:
    results = list(executor.map(process_data, items))
```

### Pattern 3: Client Factory for Multiple Regions

```python
import boto3
from botocore.config import Config
from concurrent.futures import ThreadPoolExecutor
from typing import Dict

class MultiRegionClientFactory:
    """Thread-safe factory for creating region-specific clients"""
    
    def __init__(self, profile=None):
        self.profile = profile
        self._clients: Dict[tuple, boto3.client] = {}
        self._lock = threading.Lock()
        
    def _get_client_key(self, service_name: str, region_name: str) -> tuple:
        return (service_name, region_name)
    
    def get_client(self, service_name: str, region_name: str = None, **kwargs):
        """Get or create a client for the specified service and region"""
        if region_name is None:
            region_name = 'us-east-1'
            
        key = self._get_client_key(service_name, region_name)
        
        # Check if client exists
        with self._lock:
            if key not in self._clients:
                # Create new client
                session = boto3.Session(profile_name=self.profile)
                
                client_kwargs = {
                    'region_name': region_name,
                    **kwargs
                }
                
                self._clients[key] = session.client(service_name, **client_kwargs)
                
        return self._clients[key]

# Usage
factory = MultiRegionClientFactory(profile='production')

def process_in_region(region):
    """Process data in a specific region"""
    s3_client = factory.get_client('s3', region)
    response = s3_client.list_buckets()
    return {region: len(response.get('Buckets', []))}

# Process multiple regions in parallel
regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-northeast-1']
with ThreadPoolExecutor(max_workers=4) as executor:
    results = dict(executor.map(process_in_region, regions))

print(results)
# {'us-east-1': 5, 'us-west-2': 3, 'eu-west-1': 2, 'ap-northeast-1': 1}
```

## Multi-Processing Patterns

### Process Pool with Local Clients

Processes cannot share clients due to serialization limitations:

```python
import boto3
from multiprocessing import Pool

def process_in_worker(args):
    """Each process creates its own client"""
    filename, bucket = args
    
    # Create new client in this process
    s3_client = boto3.client('s3')
    
    # Download file
    response = s3_client.get_object(Bucket=bucket, Key=filename)
    content = response['Body'].read()
    
    # Process content
    processed = content.decode().upper()
    
    # Upload result
    s3_client.put_object(
        Bucket=bucket,
        Key=f'processed/{filename}',
        Body=processed.encode()
    )
    
    return filename

# Use process pool
if __name__ == '__main__':
    files = [('file1.txt', 'my-bucket'), ('file2.txt', 'my-bucket')]
    
    with Pool(processes=4) as pool:
        results = pool.map(process_in_worker, files)
    
    print(f"Processed: {results}")
```

## Connection Management

### Configuring Connection Pooling

```python
from botocore.config import Config
import boto3

# Configure connection pooling
config = Config(
    # Maximum number of connections in pool
    max_pool_size=10,
    
    # TCP keepalive
    tcp_keepalive=True,
    
    # Keepalive interval (seconds)
    tcp_keepalive_idle_timeout=60,
    tcp_keepalive_interval=10,
    tcp_keepalive_count=5,
    
    # Timeouts
    connect_timeout=10,
    reads_timeout=60
)

s3 = boto3.client('s3', config=config)
```

### Connection Limits by Region

```python
import boto3
from botocore.config import Config
from concurrent.futures import ThreadPoolExecutor

# Create region-specific clients with connection limits
def create_region_client(region):
    config = Config(
        max_pool_size=20,  # Higher for parallel workloads
        retries={'mode': 'standard', 'total_max_attempts': 10}
    )
    return boto3.client('s3', region_name=region, config=config)

# Create clients for different regions
us_east_client = create_region_client('us-east-1')
eu_west_client = create_region_client('eu-west-1')

def upload_to_region(args):
    region, filename = args
    
    # Select appropriate client
    client = us_east_client if region == 'us-east-1' else eu_west_client
    
    with open(filename, 'rb') as f:
        client.put_object(
            Bucket=f'my-bucket-{region}',
            Key=filename,
            Body=f.read()
        )
    
    return f"{region}: {filename}"

# Upload to multiple regions in parallel
tasks = [
    ('us-east-1', 'file1.txt'),
    ('eu-west-1', 'file2.txt'),
    ('us-east-1', 'file3.txt'),
]

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(upload_to_region, tasks))
```

## Best Practices

1. **Reuse clients** in multi-threaded applications (they're thread-safe)
2. **Create new sessions per thread** when using resources or session-specific config
3. **Use connection pooling** for high-throughput workloads
4. **Implement proper error handling** in worker functions
5. **Limit concurrent connections** to avoid throttling
6. **Use context managers** for resource cleanup when needed
7. **Test with realistic loads** to identify bottlenecks

## Debugging Thread Issues

### Identifying Race Conditions

```python
import boto3
import threading
import logging

logging.basicConfig(level=logging.DEBUG)

# Enable Boto3 debug logging
boto3.set_stream_logger('botocore', logging.DEBUG)

class SharedResourceCounter:
    def __init__(self):
        self.s3 = boto3.resource('s3')
        self.count = 0
        self.lock = threading.Lock()
        
    def increment(self):
        with self.lock:
            self.count += 1
            
    def get_count(self):
        return self.count

# Test for race conditions
counter = SharedResourceCounter()

def worker():
    for _ in range(100):
        counter.increment()

threads = [threading.Thread(target=worker) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(f"Final count: {counter.get_count()}")  # Should be 1000
```

### Monitoring Connection Usage

```python
import boto3
from botocore.config import Config
import logging

# Enable HTTP connection logging
logger = logging.getLogger('urllib3.connectionpool')
logger.setLevel(logging.DEBUG)

config = Config(max_pool_size=10)
s3 = boto3.client('s3', config=config)

# Monitor connection reuse
for i in range(20):
    response = s3.list_buckets()
    print(f"Request {i+1}: {len(response.get('Buckets', []))} buckets")
```
