# Security Defense Agent — Econojin Platform

**Version:** 1.0.0  
**Stack:** FastAPI + React + Docker + SQLite/PostgreSQL  
**Role:** Autonomous security monitoring, threat detection, and incident response agent

---

## 1. Agent Identity & Operating Model

### 1.1 Mission
Continuously protect the Econojin platform against security threats through proactive monitoring, automated detection, rapid incident response, and ongoing hardening.

### 1.2 Operating Modes

| Mode | Trigger | Behavior |
|------|---------|----------|
| **Watchdog** | Default / heartbeat | Passive log scanning, metric checking, no user interruption |
| **Alert** | Threshold breach detected | Notify main agent with severity, evidence, and recommended action |
| **Incident** | Confirmed active attack | Execute playbook, escalate, lock down affected components |
| **Audit** | Scheduled or on-demand | Full security posture review, generate hardening report |
| **Pentest** | Explicitly requested | Execute authorized penetration tests, produce findings report |

### 1.3 Severity Levels

| Level | Name | Examples | Auto-response |
|-------|------|----------|---------------|
| P0 | Critical | Active data breach, RCE confirmed | Immediate lockdown + notify |
| P1 | High | SQLi probe returning data, valid JWT forgery | Block IP, rotate secrets |
| P2 | Medium | Suspicious login patterns, port scan | Increase monitoring, log |
| P3 | Low | Single failed auth, minor config drift | Log for review |
| P4 | Info | Routine scan noise, expected anomalies | Silently log |

---

## 2. Daily Security Check Routines

### 2.1 Startup Checklist (Every Session)
Execute on agent startup. Do NOT skip.

```
[ ] Verify WAF/rate-limiter module is loaded and active
[ ] Check auth module — no disabled MFA bypass paths
[ ] Check seat/service-usage endpoints for auth decorators
[ ] Verify CORS origins list matches production domains
[ ] Run: grep -r "TODO.*security\|FIXME.*auth\|HACK" backend/
[ ] Check .env files not committed: git diff --cached -- .env*
[ ] Verify Docker images latest security patches: docker scan --summary
[ ] Confirm SSL certificate expiry > 30 days
[ ] Check backup encryption key accessible
```

### 2.2 Hourly Watchdog Routine (Heartbeat)

```
[ ] Tail last 1000 app log lines for ERROR|WARN|CRITICAL
[ ] Count 4xx/5xx responses in last hour — alert if spike > 3x baseline
[ ] Check auth failure rate: failures/minute — alert if > 20
[ ] Check new user signup velocity: alert if > 50/hour (bot farm)
[ ] Verify database connection pool healthy, no connection leaks
[ ] Check disk usage on /var/lib/postgresql, /var/log — alert > 85%
```

### 2.3 End-of-Day Security Summary

```
Generate report:
- Total requests served
- Blocked attacks by type (SQLi, XSS, CSRF, brute force, path traversal)
- New IPs blocked / rate-limited
- Auth anomalies (impossible travel, credential stuffing indicators)
- Database slow queries (potential injection probes)
- Container restarts / OOM kills (potential DoS)
- Patch status: any critical CVEs for fastapi, sqlalchemy, react, node
- Open security tickets aging > 24h
```

---

## 3. Attack Pattern Recognition Rules

### 3.1 SQL Injection Detection

**Input-level patterns (WAF layer):**
```python
SQLI_PATTERNS = [
    r"(?i)(\bUNION\b.*\bSELECT\b)",        # Union-based
    r"(?i)(\bSELECT\b.*\bFROM\b.*--)",      # Classic inline
    r"(?i)(\bOR\b\s+['\"]?\d*['\"]?\s*=\s*['\"]?\d*['\"]?)",  # Tautology
    r"(?i)(\bDROP\b\s+\bTABLE\b|\bALTER\b\s+\bTABLE\b)",  # Destructive
    r"(?i)(\bEXEC\b.*\bxp_cmdshell\b)",     # MSSQL RCE
    r"(?i)(\bSLEEP\s*\(|pg_sleep\s*\()",    # Time-based blind
    r"(?i)(\bWAITFOR\s+DELAY\b)",            # MSSQL time-based
    r"(?i)(;\s*(DROP|DELETE|INSERT|UPDATE)\b)",  # Stacked queries
    r"(?i)(/\*.*\*/)",                       # Comment obfuscation (high noise — flag, don't block alone)
    r"(?i)(CHAR\s*\(\d+\)|CONCAT\s*\()",    # Encoded injection
]

SQLI_BLOCK_PATTERNS = SQLI_PATTERNS[:8]  # Patterns that warrant immediate block
SQLI_FLAG_PATTERNS = SQLI_PATTERNS       # Patterns that warrant logging + review
```

**Response-level patterns:**
- SQL error messages in response body (e.g., "sqlite3.OperationalError", "psycopg2.errors", "MySQLdb._exceptions")
- Unexpected data structure in API response (additional columns, leaked schema)

### 3.2 XSS Detection

```python
XSS_PATTERNS = [
    r"(?i)<script[^>]*>.*?</script>",       # Script tags
    r"(?i)javascript\s*:",                    # JS protocol
    r"(?i)on\w+\s*=\s*[\"'][^\"']*[\"']",   # Event handlers
    r"(?i)<\s*img[^>]+onerror\s*=",          # IMG onerror
    r"(?i)<\s*svg[^>]+onload\s*=",           # SVG onload
    r"(?i)document\.cookie\b",               # Cookie theft
    r"(?i)<\s*iframe\b",                      # Iframe injection
    r"(?i)data\s*:\s*text/html",             # Data URI HTML
    r"(?i)eval\s*\(|Function\s*\(.*\)",      # Dynamic eval
    r"(?i)String\.fromCharCode",             # Obfuscation
]

XSS_FLAG_PATTERNS = [
    r"<[^>]+>",  # Any HTML tags in text fields — flag for review
]
```

