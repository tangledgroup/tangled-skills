# Configuration and Credentials

## Credential Provider Chain

Boto3 searches for credentials in a specific order, stopping at the first source that provides valid credentials:

1. **Client/Session parameters**: Explicit credentials passed to `boto3.client()` or `Session()`
2. **Environment variables**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`
3. **Assume role provider**: Role configuration in `~/.aws/config`
4. **Web identity provider**: OIDC token-based role assumption
5. **IAM Identity Center (SSO)**: Single sign-on credentials
6. **Shared credentials file**: `~/.aws/credentials`
7. **Login with console credentials**: Browser-based authentication (requires CRT)
8. **AWS config file**: `~/.aws/config`
9. **Boto2 config file**: `/etc/boto.cfg` or `~/.boto`
10. **Container credential provider**: ECS/EKS task roles
11. **Instance metadata service**: EC2 IAM roles

## Environment Variables

```bash
# Core credentials
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_SESSION_TOKEN=your_session_token  # For temporary credentials

# Configuration
export AWS_DEFAULT_REGION=us-east-1
export AWS_PROFILE=production
export AWS_CONFIG_FILE=~/.aws/config
export AWS_SHARED_CREDENTIALS_FILE=~/.aws/credentials

# SSL/TLS
export AWS_CA_BUNDLE=/path/to/certificates.pem

# Metadata service (for EC2)
export AWS_METADATA_SERVICE_TIMEOUT=10
export AWS_METADATA_SERVICE_NUM_ATTEMPTS=5

# Retry configuration
export AWS_MAX_ATTEMPTS=10
export AWS_RETRY_MODE=standard

# STS regional endpoints
export AWS_STS_REGIONAL_ENDPOINTS=regional

# Request/response checksums
export AWS_REQUEST_CHECKSUM_CALCULATION=when-required
export AWS_RESPONSE_CHECKSUM_VALIDATION=when-required
```

## Shared Credentials File (`~/.aws/credentials`)

```ini
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

[production]
aws_access_key_id = AKIAIOSFODNN7PRODUC
aws_secret_access_key = production_secret_key_here

[development]
aws_access_key_id = AKIAIOSFODNN7DEVLOP
aws_secret_access_key = development_secret_key_here

# Temporary credentials (auto-refresh by Boto3)
[temporary]
aws_access_key_id = tmpACCESSKEY1234567890
aws_secret_access_key = tmpsecretkeyhere
aws_session_token = tmpsessiontoken1234567890abcdef
```

## AWS Config File (`~/.aws/config`)

```ini
[default]
region = us-east-1
output = json
cli_pager = less -R
profile = default

# API version overrides
api_versions =
    ec2 = 2016-11-15
    cloudfront = 2017-10-30

# Retry configuration
max_attempts = 10
retry_mode = standard

# S3-specific settings
s3 =
    addressing_style = path
    payload_signing_enabled = true
    signature_version = s3v4

# Proxy configuration
proxy_host = proxy.example.com
proxy_port = 8080

[profile production]
region = us-west-2
output = json

[profile "cross account role"]
role_arn = arn:aws:iam::123456789012:role/CrossAccountRole
source_profile = production
role_session_name = CrossAccountSession
duration_seconds = 3600

[profile mfa-role]
role_arn = arn:aws:iam::123456789012:role/MFARole
source_profile = default
mfa_serial = arn:aws:iam::123456789012:mfa/user-name
role_session_name = MFASession

[profile web-identity]
role_arn = arn:aws:iam::123456789012:role/WebIdentityRole
web_identity_token_file = /tmp/token
role_session_name = WebIdentitySession

[profile sso]
sso_start_url = https://my-company.awsapps.com/start
sso_region = us-east-1
sso_account_id = 123456789012
sso_role_name = AdministratorAccess

[profile ecs-container]
credential_source = EcsContainer

[profile ec2-instance]
credential_source = Ec2InstanceMetadata
```

## IAM Roles for EC2 Instances

When running on EC2, Boto3 automatically retrieves credentials from the instance metadata service if no other credentials are found:

```python
import boto3

# No configuration needed - uses EC2 instance role automatically
s3 = boto3.client('s3')
ec2 = boto3.client('ec2')
```

**Configure IAM role when launching EC2:**
1. Create IAM role with required permissions
2. Attach role to EC2 instance during launch or afterward
3. Boto3 automatically discovers and uses the role

## Assume Role Configuration

### Basic Assume Role

```ini
# ~/.aws/credentials
[base]
aws_access_key_id = BASE_ACCESS_KEY
aws_secret_access_key = BASE_SECRET_KEY

# ~/.aws/config
[profile assumed-role]
role_arn = arn:aws:iam::123456789012:role/AssumedRole
source_profile = base
```

```python
import boto3

# Use the assumed role profile
session = boto3.Session(profile_name='assumed-role')
s3 = session.client('s3')
```

### Assume Role with MFA

```ini
[profile mfa-assumed-role]
role_arn = arn:aws:iam::123456789012:role/MFARole
source_profile = base
mfa_serial = arn:aws:iam::123456789012:mfa/admin-user
```

When using MFA, Boto3 will prompt for the MFA token:
```python
import boto3

