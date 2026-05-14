# Administration

## Contents
- Users and Organizations
- Roles and Permissions
- Service Accounts
- Provisioning System
- Git Sync (GA in v13)
- Plugin Management
- Grafana Server CLI

## Users and Organizations

Grafana supports multiple organizations per instance. Each organization has its own users, dashboards, data sources, and alert rules.

### User Types

| Type | Description |
|------|-------------|
| Regular user | Standard account with assigned roles |
| Administrator | Full access to all organizations and settings |
| API user (service account) | Machine-to-machine access with tokens |

### Managing Users

Administrators manage users under **Administration > Users**:
- View all users, their organizations, and roles
- Disable or delete users
- Change passwords (for internal auth)
- Assign to organizations

### Organization Management

Under **Administration > Organizations**:
- Create new organizations
- Manage organization preferences (default home dashboard, theme, time zone)
- Add/remove users from organizations
- Set organization-level alert notification settings

## Roles and Permissions

Grafana uses a role-based access control system with built-in and custom roles.

### Built-in Organization Roles

| Role | Permissions |
|------|-------------|
| Viewer | Read-only: view dashboards, explore data, view alert rules |
| Editor | Viewer + create/edit dashboards, manage data sources, create alert rules |
| Admin | Editor + manage users, organization settings, plugins, provisioning |

### Built-in Global Roles

- **Instance Admin** — full access to all organizations
- **Limited Admin** — admin access to assigned organizations only

### Custom Roles (Enterprise)

Grafana Enterprise supports custom roles with fine-grained permissions. Define roles via the UI or provisioning YAML with specific permission sets for dashboards, data sources, folders, and alerting.

### Permission Scopes

Permissions can be scoped to:
- **Organization** — all resources in an org
- **Folder** — specific dashboard folder
- **Data source** — specific data source instance
- **Dashboard** — individual dashboard

## Service Accounts

Service accounts provide API access for automation without human user accounts.

### Creating a Service Account

1. Navigate to **Administration > Service accounts**
2. Click **New service account**
3. Set name and role (Viewer, Editor, Admin)
4. Click **Save**
5. Generate an API key (choose expiration: 1h, 1d, 1w, 30d, 90d, or No expiry)

### Using Service Account Tokens

```bash
# Authenticate with API token
curl -H "Authorization: Bearer glsa_<token>" \
  http://localhost:3000/api/org/users
```

### Provisioning Service Accounts

Define service accounts in provisioning YAML:

```yaml
apiVersion: 1
serviceAccounts:
  - name: ci-pipeline
    login: ci-pipeline
    orgId: 1
    role: Viewer
    tokens:
      - name: ci-token
        key: "glsa_pre-generated-key-here"
```

## Provisioning System

Grafana's provisioning system manages data sources, dashboards, and plugins via YAML configuration files. This enables version-controlled, repeatable deployments.

### Directory Structure

```
/etc/grafana/provisioning/
├── datasources/
│   └── prometheus.yaml
├── dashboards/
│   └── default.yaml
└── plugins/
    └── plugins.yaml
```

### Dashboard Provisioning

Create a provider config in `/etc/grafana/provisioning/dashboards/default.yaml`:

```yaml
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 30
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
      foldersFromFilesStructure: true
```

Place JSON dashboard files in `/var/lib/grafana/dashboards/`. Grafana loads and syncs them automatically.

### Plugin Provisioning

Pre-install plugins via `/etc/grafana/provisioning/plugins/plugins.yaml`:

```yaml
apiVersion: 1

apps:
  - type: grafana-clock-panel
    enabled: true
  - type: grafana-piechart-panel
    enabled: true
```

## Git Sync (GA in v13)

Git Sync reached general availability in Grafana 13.0, enabling bidirectional GitOps for dashboards and folders.

### How It Works

- Connect Grafana to a git repository (GitHub, GitLab, Bitbucket, or any git remote)
- Edit dashboards directly in the Grafana UI
- Save changes as commits with pull request support
- Pull changes from git into Grafana automatically
- Conflict detection and resolution for concurrent edits

### Setup

1. Navigate to **Administration > Git Sync**
2. Configure the git provider (URL, authentication method)
3. Select which folders to sync
4. Choose sync direction: push-only, pull-only, or bidirectional

### Benefits

- **Audit trail** — all dashboard changes tracked in git history
- **Rollback** — revert to previous versions via git
- **Code review** — use pull requests for dashboard changes
- **Environment parity** — same dashboards across dev/staging/prod

## Plugin Management

### Installing Plugins

```bash
# Via grafana-cli
sudo grafana-cli plugins install <plugin-id>
sudo systemctl restart grafana-server
```

### Updating Plugins

```bash
sudo grafana-cli plugins update <plugin-id>
# Or update all
sudo grafana-cli plugins update-all
```

### Plugin Configuration

Configure installed plugins under **Connections > Plugins**. Each plugin may have its own settings page for API keys, endpoints, and feature toggles.

### Plugin Allow Lists

Restrict which plugins can be installed via `grafana.ini`:

```ini
[plugins]
allow_loading_unsigned_plugins = plugin-id-1,plugin-id-2
```

## Grafana Server CLI

The `grafana-cli` tool manages plugins and administration tasks:

```bash
# Plugin management
grafana-cli plugins install <plugin-id>
grafana-cli plugins update <plugin-id>
grafana-cli plugins list

# Admin commands
grafana-cli admin reset-admin-password <new-password>
grafana-cli admin users list
```

The `grafana-server` binary runs the Grafana application:

```bash
grafana-server help
# Options: --config, --homepath, web, plugins, db, certs, generate
```