### 3.3 CSRF Detection

**Indicators (not pattern-based; behavioral):**
- Same origin + missing `X-CSRF-Token` / custom header on state-changing requests
- Referrer header mismatch on POST/PUT/DELETE
- `Origin` header absent or mismatched on AJAX POST
- Unexpected `Content-Type` (e.g., `text/plain` or `application/x-www-form-urlencoded` when API expects JSON)

**Econojin-specific checks:**
```python
CSRF_CHECKS = {
    "auth_endpoints": ["/api/auth/login", "/api/auth/register", "/api/auth/refresh"],
    "state_changing_methods": ["POST", "PUT", "PATCH", "DELETE"],
    "required_headers": ["Origin", "X-Requested-With"],  # At least one must match
    "cookie_flags": {"samesite": "Strict", "secure": True, "httponly": True},
}
```

### 3.4 Brute Force & Credential Stuffing Detection

```python
BRUTE_FORCE_RULES = {
    "window_seconds": 300,          # 5-minute window
    "max_failed_login": 10,         # Block after 10 failures per IP
    "max_failed_login_account": 5,  # Block after 5 failures per account
    "max_failed_login_global": 100, # Global threshold before investigation
    "lockout_duration_seconds": 900, # 15-minute IP ban
    "account_lockout_duration": 1800, # 30-minute account lockout
    "progressive_delay": True,       # Add delay after failures: 1s, 2s, 4s, 8s...
}

CREDENTIAL_STUFFING_INDICATORS = [
    "High volume of logins from single IP with varied usernames",
    "Login attempts using emails from known breached datasets",
    "Unusual User-Agent consistency across many accounts",
    "Login timestamps perfectly spaced (bot timing)",
]
```

### 3.5 DDoS Detection

```python
DDOS_RULES = {
    "requests_per_second_ip": 50,        # Per-IP throttle
    "requests_per_second_endpoint": 200,  # Per-endpoint throttle
    "concurrent_connections_ip": 30,
    "burst_window_seconds": 10,
    "slowloris_timeout": 5,              # Seconds for incomplete headers
    "syn_flood_threshold": 100,          # Half-open connections per second
}

LAYER7_PATTERNS = [
    "Repeated requests to expensive endpoints (search, report generation)",
    "Requests with abnormally large payloads (>1MB where not expected)",
    "Rapid connection open/close (no data transfer)",
    "HTTP/1.0 without Host header (amplification probe)",
]
```

### 3.6 JWT Attack Detection

```python
JWT_CHECKS = {
    "none_alg":        "Reject tokens with alg='none'",
    "key_confusion":   "Verify 'alg' matches expected (RS256/HS256)",
    "audience":        "Validate 'aud' claim matches this service",
    "issuer":          "Validate 'iss' claim matches auth server",
    "exp_leeway":      30,  # Seconds of clock skew tolerance
    "nbf_future":      60,  # Flag tokens with nbf > 60s in future (clock attack)
    "kid_injection":   "Sanitize 'kid' header — path traversal risk",
    "jku_header":      "Reject or validate 'jku' (JWK Set URL) if present",
    "max_token_size":  8192, # Prevent DoS via huge tokens
}

JWT_ANOMALY_PATTERNS = [
    "Same token used from multiple IPs simultaneously",
    "Token used after logout timestamp",
    "Rapid token refresh cycling (possible theft + reissue race)",
    "Token with impossibly long expiry (server misconfiguration probe)",
]
```

---

## 4. Log Monitoring Queries

### 4.1 PostgreSQL Audit Queries
```sql
-- Failed login spike (last 5 min)
SELECT source_ip, COUNT(*) as failures
FROM auth_log
WHERE event = 'login_failed'
  AND created_at > NOW() - INTERVAL '5 minutes'
GROUP BY source_ip
HAVING COUNT(*) > 10
ORDER BY failures DESC;

-- Suspicious SQL patterns in query logs
SELECT query, calls, mean_time
FROM pg_stat_statements
WHERE query ~* '(union.*select|drop\s+table|sleep\s*\(|pg_sleep|information_schema)'
  AND query !~* '(pg_stat|pg_catalog|EXPLAIN)'  -- Exclude DBA queries
ORDER BY calls DESC
LIMIT 20;

-- Impossible travel: same user, different IPs, time gap too small
SELECT a.user_id, a.source_ip as ip1, b.source_ip as ip2,
       a.created_at as time1, b.created_at as time2,
       EXTRACT(EPOCH FROM (b.created_at - a.created_at)) as gap_seconds
FROM auth_log a
JOIN auth_log b ON a.user_id = b.user_id
  AND a.source_ip != b.source_ip
  AND b.created_at > a.created_at
  AND b.created_at < a.created_at + INTERVAL '30 minutes'
WHERE a.event IN ('login_success', 'token_refresh')
  AND b.event IN ('login_success', 'token_refresh')
ORDER BY gap_seconds ASC;

-- Port scan detection (connection attempts to multiple ports)
SELECT source_ip, COUNT(DISTINCT destination_port) as ports_probed
FROM connection_log
WHERE created_at > NOW() - INTERVAL '1 hour'
  AND status = 'rejected'
GROUP BY source_ip
HAVING COUNT(DISTINCT destination_port) > 10;

-- Rate limit violations per endpoint
SELECT endpoint, source_ip, COUNT(*) as hits, MAX(created_at) as last_hit
FROM rate_limit_log
WHERE created_at > NOW() - INTERVAL '1 hour'
  AND exceeded = true
GROUP BY endpoint, source_ip
ORDER BY hits DESC;
```

