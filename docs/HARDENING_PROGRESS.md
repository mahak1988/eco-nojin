# Hardening + GEE + realtime — progress

| Track | Item | Status |
|-------|------|--------|
| Docker | postgres+postgis, redis, api, worker, beat | ✅ compose |
| Security | RS256 key paths + gen script | ✅ |
| Security | refresh jti revoke/rotate | ✅ |
| Security | native bcrypt in security.py | ✅ |
| Monitoring | WS broadcast on rule fire | ✅ |
| Beat | weekly vegetation task registered | ✅ |
| GEE | provider + setup doc | ✅ (needs your GCP keys) |
| Alembic full revision on PG | run `alembic revision --autogenerate` against compose PG | ⚠️ operator step |
| RBAC on every write | partial | ⚠️ next |
