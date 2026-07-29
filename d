# admin_panel | Admin Panel for Econojin

> **Note:** This module is the **admin panel** for the Econojin platform.
> Includes system settings management, audit log viewing, system reports, and admin dashboard.
> All endpoints in this module are **superuser-only**.

## Responsibilities

This module has four main responsibilities:

1. **Admin Dashboard** (`GET /admin/`)
   - Display system status summary (user count, settings, logs, reports)

2. **System Settings Management** (`GET /admin/settings`, `PUT /admin/settings/{key}`)
   - View and update system key-value settings
   - Set `value`, `description`, `is_active`

3. **Audit Log Viewing** (`GET /admin/audit-logs`)
   - View system events
   - Filter by event type

4. **System Report Viewing** (`GET /admin/reports`)
   - View system-generated reports

## Structure

```
admin_panel/
├── __init__.py                # Module init
├── router.py                  # ★ Admin panel router (all /admin prefixed)
├── schemas.py                 # Pydantic validation models
├── service.py                 # Business logic
├── repository.py              # ★ Specialized repositories
├── frontend/                  # ★ Admin panel frontend (Vite + React)
└── tests/                     # Pytest tests
    └── test_router.py         #   Router tests
```

## Specialized Repositories (`repository.py`)

| Repository | Model | Description |
|------------|-------|-------------|
| `AdminSettingRepository` | `AdminSetting` | Search settings by key (`get_by_key`) |
| `AuditLogRepository` | `AuditLog` | Filter logs by event type (`filter_by_event_type`) |
| `SystemReportRepository` | `SystemReport` | System report management (basic CRUD) |

## API Endpoints

> **Note:** All endpoints in this module require **superuser authentication**.

| Method | Path | Description | Requires |
|--------|------|-------------|----------|
| GET | `/admin/` | Admin dashboard | superuser |
| GET | `/admin/settings` | List system settings | superuser |
| PUT | `/admin/settings/{key}` | Update/create setting | superuser |
| GET | `/admin/audit-logs` | Audit logs | superuser |
| GET | `/admin/reports` | System reports | superuser |

### 1. Admin Dashboard

```json
// GET /admin/
// Response 200
{
    "total_users": 42,
    "total_settings": 15,
    "total_audit_logs": 1280,
    "total_reports": 7
}
```

### 2. System Settings

```json
// GET /admin/settings?limit=10&offset=0
// Response 200
[
    {
        "id": 1,
        "key": "site_name",
        "value": "Econojin",
        "description": "Site name",
        "is_active": true,
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-01-15T10:00:00Z"
    }
]
```

**Update Setting:**
```json
// PUT /admin/settings/site_name
{
    "value": "Econojin Platform",
    "description": "Official platform name",
    "is_active": true
}
// Response 200
{
    "id": 1,
    "key": "site_name",
    "value": "Econojin Platform",
    ...
}
```

### 3. Audit Logs

```json
// GET /admin/audit-logs?event_type=login&limit=10
// Response 200
[
    {
        "id": 100,
        "actor": "user@example.com",
        "event_type": "login",
        "description": "User login to system",
        "ip_address": "192.168.1.1",
        "created_at": "2025-01-15T10:30:00Z"
    }
]
```

### 4. System Reports

```json
// GET /admin/reports?limit=10&offset=0
// Response 200
[
    {
        "id": 1,
        "title": "Weekly Performance Report",
        "report_type": "performance",
        "status": "completed",
        "payload": {},
        "created_at": "2025-01-15T10:00:00Z"
    }
]
```

## Data Models

### AdminSetting
| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Unique identifier |
| `key` | str | Setting key (unique) |
| `value` | str | Setting value |
| `description` | str | Description |
| `is_active` | bool | Active status |
| `created_at` | datetime | Creation date |
| `updated_at` | datetime | Last update date |

### AuditLog
| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Unique identifier |
| `actor` | str | Event actor (user email) |
| `event_type` | str | Event type (login, logout, setting_change, ...) |
| `description` | str | Event description |
| `ip_address` | str | IP address |
| `created_at` | datetime | Event date |

### SystemReport
| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Unique identifier |
| `title` | str | Report title |
| `report_type` | str | Report type (performance, error, usage, ...) |
| `status` | str | Status (pending, running, completed, failed) |
| `payload` | dict | Report content |
| `created_at` | datetime | Creation date |

## Sample curl Requests

```bash
# Get superuser token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@econojin.com", "password": "*****"}' \
  | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# Dashboard
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/admin/

# Settings
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/admin/settings?limit=20"

# Update setting
curl -X PUT http://localhost:8000/admin/settings/site_name \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"value": "Econojin Platform", "description": "Official name", "is_active": true}'

# Logs
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/admin/audit-logs?event_type=login&limit=50"

# Reports
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/admin/reports?limit=10"
```

## Usage in Python Code

```python
import httpx

# Superuser authentication
response = httpx.post("http://localhost:8000/api/v1/auth/login",
    json={"email": "admin@econojin.com", "password": "*****"})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get dashboard
dashboard = httpx.get("http://localhost:8000/admin/", headers=headers).json()
print(f"Users: {dashboard['total_users']}")
print(f"Settings: {dashboard['total_settings']}")

# Update setting
httpx.put("http://localhost:8000/admin/settings/site_name",
    headers=headers,
    json={"value": "New Site Name"})
```

## Development & Testing

```bash
# From project root
cd d:\econojin.com

# Run tests
pytest apps/admin_panel/tests/ -v

# Run development server
python apps/main.py
# or
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000
```

## Related Environment Variables (`.env`)

```ini
# Default superuser account
FIRST_SUPERUSER=admin@econojin.com
FIRST_SUPERUSER_PASSWORD=changethis    # Change in production
```

## Changelog

- **Phase 2:** Created admin panel with 4 main sections (Dashboard, Settings, Logs, Reports)
- **Phase 2:** Implemented specialized repositories for AdminSetting, AuditLog, SystemReport
- **Phase 2:** Applied superuser access restriction to all endpoints
- **Phase 2:** Server-side validation for settings updates