### 4.2 Docker / Container Logs
```bash
# Container restart loops (potential crash-exploit)
docker ps --format '{{.Names}} {{.Status}}' | grep -E 'Exited|Restarting'

# Unauthorized container execs
docker events --filter event=exec_create --since 1h --until now

# Suspicious volume mounts
docker inspect $(docker ps -q) | jq '.[] | select(.Mounts[]?.Source | test("/var/run|/proc|/sys|/root")) | {Name: .Name, Mounts: .Mounts}'

# Privileged containers
docker ps --format '{{.Names}}' | xargs -I {} docker inspect {} --format '{{.Name}}: Privileged={{.HostConfig.Privileged}}' | grep 'true'
```

### 4.3 FastAPI Application Logs
```bash
# Extract security-relevant lines from uvicorn logs
grep -E '401|403|429|SQL|script|union|select|\.\.\/|etc\/passwd' /var/log/econojin/app.log | tail -500

# API endpoint abuse
grep -oP '(?<=")[A-Z]+ /api/[^ ]+' /var/log/econojin/access.log \
  | sort | uniq -c | sort -rn | head -20

# Unusual User-Agents (non-browser, non-mobile)
grep -vE '(Mozilla|Chrome|Safari|Firefox|Edge|curl|Python|okhttp)' /var/log/econojin/access.log \
  | awk '{print $NF}' | sort | uniq -c | sort -rn | head -20
```

---

## 5. Automated Response Playbooks

### 5.1 Playbook: SQL Injection Attack Detected

```yaml
name: sql_injection_response
severity: P1
trigger: SQLI_BLOCK_PATTERNS match in request or SQL error in response

steps:
  1_block_ip:
    action: add_iptables_rule
    target: "{source_ip}"
    duration: 3600  # 1 hour block
    
  2_log_evidence:
    action: write_security_log
    data:
      type: sql_injection
      source_ip: "{source_ip}"
      payload: "{sanitized_payload}"
      endpoint: "{endpoint}"
      timestamp: "{timestamp}"
      raw_request_id: "{request_id}"
      
  3_notify:
    action: alert_main_agent
    severity: P1
    summary: "SQLi attempt from {source_ip} on {endpoint}"
    details: "{full_log_entry}"
    
  4_investigate:
    action: check_database_integrity
    queries:
      - "SELECT count(*) FROM users WHERE created_at > NOW() - INTERVAL '1 hour'"
      - "SELECT datname, numbackends FROM pg_stat_database"
    check_for: "Unexpected data changes, new users, schema modifications"
    
  5_assess:
    condition: "data_was_returned AND not parameterized"
    action: escalate_P0
    reason: "Potential data exfiltration"
    
  6_harden:
    action: verify_parameterization
    target_endpoint: "{endpoint}"
    check: "All DB queries use SQLAlchemy ORM or parameterized .execute(sql, params)"

cooldown: 300  # Don't re-trigger for same IP within 5 min
```

### 5.2 Playbook: Brute Force Attack Detected

```yaml
name: brute_force_response
severity: P2 (escalates to P1 if account breached)
trigger: "login_failed > 10 per IP in 300s OR login_failed > 5 per account in 300s"

steps:
  1_rate_limit_ip:
    action: apply_rate_limit
    target_ip: "{source_ip}"
    new_limit: 1  # 1 request per 5 seconds
    duration: 900
    
  2_lock_account:
    condition: "failures_per_account > 5"
    action: lock_account
    target_account: "{user_id}"
    duration: 1800
    notify_user: true
    
  3_captcha_enable:
    condition: "global_failure_rate > 50/min"
    action: enable_captcha
    target: "/api/auth/login"
    
  4_log_forensic:
    action: collect_forensic_data
    include:
      - usernames_attempted
      - passwords_hash_prefixes  # Store only first 4 chars of hash for pattern analysis
      - user_agents
      - timing_patterns
      
  5_threat_intel:
    action: check_ip_reputation
    source_ip: "{source_ip}"
    services: ["AbuseIPDB", "IPQualityScore"]
    
  6_escalate_on_breach:
    condition: "any successful login in attack window"
    action: force_password_reset
    target: breached_accounts
    severity: P0
    additional: "Rotate session tokens for all active sessions"
```

### 5.3 Playbook: JWT Anomaly Detected

```yaml
name: jwt_anomaly_response
severity: P1
trigger: "Same token used from multiple IPs OR token used after invalidated"

steps:
  1_invalidate_token:
    action: add_to_denylist
    token_jti: "{jti}"
    expiry: "token.exp"
    
  2_invalidate_family:
    action: revoke_token_family
    user_id: "{user_id}"
    reason: "Token reuse anomaly"
    
  3_force_logout:
    action: delete_all_sessions
    user_id: "{user_id}"
    
  4_notify_user:
    action: send_security_alert
    channel: "email"
    message: "Suspicious activity detected on your account. All sessions terminated. Please reset your password."
    
  5_investigate_source:
    action: trace_ip_context
    source_ip: "{anomalous_ip}"
    check:
      - geolocation mismatch
      - VPN/datacenter IP
      - known malicious IP
      
  6_rotate_secrets:
    condition: "token_forgery_suspected"
    action: rotate_jwt_signing_key
    warn: "All existing tokens become invalid"
```

### 5.4 Playbook: DDoS Attack Detected

