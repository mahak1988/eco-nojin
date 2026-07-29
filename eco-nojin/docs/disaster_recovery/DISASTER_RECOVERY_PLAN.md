# Disaster Recovery Plan - Econojin Platform

**Version:** 1.0
**Last Updated:** 2026-06-15

## Recovery Time Objectives (RTO)

| Component | RTO | RPO |
|-----------|-----|-----|
| API Service | 15 minutes | 5 minutes |
| Database | 30 minutes | 1 hour |
| Cache (Redis) | 10 minutes | 6 hours |
| Full System | 2 hours | 1 hour |

## Recovery Procedures

### Database Recovery
```bash
docker-compose stop api celery-worker
gunzip -c /backups/postgres/econojin_db_YYYYMMDD_HHMMSS.sql.gz | psql -U econojin -h db econojin_prod
docker-compose start api celery-worker
```

### Redis Recovery
```bash
docker-compose stop redis
cp /backups/redis/redis_dump_YYYYMMDD_HHMMSS.rdb /data/dump.rdb
docker-compose start redis
```