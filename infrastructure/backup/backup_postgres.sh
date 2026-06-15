#!/bin/bash
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

pg_dump -U econojin -h db econojin_prod | gzip > ${BACKUP_DIR}/econojin_db_${DATE}.sql.gz
find ${BACKUP_DIR} -name "econojin_db_*.sql.gz" -mtime +${RETENTION_DAYS} -delete
echo "Backup completed: econojin_db_${DATE}.sql.gz"