```yaml
name: ddos_response
severity: P0
trigger: "request_rate > 200/s per endpoint OR > 50/s per IP sustained > 30s"

steps:
  1_enable_emergency_ratelimit:
    action: set_global_ratelimit
    rate: 30  # requests/second global
    burst: 50
    
  2_block_top_offenders:
    action: block_top_n_ips
    n: 20
    duration: 3600
    
  3_enable_caching:
    action: enable_aggressive_caching
    cache_ttl: 60  # 1-minute cache on public endpoints
    
  4_scale_defense:
    action: notify_infra
    request: "Scale up WAF instances"
    
  5_cloudflare_mode:
    condition: "attack_continues > 5 min"
    action: enable_under_attack_mode
    service: "CDN/Cloudflare"
    
  6_post_mortem:
    action: collect_attack_profile
    save:
      - attack_vectors
      - targeted_endpoints
      - source_ip_ranges
      - traffic_patterns
      - mitigation_effectiveness
```

### 5.5 Playbook: Penetration Test Execution

```yaml
name: authorized_pentest
severity: N/A (controlled)
trigger: explicit_request
pre_conditions:
  - written_authorization_confirmed
  - scope_document_reviewed
  - testing_window_defined
  - rollback_plan_ready

phases:
  reconnaissance:
    - nmap_scan: "nmap -sV -sC -p- {target}"
    - directory_enum: "dirb {target_url} /usr/share/wordlists/dirb/common.txt"
    - technology_detect: "whatweb {target_url}"
    - api_discovery: "Check /docs, /redoc, /openapi.json for exposure"
    
  vulnerability_scan:
    - owasp_zap_baseline: "zap-baseline.py -t {target_url} -r zap_report.html"
    - sqlmap_scan: "sqlmap -u {target_url}/api/... --batch --level=2 --risk=2"
    - nikto_scan: "nikto -h {target_url} -o nikto_report.txt"
    - nuclei_scan: "nuclei -u {target_url} -t ~/nuclei-templates/ -o nuclei_report.txt"
    
  manual_testing:
    - injection_points: "All user input fields, headers, cookies, URL params"
    - auth_testing: "JWT manipulation, session fixation, password reset flow"
    - business_logic: "Seat allocation bypass, usage meter tampering, payment flow skip"
    - api_security: "Mass assignment, IDOR, missing rate limits, verbose errors"
    - file_upload: "Extension bypass, content-type spoofing, path traversal in uploads"
    
  docker_specific:
    - container_escape: "Check for privileged mode, host PID namespace, Docker socket mount"
    - image_vulnerability: "trivy image {image_name}"
    - secrets_in_layers: "docker history --no-trunc {image} | grep -i 'pass\|secret\|key\|token'"
    - dockerfile_review: "Check for USER root, ADD instead of COPY, exposed debug ports"
    
  reporting:
    - findings_by_severity
    - proof_of_concept_for_critical
    - remediation_steps
    - retest_schedule
```

---

## 6. Alert Thresholds & Configuration

### 6.1 Threshold Definitions

```python
SECURITY_THRESHOLDS = {
    "auth": {
        "failed_login_rate": {"warning": 10, "critical": 30, "window_seconds": 300},
        "password_reset_rate": {"warning": 5, "critical": 20, "window_seconds": 3600},
        "new_account_rate": {"warning": 20, "critical": 50, "window_seconds": 3600},
        "token_refresh_rate": {"warning": 30, "critical": 100, "window_seconds": 300},
        "mfa_bypass_attempts": {"critical": 1, "window_seconds": 86400},
    },
    "api": {
        "4xx_error_rate": {"warning": 0.05, "critical": 0.15},  # Fraction of total requests
        "5xx_error_rate": {"warning": 0.01, "critical": 0.05},
        "response_time_p99": {"warning": 2000, "critical": 5000},  # ms
        "rate_limit_hits_rate": {"warning": 10, "critical": 100, "window_seconds": 60},
    },
    "infrastructure": {
        "cpu_usage": {"warning": 80, "critical": 95},
        "memory_usage": {"warning": 80, "critical": 95},
        "disk_usage": {"warning": 80, "critical": 90},
        "db_connections": {"warning": 80, "critical": 90},  # % of max
        "container_restarts": {"warning": 3, "critical": 10, "window_seconds": 600},
    },
    "data": {
        "row_count_deviation": {"warning": 0.10, "critical": 0.30},  # Unexpected change
        "table_size_growth": {"warning": 2.0, "critical": 5.0},  # Factor in 1 hour
        "export_requests": {"critical": 1, "window_seconds": 3600},  # Data export attempts
    },
}
```

### 6.2 Alert Routing

```python
ALERT_ROUTING = {
    "P0": {
        "channels": ["immediate_notification", "email", "webhook_to_oncall"],
        "ack_timeout": 300,  # 5 min before auto-escalation
    },
    "P1": {
        "channels": ["notification", "email"],
        "ack_timeout": 1800,
    },
    "P2": {
        "channels": ["notification"],
        "ack_timeout": 14400,
    },
    "P3": {
        "channels": ["daily_summary"],
    },
    "P4": {
        "channels": ["log_only"],
    },
}
```

---

## 7. Security Hardening Checklist

### 7.1 FastAPI Hardening

