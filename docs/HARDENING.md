# Hardening guide

## 1. Docker stack

```bash
# optional RS256 keys
bash scripts/gen_jwt_keys.sh

docker compose up --build -d
# api :8000  postgres :5432  redis :6379  worker + beat
```

`.env.docker` sets Postgres + Redis. For RS256:

```
ALGORITHM=RS256
JWT_PRIVATE_KEY_PATH=/secrets/jwt_private.pem
JWT_PUBLIC_KEY_PATH=/secrets/jwt_public.pem
```

Mount `./secrets` is already in compose.

## 2. Auth (R4/R5)

- Access + refresh in **HttpOnly** cookies
- Refresh **rotation**: old `jti` revoked on `/auth/refresh` and `/auth/logout`
- Revocation store: Redis if up, else in-process dict

## 3. Real-time alerts

1. Open `ws://localhost:8000/ws/monitoring`
2. `POST /api/v1/sensors/{id}/readings?value=10` (below rule threshold)
3. Client receives `{ "type": "alert", ... }`

## 4. Celery Beat

`beat` service runs `satellite.weekly_vegetation_check` (schedule in `celery_app.py`).

## 5. GEE live

See [GEE_SETUP.md](./GEE_SETUP.md).