session = boto3.Session(profile_name='mfa-assumed-role')
# First API call will prompt for MFA token
s3 = session.client('s3')
```

### Assume Role with Web Identity (OIDC)

```ini
[profile web-identity]
role_arn = arn:aws:iam::123456789012:role/WebIdentityRole
web_identity_token_file = /path/to/token
role_session_name = my-session-name
```

Or using environment variables:
```bash
export AWS_ROLE_ARN=arn:aws:iam::123456789012:role/WebIdentityRole
export AWS_WEB_IDENTITY_TOKEN_FILE=/path/to/token
export AWS_ROLE_SESSION_NAME=my-session-name
```

## IAM Identity Center (SSO)

### Configuration via AWS CLI v2

```bash
# Configure SSO profile
aws sso login --profile my-sso-profile
# Follow browser prompts to authenticate

# Profile is automatically added to ~/.aws/config
```

### Resulting Configuration

```ini
[profile my-sso-profile]
sso_start_url = https://my-company.awsapps.com/start
sso_region = us-east-1
sso_account_id = 123456789012
sso_role_name = AdministratorAccess
region = us-west-2
```

### Usage in Boto3

```python
import boto3

session = boto3.Session(profile_name='my-sso-profile')
s3 = session.client('s3')
# Credentials automatically refreshed as needed
```

## Login with Console Credentials (Requires CRT)

Install Boto3 with AWS Common Runtime:
```bash
pip install boto3[crt]
```

Authenticate using AWS CLI:
```bash
aws login --profile my-login-profile
# Browser opens for authentication
```

Resulting configuration:
```ini
[profile my-login-profile]
login_session = arn:aws:iam::123456789012:user/username
region = us-east-1
```

Use in Boto3:
```python
import boto3

session = boto3.Session(profile_name='my-login-profile')
s3 = session.client('s3')
# Sessions valid for up to 12 hours
```

## Programmatic Configuration

### Config Object

```python
from botocore.config import Config

config = Config(
    # Region
    region_name='us-west-2',
    
    # Signature version
    signature_version='v4',
    
    # Retry configuration
    retries={
        'mode': 'standard',
        'total_max_attempts': 10
    },
    
    # Proxy settings
    proxies={
        'http': 'http://proxy.example.com:8080',
        'https': 'https://proxy.example.com:8080'
    },
    
    # S3-specific settings
    s3={
        'addressing_style': 'path',
        'payload_signing_enabled': True
    },
    
    # TCP keepalive
    tcp_keepalive=True,
    
    # Connect timeout
    connect_timeout=10,
    
    # Read timeout
    reads_timeout=60
)

s3 = boto3.client('s3', config=config)
```

### Session Configuration

```python
import boto3

session = boto3.Session(
    aws_access_key_id='ACCESS_KEY',
    aws_secret_access_key='SECRET_KEY',
    aws_session_token='SESSION_TOKEN',  # Optional, for temporary credentials
    region_name='us-east-1',
    profile_name='my-profile'  # Alternative to explicit credentials
)

s3 = session.client('s3')
```

### Client-Specific Configuration

```python
import boto3

# Override region for specific client
s3 = boto3.client('s3', region_name='us-west-2')
ec2 = boto3.client('ec2', region_name='eu-west-1')

# Use custom endpoint (for testing or custom services)
dynamodb = boto3.client(
    'dynamodb',
    endpoint_url='http://localhost:8000',
    region_name='us-east-1'
)

# Specify API version
client = boto3.client('ec2', api_version='2016-11-15')
```

## Container Credentials (ECS/EKS)

### ECS Task Role

```ini
[profile ecs]
credential_source = EcsContainer
```

Or set environment variable:
```bash
export AWS_CONTAINER_CREDENTIALS_RELATIVE_URI=/relative/uri
```

### EKS IRSA (IAM Roles for Service Accounts)

Configure Kubernetes service account with IAM role, then use pod's metadata service:
```python
import boto3

# Automatically uses EKS pod identity
s3 = boto3.client('s3')
```

## Best Practices

1. **Never hardcode credentials** in source code or commit to version control
2. **Use IAM roles** when running on AWS infrastructure (EC2, ECS, Lambda)
3. **Implement least privilege** - grant only necessary permissions
4. **Rotate credentials regularly** if using long-term access keys
5. **Use temporary credentials** when possible (STS, assume role)
6. **Set appropriate file permissions** on credential files (600 for credentials, 600 for config)
7. **Use environment variables** for CI/CD pipelines
8. **Enable MFA** for privileged accounts and assume role scenarios

## Troubleshooting Credentials

### Debug Credential Resolution

```python
import boto3
from botocore.session import Session

session = Session()
creds = session.get_credentials()

if creds:
    print(f"Access Key ID: {creds.access_key}")
    print(f"Secret Access Key: {creds.secret_key}")
    print(f"Token: {creds.token}")
else:
    print("No credentials found")
```

### Check Credential Source

```python
import boto3

session = boto3.Session()
loader = session.get_component('credential_provider')

# Iterate through providers
for provider_name in loader._providers:
    print(f"Checking: {provider_name}")
```

### Common Credential Errors

**NoCredentialsError**: No valid credentials found
```python
import botocore.exceptions

try:
    s3 = boto3.client('s3')
    s3.list_buckets()
except botocore.exceptions.NoCredentialsError:
    print("Configure credentials using aws configure or environment variables")
```

**PartialCredentialsError**: Only access key or secret key provided
```python
try:
    s3 = boto3.client('s3')
except botocore.exceptions.PartialCredentialsError:
    print("Both AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be set")
```

**CredentialRetrievalError**: Failed to retrieve credentials from a provider
```python
try:
    s3 = boto3.client('s3')
except botocore.exceptions.CredentialRetrievalError as e:
    print(f"Failed to retrieve credentials: {e}")
```
