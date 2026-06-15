#!/bin/bash
BACKUP_DIR="/backups/redis"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

redis-cli BGSAVE
sleep 5
cp /data/dump.rdb ${BACKUP_DIR}/redis_dump_${DATE}.rdb
find ${BACKUP_DIR} -name "redis_dump_*.rdb" -mtime +${RETENTION_DAYS} -delete
echo "Backup completed: redis_dump_${DATE}.rdb"