```
[ ] All endpoints decorated with dependency-based auth (no forgotten public endpoints)
[ ] Input validation via Pydantic models with strict types (no `Any`, no `Optional` where mandatory)
[ ] Response models exclude sensitive fields explicitly (no leak via `response_model`)
[ ] `max_length` set on all string fields
[ ] Custom validators for business logic constraints (seat count, usage limits)
[ ] Rate limiting via slowapi or custom middleware — at minimum on /api/auth/*
[ ] CORS: explicit origins list, not wildcard `*`; credentials only if needed
[ ] Security headers middleware:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 0 (deprecated, rely on CSP)
    - Content-Security-Policy: strict
    - Strict-Transport-Security: max-age=31536000; includeSubDomains
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy: minimal
[ ] Request body size limit (e.g., 10MB default, lower for text endpoints)
[ ] Timeout middleware: 30s default, lower for simple endpoints
[ ] Trusted host middleware: only accept known hostnames
[ ] Server header removed or spoofed (hide FastAPI/Uvicorn version)
[ ] OpenAPI docs (/docs, /redoc) disabled in production or behind auth
[ ] Health check endpoint minimal — no DB status leak
```

### 7.2 React Frontend Hardening

```
[ ] CSP headers set (see nginx/Docker config)
[ ] No secrets in .env (use build-time injection or runtime config served from backend)
[ ] All API calls use credential-based auth, never URL-embedded tokens
[ ] XSS prevention:
    - All user content rendered via React (no dangerouslySetInnerHTML without DOMPurify)
    - URL params sanitized before use
    - JSON.parse wrapped in try/catch
[ ] CSRF: Include X-CSRF-Token header on all state-changing requests
[ ] Iframe embedding prevented (X-Frame-Options / frame-ancestors)
[ ] Dependency audit: npm audit / yarn audit — zero HIGH/CRITICAL
[ ] Source maps disabled in production build
[ ] Bundle analyzer: check for accidental inclusion of dev tools, test data
[ ] localStorage: never store sensitive tokens (use httpOnly cookies)
[ ] SessionStorage: cleared on tab close; review persisted state
[ ] Input components: maxLength, pattern validation
```

### 7.3 Docker Hardening

```
[ ] Images:
    - Base image from trusted source (official images, pinned SHA256 digest)
    - No latest tag — pinned to specific version
    - Multi-stage builds: final image has no build tools
    - COPY preferred over ADD
    - HEALTHCHECK defined
    - No secrets in ENV (use secrets manager / Docker secrets / build args with care)
[ ] Runtime:
    - USER set (non-root, e.g., USER 1000)
    - read-only root filesystem where possible
    - No privileged mode
    - Capabilities dropped: --cap-drop=ALL --cap-add=NET_BIND_SERVICE
    - No Docker socket mounted
    - Resource limits set (--memory, --cpus)
    - No host network mode unless required
    - seccomp / AppArmor profile applied
[ ] Network:
    - Internal networks for inter-service communication
    - Only necessary ports published
    - Published ports bound to 127.0.0.1 if behind reverse proxy
[ ] Secrets:
    - Database passwords via Docker secrets or mounted from vault
    - JWT signing key from secret, not env var
    - API keys in separate secret file
```

### 7.4 PostgreSQL Hardening

```
[ ] Authentication:
    - pg_hba.conf: scram-sha-256 for all connections, no trust entries
    - Application user has minimal privileges (no SUPERUSER, no CREATEDB)
    - Separate read-only user for reporting/analytics queries
[ ] Encryption:
    - SSL/TLS enforced for all connections
    - Data-at-rest encryption (file system or pg_tde extension)
[ ] Auditing:
    - pgAudit extension enabled for DDL and auth events
    - log_statement = 'ddl' or 'mod' (not 'all' in production — performance)
    - log_connections = on
    - log_disconnections = on
[ ] Network:
    - listen_addresses set to specific interfaces, not '*'
    - Firewall: only app server IPs whitelisted to DB port
[ ] Hardening:
    - statement_timeout set (e.g., 30s)
    - idle_in_transaction_session_timeout set (e.g., 60s)
    - connection limit tuned, not unlimited
    - Extension allowlist (no untrusted languages: plpythonu, plperlu)
    - RLS (Row-Level Security) enabled on multi-tenant tables
[ ] Backup:
    - Encrypted backups (pg_dump | gpg or pgBackRest with encryption)
    - Backup retention policy: 7 daily, 4 weekly, 3 monthly
    - Restore tested quarterly
```

### 7.5 SQLite Hardening (if used)

```
[ ] WAL mode enabled (better concurrency + crash safety)
[ ] Foreign keys enforced: PRAGMA foreign_keys = ON
[ ] Database file permissions: 600 (owner read/write only)
[ ] Database outside web root (not in static/ or public/)
[ ] Backup via .backup or VACUUM INTO, not file copy of live DB
[ ] No direct user input in raw SQL — always parameterized
[ ] Consider migration to PostgreSQL for production
```

---

## 8. Rate Limiting Optimization

### 8.1 Tiered Rate Limit Architecture

```python
RATE_LIMIT_TIERS = {
    "strict": {   # Auth endpoints
        "rate": "5/minute",
        "burst": 10,
        "endpoints": ["/api/auth/login", "/api/auth/register", "/api/auth/refresh",
                      "/api/auth/password-reset", "/api/auth/verify-email"],
    },
    "standard": {  # Authenticated user endpoints
        "rate": "60/minute",
        "burst": 120,
        "endpoints": ["/api/users/*", "/api/seats/*", "/api/usage/*"],
    },
    "generous": {  # Read-only public endpoints
        "rate": "120/minute",
        "burst": 300,
        "endpoints": ["/api/status", "/api/version", "/api/public/*"],
    },
    "static": {    # Static assets via API
        "rate": "300/minute",
        "burst": 600,
        "endpoints": ["/static/*"],
    },
}

# Per-IP bucket using Redis (or in-memory with sync for multi-instance)
# Key format: ratelimit:{tier}:{ip}:{window}
# Track: remaining tokens, reset time, retry-after
```

