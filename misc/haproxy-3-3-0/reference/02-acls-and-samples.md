# ACLs and Sample Fetching

## ACL Basics

ACLs (Access Control Lists) define named conditions that match sampled data against patterns. They are the foundation of content-based routing and traffic control in HAProxy.

### Defining ACLs

```
acl <name> [<fetch>] [-m <method>] [flags] <pattern>...
```

- `<name>` — arbitrary identifier for the ACL
- `<fetch>` — sample fetch function (optional, defaults to `url` in HTTP mode)
- `-m <method>` — matching method
- `<pattern>` — one or more patterns to match

### Matching Methods

**Booleans:**
- `-m bool` — matches true values (non-zero integers)

**Integers:**
- `-m int` — exact integer match
- `-m range <lo>-<hi>` — inclusive range
- `-m gt <n>` / `-m lt <n>` / `-m ge <n>` / `-m le <n>` — comparison

**Strings:**
- `-m str` — full string equality
- `-m sub` — substring match
- `-m len` — exact length match
- `-m found` — non-empty string
- `-m end <suffix>` — ends with
- `-m dir <dir>` — starts with directory prefix
- `-m dom <domain>` — domain match (for host headers)

**Regular Expressions:**
- `-m reg "<regex>"` — PCRE regex match
- `-m len_reg "<regex>"` — match if length matches regex

**IP Addresses:**
- `-m ip <network>/<prefix>` — IP in network
- `-m src` — source address (alias for `src -m ip`)
- `-m dst` — destination address

### ACL Examples

```
# Match specific paths
acl is_api path_beg /api/
acl is_admin path_beg /admin/
acl is_static path_end .css .js .png .jpg .gif

# Match by source IP
acl internal_net src 10.0.0.0/8 172.16.0.0/12 192.168.0.0/16
acl blocked_ips src -f /etc/haproxy/blocked_ips.txt

# Match by header
acl is_mobile hdr_sub(User-Agent) -i mobile android iphone
acl has_api_key hdr_cnt(X-API-Key) gt 0

# Match by domain
acl example_com hdr(host) -i www.example.com example.com
```

### Using ACLs in Conditions

ACLs form conditions for rules. Multiple ACLs combine with boolean operators:

```
# Single condition
use_backend api if is_api

# Combined conditions
http-request deny if blocked_ips
use_backend admin if internal_net and is_admin
http-request redirect prefix https://%[hdr(host)]%[capture.req.uri] if !{ ssl_fc }

# Negation
default_backend web-servers if !is_static
```

Conditions support `and`, `or`, `!` (negation), and parentheses for grouping.

## Fetching Samples

Sample fetching extracts data from connections, requests, responses, or internal state. The syntax is `%[<fetch>[,<converter>]]`.

### Sample Types

- **SMP_T_BOOL** — boolean (true/false)
- **SMP_T_INT** — signed 32-bit integer
- **SMP_T_L4IP** — layer 4 IP address
- **SMP_T_L4STR** — layer 4 string
- **SMP_T_IPV4** — IPv4 address
- **SMP_T_IPV6** — IPv6 address
- **SMP_T_DIR** — directory path
- **SMP_T_STR** — string

### Internal State Fetches

Fetch data from HAProxy's internal state:

- `src` — client source IP address
- `dst` — client destination IP address
- `src_port` / `dst_port` — client source/destination port
- `pid` — process ID
- `uid` — stream unique ID
- `fconn` — frontend connection count
- `sconn` — server connection count
- `sc0(<backend>)` — sticky counter 0 for a backend
- `var(<scope>.<name>)` — variable value

### Layer 4 Fetches

Available after connection acceptance:

- `src` / `dst` — source/destination addresses
- `src_port` / `dst_port` — source/destination ports
- `conn_rate` / `sess_rate` — connection/session rates
- `fe_name` / `be_name` / `srv_name` — frontend/backend/server names

### Layer 5 (SSL/TLS) Fetches

Available when SSL is terminated on the frontend:

- `ssl_fc` — SSL frontend connection status (1 if present)
- `ssl_fc_protocol` — negotiated TLS version string
- `ssl_fc_cipher` — negotiated cipher name
- `ssl_fc_ecurve` — elliptic curve used
- `ssl_fc_sni` — Server Name Indication value
- `ssl_c_verify_i` — client certificate verification result (0 = success)
- `ssl_c_serial` — client certificate serial number
- `ssl_c_subject` / `ssl_c_issuer` — client cert DN
- `ssl_c_not_after` — client cert expiration date
- `ssl_fc_has_ech` — whether ECH was used
- `ssl_fc_key_exchange` — key exchange algorithm
- `ssl_fc_sig_scheme` — signature scheme

### Layer 6 (Buffer/Content) Fetches

Inspect raw buffer contents:

- `len` — buffer length
- `meth` — HTTP method
- `ver` — HTTP version
- `path` — URL path
- `query` — query string
- `url` — full URL (path + query)
- `host` — Host header value
- `cookie(<name>)` — specific cookie value
- `hdr(<name>)` — specific HTTP header value
- `hdr_val(<name>)` — header value
- `hdr_len(<name>)` — header value length
- `hdr_cnt(<name>)` — number of occurrences of header

### Layer 7 (HTTP) Fetches

HTTP-specific fetches:

- `method` — HTTP method (GET, POST, etc.)
- `status` — response status code
- `capture.req.hdr(<n>)` — captured request header n
- `capture.res.hdr(<n>)` — captured response header n
- `capture.var(<name>)` — captured variable value
- `url_param(<name>)` — specific URL parameter value

