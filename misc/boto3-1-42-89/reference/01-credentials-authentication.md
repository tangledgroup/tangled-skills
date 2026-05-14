# Credentials and Authentication

## Credential Chain

Boto3 searches for credentials in a specific order, stopping at the first successful source:

1. **Parameters** — passing credentials directly when creating a client or session
2. **Environment variables** — `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`
3. **Assume role provider** — role configuration in AWS config file
4. **Assume role with web identity provider** — OIDC/federation tokens
5. **AWS IAM Identity Center (SSO) credential provider** — SSO session profiles
6. **Shared credentials file** — `~/.aws/credentials`
7. **Login with console credentials** — AWS Management Console sign-in via AWS CLI
8. **AWS config file** — `~/.aws/config`
9. **Boto2 config file** — `~/.boto` (legacy backward compatibility)
10. **Container credential provider** — ECS/EKS container metadata
11. **Instance metadata service** — EC2 instance profile IAM role

## Passing Credentials Directly

Provide credentials as parameters when creating a client:

```python
import boto3

client = boto3.client(
    's3',
    aws_access_key_id='AKIAIOSFODNN7EXAMPLE',
    aws_secret_access_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
    region_name='us-east-1'
)
```

Or when creating a session:

```python
session = boto3.Session(
    aws_access_key_id='AKIAIOSFODNN7EXAMPLE',
    aws_secret_access_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
    region_name='us-east-1'
)
client = session.client('s3')
```

Use cases for direct credentials: retrieving temporary credentials via AWS STS, loading from external sources like OS keychain, or testing with specific credential sets.

## Environment Variables

Boto3 checks these environment variables:

- `AWS_ACCESS_KEY_ID` — access key for your AWS account
- `AWS_SECRET_ACCESS_KEY` — secret key for your AWS account
- `AWS_SESSION_TOKEN` — session token (temporary credentials only)
- `AWS_DEFAULT_REGION` — default region, e.g., `us-east-1`
- `AWS_PROFILE` — default profile name
- `AWS_CONFIG_FILE` — custom config file location (default: `~/.aws/config`)
- `AWS_SHARED_CREDENTIALS_FILE` — custom credentials file location (default: `~/.aws/credentials`)
- `AWS_CA_BUNDLE` — path to custom certificate bundle
- `AWS_EC2_METADATA_DISABLED` — disable EC2 instance metadata service
- `AWS_STS_REGIONAL_ENDPOINTS` — STS endpoint resolution logic
- `AWS_MAX_ATTEMPTS` — total retry attempts per request
- `AWS_RETRY_MODE` — retry mode (`legacy`, `standard`, `adaptive`)
- `AWS_APP_ID` — optional application identifier
- `AWS_SIGV4A_SIGNING_REGION_SET` — comma-delimited regions for SigV4a signing

## Shared Credentials File

Located at `~/.aws/credentials` by default. INI-formatted with profile sections:

```ini
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

[production]
aws_access_key_id = AKIAIOSFODNN7PRODUCTION
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYPRODUCTIONKEY
region = us-west-2
```

Specify a profile via the `AWS_PROFILE` environment variable or when creating a session:

```python
session = boto3.Session(profile_name='production')
client = session.client('ec2')
```

## AWS Config File

Located at `~/.aws/config` by default. Section names must start with `profile` (except `[default]`):

```ini
[default]
region = us-east-1
output = json

[profile production]
region = us-west-2
role_arn = arn:aws:iam::123456789012:role/ProductionRole
source_profile = default
mfa_serial = arn:aws:iam::123456789012:mfa/user-name
```

Configuration values in the AWS config file can be individually overwritten by environment variables or `Config` objects.

## Assume Role Configuration

Configure IAM role assumption in the AWS config file:

```ini
[profile admin]
role_arn = arn:aws:iam::123456789012:role/AdminRole
source_profile = default
mfa_serial = arn:aws:iam::123456789012:mfa/user-name
duration_seconds = 3600
external_id = my-external-id
```

Available assume role configuration values:

- `role_arn` — ARN of the role to assume (required)
- `source_profile` — profile containing source credentials
- `mfa_serial` — ARN of MFA device
- `duration_seconds` — session duration (900–43200 seconds)
- `external_id` — external ID for cross-account roles
- `role_session_name` — unique identifier for the role session
- `credential_save_duration` — how long to cache temporary credentials

Boto3 calls `sts:AssumeRole` automatically when using a profile with role configuration. Temporary credentials are not written to disk.

## Assume Role with Web Identity

For OIDC/federation authentication (EKS pods, GitHub Actions, etc.):

```ini
[profile github-actions]
role_arn = arn:aws:iam::123456789012:role/GitHubActionsRole
web_identity_token_file = /token/file/path
```

Or via environment variables:

- `AWS_WEB_IDENTITY_TOKEN_FILE` — path to the OIDC token file
- `AWS_ROLE_ARN` — ARN of the role to assume
- `AWS_ROLE_SESSION_NAME` — session name for the assumed role

## AWS IAM Identity Center (SSO)

Configure SSO profiles using AWS CLI v2:

```bash
aws sso login --sso-start-url https://myorg.awsapps.com/start
```

Then in `~/.aws/config`:

```ini
[profile sso-admin]
sso_start_url = https://myorg.awsapps.com/start
sso_region = us-east-1
sso_account_id = 123456789012
sso_role_name = AdministratorAccess
```

Use the profile in Boto3:

```python
session = boto3.Session(profile_name='sso-admin')
client = session.client('ec2')
```

Requires AWS CLI v2.32.0+ and Boto3 1.41.0+ with CRT enabled.

## Console Login Credentials

Use AWS Management Console sign-in credentials programmatically:

```bash
aws configure login
```

This creates a profile in `~/.aws/config` that Boto3 uses automatically when specified:

```python
session = boto3.Session(profile_name='my-login-profile')
client = session.client('s3')
```

Boto3 automatically refreshes cached credentials as needed. Requires AWS CLI v2.32.0+ and Boto3 with CRT dependency.

## Container Credentials

For ECS or EKS containers, set the `AWS_CONTAINER_CREDENTIALS_FULL_URI` environment variable to an HTTP endpoint. The SDK requests credentials from that endpoint automatically.

## EC2 Instance Metadata

When running on EC2, credentials are retrieved from the instance metadata service. Configure via AWS config file:

```ini
[profile ec2-profile]
credential_source = Ec2InstanceMetadata
```

Supported `credential_source` values: `Ec2InstanceMetadata`, `EcsContainer`, `Environment`.

Additional IMDS configuration options:

- `metadata_service_timeout` — timeout in seconds for IMDS requests
- `metadata_service_num_attempts` — retry attempts for IMDS
- `imds_use_ipv6` — use IPv6 endpoint for IMDS