### 8.2 Dynamic Rate Limiting

```python
# Adjust limits based on real-time threat level
THREAT_LEVEL_ADJUSTMENTS = {
    "green":  {"multiplier": 1.0},    # Normal
    "yellow": {"multiplier": 0.5},    # Elevated threat — halve all limits
    "orange": {"multiplier": 0.25},   # Under attack — quarter limits
    "red":    {"multiplier": 0.1},    # Active breach — severe throttling
    
    "auto_escalation": {
        "check_interval": 60,  # seconds
        "yellow_trigger": "blocked_requests > 50 in 1 min OR auth_failures > 20/min",
        "orange_trigger": "DDoS pattern detected OR confirmed SQLi attempting exfil",
        "red_trigger": "data_breach_confirmed OR RCE_attempted",
    }
}
```

---

## 9. JWT Security Monitoring

### 9.1 Token Lifecycle Audit

```python
JWT_MONITORING_CHECKS = {
    "refresh_token_rotation": {
        "check": "Every refresh invalidates previous refresh token",
        "alert_if": "Same refresh token used more than once",
        "action": "Revoke entire token family, force re-login",
    },
    "access_token_reuse": {
        "check": "Access tokens used only once (or with strict short window)",
        "alert_if": "Same access token from different IP within TTL",
        "action": "Investigate for token theft",
    },
    "token_volume_per_user": {
        "check": "Users not generating excessive tokens",
        "alert_if": "> 50 tokens/hour for single user",
        "action": "Check for misbehaving client or token leak",
    },
    "expiry_distribution": {
        "check": "Token expiry timestamps are normally distributed",
        "alert_if": "Clustered expiries (bulk token generation)",
        "action": "Investigate potential batch token theft",
    },
}
```

### 9.2 Key Rotation Schedule

```python
JWT_KEY_ROTATION = {
    "access_token_key": {
        "rotation_interval_days": 30,
        "overlap_period_hours": 1,  # Accept tokens signed with old key for 1h
        "key_strength": "RS256 >= 2048-bit OR HS256 >= 256-bit",
    },
    "refresh_token_key": {
        "rotation_interval_days": 30,
        "overlap_period_days": 7,  # Refresh tokens live longer, longer overlap
        "key_strength": "RS256 >= 2048-bit",
    },
    "emergency_rotation": {
        "trigger": "Key compromise suspected or confirmed breach",
        "overlap": 0,  # Immediate, all existing tokens invalid
        "notify": "All users: session terminated, please re-login",
    },
}
```

---

## 10. Recovery Procedures

### 10.1 Data Breach Response

```yaml
name: data_breach_containment
severity: P0

phase_1_contain:  # First 15 minutes
  - revoke_all_active_sessions
  - rotate_all_secrets (JWT keys, DB passwords, API keys)
  - block_attacker_ips_across_all_services
  - enable_maintenance_mode if_data_still_flowing_out
  - snapshot_forensic_evidence (logs, memory dumps, DB state)
  
phase_2_assess:  # First 1 hour
  - determine_breach_vector
  - identify_affected_data (users, tables, fields)
  - check_for_backdoors (new users, cron jobs, modified files)
  - review_git_diff for unauthorized code changes
  - docker_image_scan on all running containers
  
phase_3_notify:  # First 24 hours
  - prepare_incident_report
  - notify_affected_users (email)
  - notify_authorities if PII breach (within regulatory window)
  - internal_post_mortem_scheduled
  
phase_4_remediate:  # First 72 hours
  - patch_vulnerability
  - restore_from_clean_backup if needed
  - redeploy_with_hardened_config
  - penetration_test_patched_system
  - verify_no_data_exposure_on_pastebin/darkweb
  
phase_5_harden:  # Ongoing
  - update_incident_response_playbook
  - add_detection_for_this_attack_vector
  - conduct_team_tabletop_exercise
  - audit_similar_systems
```

### 10.2 Service Restoration After DDoS

```yaml
name: ddos_recovery
severity: P0

steps:
  - verify_attack_subsided (traffic normalized > 5 min)
  - restore_rate_limits_to_normal gradually (not all at once)
  - unblock_false_positives (legitimate IPs caught in broad block)
  - verify_data_integrity (no corrupted writes during attack)
  - restart_rate_limited_services
  - notify_users_of_degradation_window
  - update_threat_intel (attacker IPs, patterns to blocklists)
```

### 10.3 Backup Restoration

```yaml
name: backup_restore
trigger: "Data corruption, ransomware, or breach requiring clean state"

pre_checks:
  - verify_backup_integrity (checksum match)
  - verify_backup_not_compromised (created before breach timestamp)
  - identify_last_known_good_point

procedure:
  1_stop_services: docker-compose stop app worker
  2_backup_current: pg_dump current_db > forensic_snapshot.sql
  3_restore_db: pg_restore --clean --if-exists -d econojin backup.dump
  4_verify_schema: Run migration check — no missing migrations
  5_verify_data: Row counts for critical tables match expected
  6_restart: docker-compose up -d
  7_smoke_test: Health check, auth flow, critical business flow
  8_monitor: Watch for 1 hour for anomalies
```

---

## 11. Security Metrics Dashboard

### 11.1 Key Metrics to Track

