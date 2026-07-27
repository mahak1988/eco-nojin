# Phase 1 progress

## Stage 1 — HttpOnly cookies — DONE

PowerShell-safe test (use a file for JSON body):

```powershell
@'
{"email":"farmer1@example.com","password":"Secret123!","full_name":"Test Farmer"}
'@ | Set-Content -Encoding utf8 body.json

curl.exe -c cookies.txt -b cookies.txt -X POST `
  -H "Content-Type: application/json" -H "User-Agent: Mozilla/5.0" `
  --data-binary "@body.json" `
  http://localhost:8000/api/v1/auth/register

# if already registered:
@'
{"email":"farmer1@example.com","password":"Secret123!"}
'@ | Set-Content -Encoding utf8 login.json
curl.exe -c cookies.txt -b cookies.txt -X POST `
  -H "Content-Type: application/json" -H "User-Agent: Mozilla/5.0" `
  --data-binary "@login.json" `
  http://localhost:8000/api/v1/auth/login

curl.exe -b cookies.txt -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/auth/me
```

## Stage 2 — require_permission on writes — DONE

- Education POST/PATCH/DELETE → `education:write`
- Accounting POST/PATCH → `accounting:write`
- Local soft-gate: if `ENVIRONMENT=local` and `REQUIRE_AUTH_FOR_WRITES=false`, permission check is skipped (same as before for local DX)
- Staging/prod: set `REQUIRE_AUTH_FOR_WRITES=true` to enforce RBAC

## Stage 3 — FE Education (next)
## Stage 4 — Accounting seed + contract tests
