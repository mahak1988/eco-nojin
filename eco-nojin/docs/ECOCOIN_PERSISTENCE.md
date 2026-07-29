# EcoCoin persistence & oracle (Phase D)

## Local SQLite

On `ENVIRONMENT=local`, `init_db()` runs `Base.metadata.create_all` including `ecocoin_mint_events`.

Restart uvicorn after pull so the table is created.

## Alembic (staging / prod path)

```bash
pip install alembic
alembic upgrade head
```

Revision `20260729_0001` creates `ecocoin_mint_events`.

## Oracle

- Algorithm: HMAC-SHA256
- Secret: env `ECOCOIN_ORACLE_SECRET` (dev default is insecure — set in production)
- Endpoints return `oracle_signature` on successful impact-mint when DB session is available

## Credit types

| id | name | unit | Fc |
|----|------|------|-----|
| 0 | carbon | tCO2e | 25 |
| 1 | water | m3_saved | 0.05 |
| 2 | soil_soc | tC_per_ha | 40 |
| 3 | biodiversity | index | 2 |