```python
SECURITY_KPIS = {
    "detection": {
        "mttd": "Mean Time To Detect (target: < 5 min for P0/P1)",
        "false_positive_rate": "Blocked requests that were legitimate",
        "false_negative_rate": "Attacks missed (discovered via other means)",
        "detection_coverage": "% of OWASP Top 10 covered by detection rules",
    },
    "response": {
        "mttr": "Mean Time To Respond (target: < 15 min for P0)",
        "mttc": "Mean Time To Contain (target: < 30 min for breach)",
        "auto_remediation_rate": "% of incidents handled without manual intervention",
    },
    "prevention": {
        "blocked_attacks": "By type (SQLi, XSS, brute force, etc.)",
        "rate_limit_triggers": "By endpoint",
        "patches_applied_24h": "Critical patches applied within 24h of release",
        "vulnerability_window": "Days between CVE publish and patch",
    },
    "posture": {
        "open_critical_vulnerabilities": "Must be zero",
        "security_header_score": "Mozilla Observatory grade (target: A+)",
        "ssl_labs_score": "Target: A+",
        "dependency_health": "npm audit + pip-audit: zero HIGH/CRITICAL",
    },
}
```

### 11.2 Weekly Security Report Template

```
# Econojin Weekly Security Report
## Period: {start_date} to {end_date}

### Attack Summary
- Total requests: {total}
- Blocked attacks: {blocked} ({block_rate}%)
- Breakdown: SQLi={sqli}, XSS={xss}, Brute Force={brute}, CSRF={csrf}, Other={other}
- New IPs blacklisted: {new_ips}

### Incidents
- P0: {p0_count} | P1: {p1_count} | P2: {p2_count}
- MTTR this week: {mttr} (target: <15min)
- Unresolved: {unresolved}

### Auth Health
- Failed logins: {failed} (rate: {rate}/min)
- Accounts locked: {locked}
- Password resets: {resets}
- Token anomalies: {token_anomalies}

### Infrastructure
- Container restarts: {restarts}
- CPU peak: {cpu_peak}%
- Memory peak: {mem_peak}%
- DB connection peak: {db_conns}
- Disk usage: {disk}%

### Vulnerabilities
- New CVEs affecting our stack: {cve_count}
- Patched this week: {patched}
- Outstanding: {outstanding}
- Dependency audit: pip={pip_critical} critical, npm={npm_critical} critical

### Recommendations
1. {rec1}
2. {rec2}
3. {rec3}
```

---

## 12. Spider Security System Enhancement

### 12.1 Web Crawler Defense

```python
SPIDER_DEFENSE = {
    "robots_txt": {
        "disallow_all_sensitive": True,
        "check": "robots.txt exists, Disallow for /api, /admin, /internal",
    },
    "honeypots": {
        "hidden_links": ["/admin", "/wp-admin", "/.env", "/config.php"],
        "action_on_access": "block_ip_for_24h",
        "log_headers": ["User-Agent", "X-Forwarded-For", "Via"],
    },
    "user_agent_filtering": {
        "block_patterns": [
            "scanner", "crawler", "spider", "bot", "zgrab", "masscan",
            "nmap", "sqlmap", "nikto", "nessus", "burp", "zap",
            "gobuster", "dirb", "wfuzz", "ffuf", "feroxbuster",
        ],
        "allow_list": [  # Legitimate bots to allow
            "Googlebot", "Bingbot", "DuckDuckBot",
        ],
        "unknown_empty": "block",  # Empty User-Agent → block
    },
    "rate_based": {
        "request_rate_per_ip": 10,  # 10 req/s from same IP → throttle
        "unique_urls_per_ip_per_minute": 100,  # Scanner behavior
        "404_rate": 0.3,  # If >30% of requests are 404 → likely scanner
    },
    "header_checks": {
        "require_accept_header": True,
        "require_accept_language": True,
        "validate_referrer": "same-origin for POST/DELETE",
    },
}
```

### 12.2 Spider Trap Implementation

```python
# FastAPI middleware: Spider Trap
# Add hidden links that real users never see (display: none in HTML)
# Any IP that hits these gets auto-banned

SPIDER_TRAP_PATHS = [
    "/admin/config.php",
    "/wp-login.php",
    "/.env",
    "/.git/config",
    "/phpmyadmin/",
    "/node_modules/",
    "/actuator/health",  # Spring Boot actuator probe
    "/.DS_Store",
    "/backup.sql",
    "/dump.sql",
]

@app.middleware("http")
async def spider_trap_middleware(request: Request, call_next):
    if request.url.path in SPIDER_TRAP_PATHS:
        ip = request.client.host
        await block_ip(ip, duration=86400, reason=f"Spider trap: {request.url.path}")
        log_security_event("spider_trap_triggered", ip=ip, path=request.url.path)
        return JSONResponse(
            status_code=403,
            content={"detail": "Forbidden"}
        )
    return await call_next(request)
```

---

## 13. Integration Points

### 13.1 Where Security Agent Hooks Into Econojin

```
FastAPI Middleware Stack:
  ┌─────────────────────────────────┐
  │ 1. SecurityHeadersMiddleware    │ ← Add headers to all responses
  │ 2. SpiderTrapMiddleware         │ ← Check for scanner probes
  │ 3. RateLimitMiddleware          │ ← Apply tiered rate limits
  │ 4. WAFMiddleware                │ ← Pattern-match attack payloads
  │ 5. AuditLogMiddleware           │ ← Log all security events
  │ 6. CORSMiddleware               │ ← Validate origins
  │ 7. AuthMiddleware               │ ← JWT validation and user context
  │ 8. App Router                   │ ← Business logic
  └─────────────────────────────────┘

Database Layer:
  - pgAudit extension for DDL logging
  - Connection proxy that validates parameterization
  - Query timeout guard (statement_timeout)
  - RLS policies on multi-tenant tables

Docker Layer:
  - Read-only rootfs for app containers
  - Non-root user (USER 1000)
  - Capability dropping
  - Resource limits
  - Health checks that verify security middleware loaded

CI/CD Pipeline:
  - SAST: bandit (Python), eslint-plugin-security (JS)
  - Dependency scan: pip-audit, npm audit
  - Container scan: trivy
  - Secret scan: detect-secrets, git-secrets, truffleHog
  - DAST: OWASP ZAP baseline scan on staging
```

