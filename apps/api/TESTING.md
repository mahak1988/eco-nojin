# EcoNojin API - Testing Guide

## Prerequisites

1. API must be running:
```bash
cd apps/api
uvicorn app.main:app --reload
```

## Quick Start

### 1. Create Admin User

```bash
cd apps/api
python run_seed.py
```

Expected output:
```
SUCCESS: Admin user created!
   ID: 1
   Email: admin@econojin.com
   Password: <YOUR_ADMIN_PASSWORD>
   Role: admin
```

### 2. Run Automated Tests

```bash
cd apps/api
python test_auth.py
```

## Manual Testing with curl

### Register

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "farmer@example.com",
    "password": "<YOUR_TEST_PASSWORD>",
    "full_name": "Test Farmer",
    "role": "farmer"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@econojin.com",
    "password": "<YOUR_ADMIN_PASSWORD>"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Get Current User

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### List Users (Admin Only)

```bash
curl http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### Update Profile

```bash
curl -X PATCH http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Tehran, Iran",
    "bio": "Updated bio"
  }'
```

## Swagger UI

1. Open: http://localhost:8000/docs
2. Click 'Authorize' button (top right)
3. Login via POST /auth/login and copy token
4. Enter: `Bearer YOUR_TOKEN`
5. Test endpoints

## Endpoints Summary

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/v1/auth/register | No | Register new user |
| POST | /api/v1/auth/login | No | Login and get token |
| GET | /api/v1/auth/me | Yes | Get current user |
| GET | /api/v1/users/ | Admin | List all users |
| GET | /api/v1/users/{id} | Yes | Get user by ID |
| PATCH | /api/v1/users/me | Yes | Update profile |

## Troubleshooting

### Error: Incorrect email or password
- Solution: Run `python run_seed.py` to create admin user

### Error: Could not validate credentials
- Solution: Token expired or invalid. Login again.

### Error: ModuleNotFoundError
- Solution: Run from `apps/api` directory

