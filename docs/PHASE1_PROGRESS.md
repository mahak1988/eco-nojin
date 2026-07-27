# Phase 1 progress

## Stage 1 — HttpOnly cookies (DONE)

- `POST /api/v1/auth/login|register|refresh` set `access_token` + `refresh_token` HttpOnly cookies
- `POST /api/v1/auth/logout` clears cookies (no auth required)
- `GET /api/v1/auth/me` accepts Bearer **or** access cookie
- Refresh accepts body `refreshToken` **or** refresh cookie
- Body still returns tokens for mobile/API clients
- FE `apiFetch` uses `credentials: "include"`

### Manual test

```powershell
# Register
curl.exe -c cookies.txt -b cookies.txt -X POST -H "Content-Type: application/json" -H "User-Agent: Mozilla/5.0" ^
  -d "{\"email\":\"farmer1@example.com\",\"password\":\"Secret123!\",\"full_name\":\"Test Farmer\"}" ^
  http://localhost:8000/api/v1/auth/register

# Me via cookie only (no Authorization header)
curl.exe -b cookies.txt -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/auth/me

# Refresh via cookie
curl.exe -c cookies.txt -b cookies.txt -X POST -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/auth/refresh

# Logout
curl.exe -c cookies.txt -b cookies.txt -X POST -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/auth/logout
```

## Next stages
2. require_permission on education/accounting writes
3. FE Education real API + Loading/Error/Empty
4. Accounting seed + contract tests