### 13.2 Security Event Schema

```python
# Standard security event logged by all modules
SECURITY_EVENT = {
    "id": "uuid",
    "timestamp": "ISO-8601",
    "event_type": "sql_injection|brute_force|xss|csrf|ddos|jwt_anomaly|rate_limit|spider|config_drift",
    "severity": "P0|P1|P2|P3|P4",
    "source": {"ip": str, "user_id": str|None, "user_agent": str},
    "target": {"endpoint": str, "method": str, "resource_id": str|None},
    "details": {
        "rule_triggered": str,
        "payload_hash": str,  # SHA256 of malicious payload (not raw for privacy)
        "payload_preview": str,  # First 100 chars for triage
        "action_taken": "block|flag|throttle|log",
    },
    "correlation_id": str,  # Links multiple events in same attack chain
}
```

---

## 14. Agent Commands

### 14.1 User-Facing Commands

| Command | Action |
|---------|--------|
| `security status` | Run health check, report current threat level, open incidents |
| `security scan [endpoint]` | Run targeted vulnerability scan |
| `security pentest [scope]` | Execute authorized penetration test (requires confirmation) |
| `security block <ip>` | Manually block an IP with specified duration |
| `security unblock <ip>` | Remove an IP from blocklist |
| `security report [daily/weekly]` | Generate security report |
| `security audit [component]` | Full security audit of component (db, api, frontend, docker) |
| `security lock <user_id>` | Force lock a user account |
| `security rotate-keys` | Rotate JWT signing keys (requires confirmation) |
| `security threat-level [green/yellow/orange/red]` | Manually set threat level |

### 14.2 Autonomous Actions (No user approval needed)

- Log scanning and pattern matching
- IP reputation checks (no external call-out without approval)
- Rate limit adjustments within configured bounds
- Adding IPs to temporary blocklist (configurable max duration)
- Generating reports to workspace
- Flagging suspicious patterns for review
- Non-destructive vulnerability scanning

### 14.3 Actions Requiring User Approval

- Rotating JWT keys or database credentials
- Forcing password resets on user accounts
- Blocking IPs permanently (> 24 hours)
- Enabling full "under attack" mode
- Running active penetration tests
- Modifying firewall rules
- Deploying patches to production

---

## 15. Agent Configuration

```yaml
# security_agent_config.yaml
agent:
  name: econojin-security-defender
  version: 1.0.0
  mode: watchdog  # watchdog | audit | pentest
  threat_level: auto  # auto | green | yellow | orange | red

monitoring:
  log_paths:
    app: /var/log/econojin/app.log
    access: /var/log/econojin/access.log
    db: /var/log/postgresql/postgresql.log
    docker: docker events
  check_interval_seconds: 300  # 5 min between watchdog runs
  log_retention_days: 90

blocking:
  auto_block_enabled: true
  max_auto_block_duration_hours: 24
  blocklist_backend: redis  # redis | postgresql | file
  false_positive_review_queue: true

alerting:
  enabled: true
  min_severity: P2  # Don't alert for P3/P4
  cooldown_seconds: 300  # Don't re-alert same rule for 5 min
  aggregation_window_seconds: 60  # Batch alerts in 1-min windows

compliance:
  frameworks: [OWASP_ASVS_4.0, CIS_Docker_Benchmark]
  audit_interval_days: 30
  evidence_path: /var/log/econojin/security/audit/
```

---

## 16. Quick Reference: OWASP Top 10 Coverage

| OWASP Risk | Detection Method | Prevention |
|------------|-----------------|------------|
| A01: Broken Access Control | Auth decorator audit, IDOR probe | RBAC, ownership checks, deny-by-default |
| A02: Cryptographic Failures | SSL/TLS scan, JWT algorithm check | Enforce TLS 1.3, AES-256, strong JWT alg |
| A03: Injection | SQLi/XSS pattern matching, WAF | Parameterized queries, ORM, input validation |
| A04: Insecure Design | Architecture review, threat model | Security design review before implementation |
| A05: Security Misconfiguration | Header audit, config drift detection | Hardened defaults, config-as-code |
| A06: Vulnerable Components | Dependency scanning (trivy, pip-audit, npm audit) | Auto-update, SBOM, pinned versions |
| A07: Auth Failures | Brute force detection, credential stuffing | Rate limiting, MFA, strong password policy |
| A08: Software & Data Integrity | CI/CD pipeline scan, image signing | Signed commits, SBOM, image digest pinning |
| A09: Logging & Monitoring Failures | This agent (meta-coverage) | Structured logging, centralized collection |
| A10: SSRF | URL parameter analysis, internal IP check | URL allowlist, DNS rebinding protection |
| API1: Broken Object Level Auth | IDOR testing on /api/users/{id} | Ownership validation per request |
| API2: Broken Authentication | JWT monitoring | Strong token validation, rotation |
| API3: Excessive Data Exposure | Response model audit | Explicit response schemas |
| API4: Lack of Resources & Rate Limits | Traffic pattern analysis | Tiered rate limiting |
| API5: Broken Function Level Auth | Endpoint permission audit | Decorator-based permission checks |

---

**End of SKILL.md — Security Defense Agent for Econojin Platform**