### Fetches for Stick-Table Data

- `sc_http_req_rate(0)` — HTTP request rate from stick counter 0
- `sc0_http_req_rate` — shorthand
- `sc_geoip0(0)` — GeoIP country from stick counter 0

## Converters

Converters transform sample values. Applied with comma after fetch: `%[fetch,converter1,converter2]`.

### String Converters

- `lower` / `upper` — case conversion
- `substr(<start>[,<len>])` — extract substring
- `regsub(<regex>,<replacement>,<flags>)` — regex substitution
- `int(<base>)` — convert to integer
- `sha1` / `md5` / `crc32` — hash the value
- `url_decode` / `url_encode` — URL encoding/decoding
- `unescape` — decode percent-encoded strings
- `json_escape` — escape for JSON embedding
- `trim` — remove leading/trailing whitespace
- `replaceall(<search>,<replace>)` — global string replacement

### Numeric Converters

- `abs` — absolute value
- `itoa` — integer to ASCII
- `atoi` — ASCII to integer
- `mathexpr(<expression>)` — mathematical expression evaluation
- `log2` — base-2 logarithm
- `rand([<min>,]<max>)` — random number in range

### IP Address Converters

- `ipaddrlen` — CIDR length of IP address
- `ipaddr_nbits(<n>)` — extract n bits from IP
- `netmask(<prefix>)` — apply network mask
- `src_to_ip` / `dst_to_ip` — convert source/dest to IP type

### Combining Fetches and Converters

```
# Extract domain from Host header, lowercase
%[hdr(host),lower,map_dom(/etc/haproxy/domain-map)]

# Hash the source IP for consistent routing
%[src,int,sha1]

# Get first path segment
%[path,regsub(^/([^/]+).*),\1)]

# Check if status is a 5xx error
%[status,int,lt(600),and,status,int,ge(500)]
```

## Variables

Variables store sample values for later use. Scopes determine lifetime:

- **proc.** — process-wide, persists for HAProxy lifetime
- **sess.** — session-wide (all streams in a connection)
- **txn.** — transaction-wide (single HTTP request/response pair)
- **req.** — request processing only
- **res.** — response processing only
- **check** — health check execution only

### Setting Variables

```
# In configuration
http-request set-var(txn.path) path
http-request set-var(txn.client_ip) src
http-response set-var(res.status) status

# From CLI
set var proc.maintenance int(0)
```

### Using Variables in Conditions

```
acl maintenance_mode var(proc.maintenance) -m int gt 0
http-request deny if maintenance_mode

# Track request count per session
http-request set-var(sess.req_count) str_inc(var(sess.req_count),1)
acl too_many_requests var(sess.req_count,int) gt 100
```

## Maps

Maps transform input values to output values using pattern matching. Loaded from files or defined inline.

### Map File Format

```
# /etc/haproxy/domain-map
www.example.com    example
api.example.com    api
*.example.org      org
*                  default
```

### Using Maps in Fetches

```
%[hdr(host),map(/etc/haproxy/domain-map)]
%[src,map_ip(/etc/haproxy/geoip-map)]
%[path,map_reg(/etc/haproxy/path-map)]
```

Map matching methods:
- `map` — string equality (default)
- `map_int` — integer match
- `map_ip` — IP network match
- `map_reg` — regex match
- `map_str` — string match
- `map_sub` — substring match
- `map_end` — suffix match
- `map_dom` — domain match

## Stick-Tables

Stick-tables store per-key data for rate limiting, DDoS protection, and persistence.

### Defining a Stick-Table

```
stick-table type ip size 200k expire 5m store http_req_rate(10s),http_err_rate(10s),conn_cur,bytes_in
```

- `type { ip | integer | string(<len>) | binary(<len>) }` — key type
- `size <entries>` — maximum entries (suffix k/m for thousands/millions)
- `expire <time>` — entry expiration time
- `store <data-types>` — data tracked per entry

### Data Types

- `http_req_rate(<interval>)` — HTTP request rate over interval
- `http_err_rate(<interval>)` — HTTP error rate over interval
- `conn_cur` — current connection count
- `conn_rate(<interval>)` — connection rate over interval
- `bytes_in` / `bytes_out` — bytes transferred
- `gpc0` — general purpose counter 0
- `gpt0` — general purpose table 0 (array of strings)

### Using Stick-Tables for Rate Limiting

```
frontend http-in
    bind *:80

    # Define the stick-table
    stick-table type ip size 100k expire 30s store http_req_rate(10s)

    # Track each source IP
    http-request track-sc0 src

    # Deny if rate exceeds 100 requests per 10 seconds
    http-request deny deny_status 429 if { sc_http_req_rate(0) gt 100 }

    default_backend web-servers
```

### Using Stick-Tables for DDoS Protection

```
frontend http-in
    bind *:80

    stick-table type ip size 500k expire 1m \
        store http_req_rate(10s),conn_cur,http_err_rate(10s)

    http-request track-sc0 src

    # Block IPs with too many connections
    tcp-request connection reject if { SC0_CONN_CUR gt 50 }

    # Block IPs with high error rates
    http-request deny if { sc_http_err_rate(0) gt 50 }

    # Temporary block for abuse
    http-request tarpit if { sc_http_req_rate(0) gt 200 }
```

### Pre-defined ACLs

HAProxy provides built-in ACLs:
- `L7OK` — HTTP request/response successfully processed
- `L7fe` — frontend has seen a complete HTTP request
- `L7srtt` — server round-trip time exceeded timeout
- `L4src` / `L4dst` — source/destination addresses available
- `ON_ERROR` — connection ended with an error
