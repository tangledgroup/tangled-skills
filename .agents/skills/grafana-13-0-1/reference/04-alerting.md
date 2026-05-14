# Alerting

## Contents
- How Alerting Works
- Alert Rules
- Contact Points and Notification Policies
- Alert States
- External Integrations
- Performance Considerations

## How Alerting Works

Grafana Alerting is built on the Prometheus alerting model. It periodically evaluates alert rules by executing data source queries and checking conditions against results.

Flow:
1. **Alert rule** defines a query and condition
2. Grafana executes the query on a scheduled interval
3. Each result produces an **alert instance** (one per time series or dimension)
4. If the condition is breached, the instance enters **firing** state
5. Firing instances are routed through **notification policies** to **contact points**

## Alert Rules

An alert rule consists of:
- **Name** — unique identifier within the folder/namespace
- **Data source** — where to query data
- **Query** — the actual query (PromQL, LogQL, SQL, etc.)
- **Condition** — expression evaluated against query results (e.g., `A > threshold`)
- **Evaluation interval** — how often the rule is checked
- **For duration** — how long the condition must be true before firing
- **Labels** — key-value pairs for grouping and routing
- **Annotations** — metadata included in notifications (summary, description)

### Creating an Alert Rule

1. Navigate to **Alerting > Alert rules**
2. Click **New alert rule**
3. Select a data source and write a query
4. Define the condition (e.g., `A is above 80`)
5. Set evaluation interval and "for" duration
6. Add labels and annotations
7. Save to a folder

### Example: High CPU Alert

```
Query: 100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
Condition: A > 80
For: 5m
Labels: severity=critical, team=infrastructure
Annotations:
  summary: "High CPU on {{ $labels.instance }}"
  description: "CPU usage is above 80% for more than 5 minutes."
```

### Multi-Query Alert Rules

Combine queries from multiple data sources using expressions. This enables correlating metrics with logs or traces in a single alert condition.

## Contact Points and Notification Policies

### Contact Points

A contact point defines where notifications are sent:

| Type | Description |
|------|-------------|
| Email | Send to email addresses |
| Slack | Post to Slack channels via webhook |
| PagerDuty | Trigger PagerDuty incidents |
| Opsgenie | Route to Opsgenie |
| Webhook | POST JSON to any HTTP endpoint |
| Discord | Send to Discord channels |
| Teams | Send to Microsoft Teams |
| VictorOps | Route to Splunk On-Call |

Configure contact points under **Alerting > Contact points**. Each contact point has a unique name used by notification policies.

### Notification Policies

Notification policies define how alert instances are routed, grouped, and throttled:

- **Root policy** — default route for all alerts
- **Child policies** — match on labels to route specific alerts
- **Grouping** — combine related alerts into single notifications
- **Interval** — minimum time between notification repeats
- **Wait period** — delay before sending first notification
- **Repeat interval** — how often to re-send for persistent alerts

Example policy tree:
```
Root (default: email-team)
├── match: severity=critical → pagerduty-oncall (interval: 1m)
├── match: team=backend → slack-backend (group_by: alertname, interval: 5m)
└── match: environment=production → webhook-ops (interval: 2m)
```

## Alert States

| State | Description |
|-------|-------------|
| Normal | Condition is not met, no alert |
| Pending | Condition has been met but "for" duration not yet elapsed |
| Firing | Condition has been met for the required duration |

State transitions: `Normal → Pending → Firing → Normal` (when condition clears).

## External Integrations

Grafana Alerting integrates with:

- **Prometheus Alertmanager** — send alerts to external Alertmanager for unified routing
- **AMT (Alertmanager Transfer)** — sync Grafana alert rules to Prometheus Alertmanager
- **Webhook receivers** — custom HTTP endpoints for any integration
- **Grafana OnCall** — incident management and on-call scheduling
- **Grafana Synthetic Monitoring** — correlate uptime checks with alerts

### Sending to Prometheus Alertmanager

Configure in `grafana.ini`:

```ini
[alerting.alertmanager]
enabled = true
[alerting.alertmanager.0]
name = prod-alertmanager
url = http://alertmanager:9093
```

## Performance Considerations

In Grafana OSS, the alert engine runs in the same process as the UI and data source proxy. Key considerations:

- **High rule counts with short evaluation intervals** can saturate CPU independently of user activity
- Alert CPU saturation directly competes with dashboard query performance
- At large scale, isolate alert evaluation to dedicated instances
- Use appropriate "for" durations to reduce unnecessary state transitions
- Group related alerts in notification policies to reduce notification volume

Refer to [Performance considerations and limitations](https://grafana.com/docs/grafana/latest/alerting/set-up/performance-limitations/) for detailed guidance.
